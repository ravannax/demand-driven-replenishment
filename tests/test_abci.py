import pandas as pd

from src.abci import categorize_abc, classify_abci


def test_categorize_thresholds():
    assert categorize_abc(0.10) == "S"
    assert categorize_abc(0.70) == "A"
    assert categorize_abc(0.90) == "B"
    assert categorize_abc(0.99) == "C"


def test_classify_inactive_and_new():
    df = pd.DataFrame(
        [
            {"sku": "A", "ventas_6m": 1000, "es_nuevo": False, "fecha_ultima_venta": "2026-05-01"},
            {"sku": "B", "ventas_6m": 100, "es_nuevo": False, "fecha_ultima_venta": "2026-04-01"},
            {"sku": "C", "ventas_6m": 0, "es_nuevo": True, "fecha_ultima_venta": pd.NaT},
            {"sku": "D", "ventas_6m": 0, "es_nuevo": False, "fecha_ultima_venta": "2024-01-01"},
        ]
    )
    out = classify_abci(df, inactive_cutoff=pd.Timestamp("2025-06-01"))
    assert out.set_index("sku").loc["C", "abci"] == "C"  # nuevo inactivo → C
    assert out.set_index("sku").loc["D", "abci"] == "I12m"
