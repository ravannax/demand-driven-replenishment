"""Clasificación ABCI (Pareto extendido).

Analogía: ordenas la despensa por cuánto aporta cada producto a las ventas.
- S: los pocos que generan la mayor parte (super A)
- A / B / C: el resto del Pareto
- I: sin venta reciente (inactivo)
"""

from __future__ import annotations

import pandas as pd


DEFAULT_THRESHOLDS = {
    "S": 0.65,
    "A": 0.80,
    "B": 0.95,
}


def categorize_abc(cum_pct: float, thresholds: dict[str, float] | None = None) -> str:
    """Asigna S/A/B/C según porcentaje acumulado de ventas."""
    thr = thresholds or DEFAULT_THRESHOLDS
    if cum_pct <= thr["S"]:
        return "S"
    if cum_pct <= thr["A"]:
        return "A"
    if cum_pct <= thr["B"]:
        return "B"
    return "C"


def classify_abci(
    df: pd.DataFrame,
    sku_col: str = "sku",
    sales_col: str = "ventas_6m",
    is_new_col: str = "es_nuevo",
    last_sale_col: str = "fecha_ultima_venta",
    inactive_cutoff: pd.Timestamp | None = None,
    thresholds: dict[str, float] | None = None,
) -> pd.DataFrame:
    """Clasifica SKUs en S/A/B/C/I6m/I12m.

    Pasos:
    1. Pareto sobre SKUs con venta > 0 en la ventana.
    2. Sin venta → I (luego se subdivide).
    3. Código nuevo + I → C (dar chance a lanzamientos).
    4. I12m si última venta es anterior al corte de 12 meses; si no I6m.
    """
    out = df.copy()
    thr = thresholds or DEFAULT_THRESHOLDS

    with_sales = out[out[sales_col] > 0].sort_values(sales_col, ascending=False).copy()
    total = with_sales[sales_col].sum()
    if total > 0:
        with_sales["pct_acum"] = with_sales[sales_col].cumsum() / total
        with_sales["abci"] = with_sales["pct_acum"].map(lambda x: categorize_abc(x, thr))
    else:
        with_sales["pct_acum"] = 0.0
        with_sales["abci"] = "C"

    abci_map = with_sales.set_index(sku_col)["abci"].to_dict()
    pct_map = with_sales.set_index(sku_col)["pct_acum"].to_dict()
    out["abci"] = out[sku_col].map(abci_map)
    out["pct_acum_ventas"] = out[sku_col].map(pct_map)

    inactive_mask = out["abci"].isna()
    out.loc[inactive_mask, "abci"] = "I"

    if is_new_col in out.columns:
        new_inactive = (out[is_new_col] == True) & (out["abci"] == "I")  # noqa: E712
        out.loc[new_inactive, "abci"] = "C"

    if inactive_cutoff is not None and last_sale_col in out.columns:
        still_i = out["abci"] == "I"
        last = pd.to_datetime(out[last_sale_col], errors="coerce")
        i12 = still_i & (last.isna() | (last < inactive_cutoff))
        i6 = still_i & ~i12
        out.loc[i12, "abci"] = "I12m"
        out.loc[i6, "abci"] = "I6m"
    else:
        out.loc[out["abci"] == "I", "abci"] = "I6m"

    return out
