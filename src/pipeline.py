"""Pipeline completo: KPIs → ABCI → reposición → export."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .abci import classify_abci
from .commercial_month import commercial_month_start
from .kpis import build_sku_kpis
from .replenishment import apply_replenishment

ROOT = Path(__file__).resolve().parents[1]


def run_pipeline(
    data_dir: Path | str | None = None,
    output_dir: Path | str | None = None,
    analysis_date: str | None = None,
    cutoff_day: int = 21,
    buffer_months: float = 3.0,
) -> pd.DataFrame:
    data_dir = Path(data_dir or ROOT / "data" / "synthetic")
    output_dir = Path(output_dir or ROOT / "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    products = pd.read_csv(data_dir / "products.csv")
    sales = pd.read_csv(data_dir / "sales.csv", parse_dates=["fecha"])
    inventory = pd.read_csv(data_dir / "inventory.csv")
    meta = pd.read_csv(data_dir / "meta.csv")

    if analysis_date is None:
        analysis_date = str(meta.iloc[0]["analysis_date"])

    kpis = build_sku_kpis(sales, analysis_date=analysis_date, cutoff_day=cutoff_day)

    merged = products.merge(kpis, on="sku", how="left").merge(inventory, on="sku", how="left")
    for col in [
        "unidades_promedio_12m",
        "unidades_mediana_12m",
        "unidades_promedio_6m",
        "unidades_mediana_6m",
        "ventas_6m",
        "ventas_12m",
        "unidades_28d",
        "est_demanda",
        "stock_total",
        "solicitados",
        "embarcados",
        "internados",
    ]:
        if col in merged.columns:
            merged[col] = merged[col].fillna(0)

    analysis_ts = pd.Timestamp(analysis_date)
    inactive_cutoff = commercial_month_start(analysis_ts, cutoff_day) - pd.DateOffset(months=12)

    merged = classify_abci(
        merged,
        sales_col="ventas_6m",
        is_new_col="es_nuevo",
        last_sale_col="fecha_ultima_venta",
        inactive_cutoff=pd.Timestamp(inactive_cutoff),
    )

    merged["margen_real_proxy"] = (
        (merged["precio_mayor"] - merged["costo_unitario"]) / merged["precio_mayor"]
    ).round(3)
    merged["margen_diff"] = (merged["margen_real_proxy"] - merged["margen_esperado"]).round(3)

    merged = apply_replenishment(merged, buffer_months=buffer_months)

    # Orden útil para compradores: primero lo que hay que comprar, por ABCI
    abci_order = {"S": 0, "A": 1, "B": 2, "C": 3, "I6m": 4, "I12m": 5}
    merged["_ord"] = merged["abci"].map(abci_order).fillna(9)
    merged = merged.sort_values(["_ord", "cantidad_a_comprar"], ascending=[True, False]).drop(columns=["_ord"])

    out_xlsx = output_dir / "sugerido_compras.xlsx"
    out_csv = output_dir / "sugerido_compras.csv"
    merged.to_csv(out_csv, index=False)
    merged.to_excel(out_xlsx, index=False, sheet_name="SC")

    # Resumen ejecutivo
    summary = pd.DataFrame(
        [
            {
                "analysis_date": analysis_date,
                "skus": len(merged),
                "skus_con_compra": int((merged["cantidad_a_comprar"] > 0).sum()),
                "unidades_a_comprar": float(merged["cantidad_a_comprar"].sum()),
                "costo_total": float(merged["costo_total"].sum()),
                "skus_S": int((merged["abci"] == "S").sum()),
                "skus_A": int((merged["abci"] == "A").sum()),
                "skus_B": int((merged["abci"] == "B").sum()),
                "skus_C": int((merged["abci"] == "C").sum()),
                "skus_I6m": int((merged["abci"] == "I6m").sum()),
                "skus_I12m": int((merged["abci"] == "I12m").sum()),
            }
        ]
    )
    summary.to_csv(output_dir / "resumen.csv", index=False)
    summary.to_excel(output_dir / "resumen.xlsx", index=False)

    return merged


if __name__ == "__main__":
    df = run_pipeline()
    print(df[["sku", "abci", "cantidad_a_comprar", "costo_total", "modo_compra"]].head(15).to_string(index=False))
    print("\nFilas:", len(df))
