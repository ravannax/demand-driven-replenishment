"""Mes comercial con corte configurable (por defecto día 21).

Analogía: imagina que tu "mes de negocio" no empieza el 1, sino el 21.
Así, del 21 de abril al 20 de mayo es el "mes comercial de mayo".
"""

from __future__ import annotations

from datetime import date

import pandas as pd


def commercial_month_start(ref: date | pd.Timestamp, cutoff_day: int = 21) -> pd.Timestamp:
    """Devuelve el primer día del mes comercial que contiene `ref`.

    Si el día >= cutoff_day, ya estamos en el mes comercial *siguiente*
    (anclado al día 1 de ese mes calendario para agrupar).
    """
    ts = pd.Timestamp(ref)
    if ts.day >= cutoff_day:
        # Entramos al mes comercial del mes calendario siguiente
        anchor = (ts + pd.offsets.MonthBegin(1)).normalize()
    else:
        anchor = ts.replace(day=1)
    return pd.Timestamp(anchor)


def commercial_month_label(ref: date | pd.Timestamp, cutoff_day: int = 21) -> str:
    """Etiqueta YYYY-MM del mes comercial."""
    start = commercial_month_start(ref, cutoff_day)
    return start.strftime("%Y-%m")


def adjust_to_commercial_month(series: pd.Series, cutoff_day: int = 21) -> pd.Series:
    """Convierte fechas de documento al ancla (día 1) del mes comercial."""
    return series.map(lambda d: commercial_month_start(d, cutoff_day))


def window_bounds(
    analysis_date: date | pd.Timestamp,
    n_months: int,
    cutoff_day: int = 21,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Ventana de los últimos `n_months` meses comerciales hasta el mes actual."""
    end = commercial_month_start(analysis_date, cutoff_day)
    start = end - pd.DateOffset(months=n_months - 1)
    return pd.Timestamp(start), pd.Timestamp(end)
