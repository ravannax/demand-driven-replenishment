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
    discontinued_col: str = "descontinuado",
    buffer_months: float = 3.0,
    plaza_prefixes: tuple[str, ...] = ("LOC", "PLZ", "URB"),
) -> pd.DataFrame:
    """Agrega columnas de decisión de compra al dataframe de SKUs.

    SKUs descontinuados quedan con cantidad_a_comprar = 0 (no se reponen).
    """
    out = df.copy()

    suppliers = out[supplier_col].fillna("").astype(str) if supplier_col in out.columns else pd.Series("", index=out.index)
    plaza_mask = suppliers.str.upper().str.startswith(plaza_prefixes)

    demand_med = (
        out[demand_median_col].fillna(0).astype(float)
        if demand_median_col in out.columns
        else pd.Series(0.0, index=out.index)
    )
    demand_avg = (
        out[demand_avg_col].fillna(0).astype(float)
        if demand_avg_col in out.columns
        else pd.Series(0.0, index=out.index)
    )
    lead = (
        out[lead_col].fillna(0).astype(float)
        if lead_col in out.columns
        else pd.Series(0.0, index=out.index)
    )
    stock = (
        out[stock_col].fillna(0).astype(float)
        if stock_col in out.columns
        else pd.Series(0.0, index=out.index)
    )
    inbound = (
        out[inbound_col].fillna(0).astype(float)
        if inbound_col in out.columns
        else pd.Series(0.0, index=out.index)
    )
    ordered = (
        out[ordered_col].fillna(0).astype(float)
        if ordered_col in out.columns
        else pd.Series(0.0, index=out.index)
    )
    shipped = (
        out[shipped_col].fillna(0).astype(float)
        if shipped_col in out.columns
        else pd.Series(0.0, index=out.index)
    )

    stock_ajustado = stock + inbound - demand_med * lead
    qty_std = np.maximum(0.0, demand_med * (lead + buffer_months) - stock_ajustado - ordered - shipped)
    qty_plz = np.maximum(0.0, demand_avg * 2.0 - stock)

    out["modo_compra"] = np.where(plaza_mask, "plaza", "estandar")
    out["cantidad_a_comprar"] = np.where(plaza_mask, qty_plz, qty_std)

    if discontinued_col in out.columns:
        discontinued = out[discontinued_col].fillna(False).astype(bool)
        out.loc[discontinued, "cantidad_a_comprar"] = 0.0
        out.loc[discontinued, "modo_compra"] = "descontinuado"

    med = demand_med.replace(0, np.nan)
    out["stock_meses"] = (stock / med).fillna(stock)
    out["transito_meses"] = ((ordered + shipped) / med).fillna(ordered + shipped)

    if unit_cost_col in out.columns:
        out["costo_total"] = out["cantidad_a_comprar"] * out[unit_cost_col].fillna(0)
    else:
        out["costo_total"] = np.nan

    return out
