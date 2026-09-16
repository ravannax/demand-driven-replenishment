import pandas as pd

from src.replenishment import apply_replenishment, is_plaza_supplier, qty_plaza, qty_standard


def test_qty_standard_walkthrough():
    # demanda 10/mes, lead 2, stock 5, sin tránsito → objetivo 5 meses = 50, stock_aj = 5-20 = -15
    # qty = 50 - (-15) = 65
    assert qty_standard(demand=10, lead_time=2, stock=5, buffer_months=3) == 65


def test_qty_never_negative():
    assert qty_standard(demand=1, lead_time=1, stock=1000, buffer_months=3) == 0


def test_plaza():
    assert qty_plaza(avg_monthly_demand=10, stock=5, target_months=2) == 15
    assert is_plaza_supplier("LOC-DELTA")
    assert not is_plaza_supplier("IMP-ALPHA")


def test_discontinued_gets_zero_qty():
    df = pd.DataFrame(
        [
            {
                "sku": "LIVE",
                "cod_proveedor": "IMP-A",
                "unidades_mediana_12m": 10,
                "unidades_promedio_12m": 12,
                "lead_time": 2,
                "stock_total": 5,
                "internados": 0,
                "solicitados": 0,
                "embarcados": 0,
                "costo_unitario": 3.0,
                "descontinuado": False,
            },
            {
                "sku": "DEAD",
                "cod_proveedor": "IMP-A",
                "unidades_mediana_12m": 10,
                "unidades_promedio_12m": 12,
                "lead_time": 2,
                "stock_total": 5,
                "internados": 0,
                "solicitados": 0,
                "embarcados": 0,
                "costo_unitario": 3.0,
                "descontinuado": True,
            },
        ]
    )
    out = apply_replenishment(df)
    assert out.set_index("sku").loc["LIVE", "cantidad_a_comprar"] == 65
    assert out.set_index("sku").loc["DEAD", "cantidad_a_comprar"] == 0
    assert out.set_index("sku").loc["DEAD", "modo_compra"] == "descontinuado"


def test_apply_plaza_vectorized():
    df = pd.DataFrame(
        [
            {
                "sku": "P1",
                "cod_proveedor": "LOC-1",
                "unidades_mediana_12m": 0,
                "unidades_promedio_12m": 10,
                "lead_time": 1,
                "stock_total": 5,
                "internados": 0,
                "solicitados": 0,
                "embarcados": 0,
                "costo_unitario": 2.0,
                "descontinuado": False,
            }
        ]
    )
    out = apply_replenishment(df)
    assert out.iloc[0]["modo_compra"] == "plaza"
    assert out.iloc[0]["cantidad_a_comprar"] == 15
