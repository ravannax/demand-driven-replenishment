"""KPIs de demanda / ventas por SKU a partir de líneas de venta."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .commercial_month import adjust_to_commercial_month, commercial_month_start


def build_sku_kpis(
    sales: pd.DataFrame,
    analysis_date: str | pd.Timestamp,
    cutoff_day: int = 21,
    sku_col: str = "sku",
    date_col: str = "fecha",
    qty_col: str = "unidades",
    revenue_col: str = "ventas",
) -> pd.DataFrame:
    """Agrega indicadores por SKU en ventanas 28d / 6m / 12m.

    Los meses sin venta se rellenan con 0 antes de promediar (evita sesgo al alza).
    """
    analysis = pd.Timestamp(analysis_date)
    df = sales.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df["mes_comercial"] = adjust_to_commercial_month(df[date_col], cutoff_day)

    current_cm = commercial_month_start(analysis, cutoff_day)
    months_12 = pd.date_range(current_cm - pd.DateOffset(months=11), current_cm, freq="MS")
    months_6 = months_12[-6:]

    # Mensual por SKU
    monthly = (
        df.groupby([sku_col, "mes_comercial"], as_index=False)
        .agg(unidades=(qty_col, "sum"), ventas=(revenue_col, "sum"))
    )

    skus = sorted(df[sku_col].unique())
    grid = pd.MultiIndex.from_product([skus, months_12], names=[sku_col, "mes_comercial"])
    monthly = (
        monthly.set_index([sku_col, "mes_comercial"])
        .reindex(grid, fill_value=0)
        .reset_index()
    )

    def _agg_window(months: pd.DatetimeIndex, prefix: str) -> pd.DataFrame:
        sub = monthly[monthly["mes_comercial"].isin(months)]
        g = sub.groupby(sku_col).agg(
            **{
                f"unidades_promedio_{prefix}": ("unidades", "mean"),
                f"unidades_mediana_{prefix}": ("unidades", "median"),
                f"unidades_total_{prefix}": ("unidades", "sum"),
                f"ventas_{prefix}": ("ventas", "sum"),
            }
        )
        return g

    k6 = _agg_window(months_6, "6m")
    k12 = _agg_window(months_12, "12m")

    # 28 días y 29-56
    d0 = analysis.normalize()
    mask_28 = (df[date_col] > d0 - pd.Timedelta(days=28)) & (df[date_col] <= d0)
    mask_2956 = (df[date_col] > d0 - pd.Timedelta(days=56)) & (df[date_col] <= d0 - pd.Timedelta(days=28))

    u28 = df.loc[mask_28].groupby(sku_col)[qty_col].sum().rename("unidades_28d")
    u2956 = df.loc[mask_2956].groupby(sku_col)[qty_col].sum().rename("unidades_29_56d")
    last_sale = df.groupby(sku_col)[date_col].max().rename("fecha_ultima_venta")

    out = k12.join(k6, how="outer").join(u28, how="left").join(u2956, how="left").join(last_sale, how="left")
    out = out.fillna({"unidades_28d": 0, "unidades_29_56d": 0}).reset_index()

    # Estimación de demanda mensual = promedio de 3 señales en la misma unidad:
    # promedio 12m, promedio 6m y run-rate de 28d escalado a ~30 días.
    # (Antes se mezclaba unidades_28d totales con promedios mensuales.)
    out["unidades_28d_mensual"] = out["unidades_28d"] * (30.0 / 28.0)
    out["est_demanda"] = out[
        ["unidades_promedio_12m", "unidades_promedio_6m", "unidades_28d_mensual"]
    ].mean(axis=1)

    return out
