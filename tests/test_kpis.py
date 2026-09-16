import pandas as pd

from src.kpis import build_sku_kpis


def test_est_demanda_uses_monthly_equivalent_of_28d():
    # Un solo SKU: 30 uds en 28d y 10/mes en los meses del grid → 28d_mensual ≈ 32.14
    # Media de (10, 10, 32.14) ≈ 17.38
    sales = pd.DataFrame(
        {
            "sku": ["X"] * 3,
            "fecha": pd.to_datetime(["2026-08-20", "2026-08-25", "2026-08-28"]),
            "unidades": [10, 10, 10],
            "ventas": [100.0, 100.0, 100.0],
        }
    )
    out = build_sku_kpis(sales, analysis_date="2026-09-01", cutoff_day=21)
    row = out.iloc[0]
    expected_28d_m = 30.0 * (30.0 / 28.0)
    assert abs(row["unidades_28d_mensual"] - expected_28d_m) < 1e-9
    # Promedios mensuales incluyen muchos ceros del grid → est_demanda < unidades_28d crudo
    assert row["est_demanda"] != row[["unidades_promedio_12m", "unidades_promedio_6m", "unidades_28d"]].mean()
    assert abs(
        row["est_demanda"]
        - row[["unidades_promedio_12m", "unidades_promedio_6m", "unidades_28d_mensual"]].mean()
    ) < 1e-9
