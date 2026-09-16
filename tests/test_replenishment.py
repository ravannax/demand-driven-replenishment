from src.replenishment import is_plaza_supplier, qty_plaza, qty_standard


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
