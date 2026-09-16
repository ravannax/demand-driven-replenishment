"""Fórmulas de cantidad a comprar (sugerido de compras / SC).

Analogía: miras cuánto se consume un producto al mes, cuánto tarda en llegar
el pedido (lead time), cuánto tienes hoy y cuánto ya pediste. Compras lo
necesario para no quedarte seco durante la espera + un colchón.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def qty_standard(
    demand: float,
    lead_time: float,
    stock: float,
    inbound: float = 0.0,
    ordered: float = 0.0,
    shipped: float = 0.0,
    buffer_months: float = 3.0,
) -> float:
    """Fórmula general de reposición.

    1) Proyecta stock al final del lead time:
       stock_ajustado = stock + inbound - demand * lead_time
    2) Objetivo de cobertura = lead_time + buffer_months
    3) Descuenta lo ya pedido / embarcado
    4) Nunca negativo
    """
    demand = float(demand or 0)
    lead_time = float(lead_time or 0)
    stock = float(stock or 0)
    inbound = float(inbound or 0)
    ordered = float(ordered or 0)
    shipped = float(shipped or 0)

    stock_ajustado = stock + inbound - demand * lead_time
    qty = demand * (lead_time + buffer_months) - stock_ajustado - ordered - shipped
    return float(max(0.0, qty))


def qty_plaza(avg_monthly_demand: float, stock: float, target_months: float = 2.0) -> float:
    """Excepción 'compra plaza' (proveedores de reposición rápida).

    Usa promedio (no mediana) porque en ítems irregulares la mediana suele ser 0.
    Objetivo simplificado: ~target_months de stock.
    """
    avg = float(avg_monthly_demand or 0)
    stock = float(stock or 0)
    return float(max(0.0, avg * target_months - stock))


def is_plaza_supplier(supplier_code: str, prefixes: tuple[str, ...] = ("LOC", "PLZ", "URB")) -> bool:
    """Proveedores locales / plaza: lead corto, fórmula simplificada."""
    code = str(supplier_code or "").upper()
    return any(code.startswith(p) for p in prefixes)


def stock_months(stock: float, median_demand: float) -> float:
    if median_demand and median_demand > 0:
        return float(stock) / float(median_demand)
    return float(stock)


def transit_months(ordered: float, shipped: float, median_demand: float) -> float:
    transit = float(ordered or 0) + float(shipped or 0)
    if median_demand and median_demand > 0:
        return transit / float(median_demand)
    return transit


def apply_replenishment(
    df: pd.DataFrame,
    demand_median_col: str = "unidades_mediana_12m",
    demand_avg_col: str = "unidades_promedio_12m",
    lead_col: str = "lead_time",
    stock_col: str = "stock_total",
    inbound_col: str = "internados",
    ordered_col: str = "solicitados",
    shipped_col: str = "embarcados",
    supplier_col: str = "cod_proveedor",
    unit_cost_col: str = "costo_unitario",
    buffer_months: float = 3.0,
    plaza_prefixes: tuple[str, ...] = ("LOC", "PLZ", "URB"),
) -> pd.DataFrame:
    """Agrega columnas de decisión de compra al dataframe de SKUs."""
    out = df.copy()

    qtys = []
    modes = []
    for _, row in out.iterrows():
        plaza = is_plaza_supplier(row.get(supplier_col, ""), plaza_prefixes)
        if plaza:
            q = qty_plaza(row.get(demand_avg_col, 0), row.get(stock_col, 0))
            modes.append("plaza")
        else:
            q = qty_standard(
                demand=row.get(demand_median_col, 0),
                lead_time=row.get(lead_col, 0),
                stock=row.get(stock_col, 0),
                inbound=row.get(inbound_col, 0),
                ordered=row.get(ordered_col, 0),
                shipped=row.get(shipped_col, 0),
                buffer_months=buffer_months,
            )
            modes.append("estandar")
        qtys.append(q)

    out["modo_compra"] = modes
    out["cantidad_a_comprar"] = qtys
    out["stock_meses"] = [
        stock_months(r.get(stock_col, 0), r.get(demand_median_col, 0)) for _, r in out.iterrows()
    ]
    out["transito_meses"] = [
        transit_months(r.get(ordered_col, 0), r.get(shipped_col, 0), r.get(demand_median_col, 0))
        for _, r in out.iterrows()
    ]
    if unit_cost_col in out.columns:
        out["costo_total"] = out["cantidad_a_comprar"] * out[unit_cost_col].fillna(0)
    else:
        out["costo_total"] = np.nan

    return out
