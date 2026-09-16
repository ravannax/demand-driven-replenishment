"""Generador de datos sintéticos 100% ficticios.

El seed fijo garantiza que cualquiera que clone el repo obtenga los mismos datos.
Ningún SKU, precio, stock ni demanda proviene de datos reales.
Los patrones (ventas irregulares, cola larga, lead times) son genéricos de retail/repuestos.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "data" / "synthetic"

FAMILIES = [
    ("FILTROS", ["aceite", "aire", "combustible", "habitaculo"]),
    ("FRENOS", ["pastilla", "disco", "tambor", "liquido"]),
    ("SUSPENSION", ["amortiguador", "buje", "rotula", "brazo"]),
    ("MOTOR", ["correa", "tensor", "bomba", "junta"]),
    ("ELECTRICOS", ["bateria", "alternador", "sensor", "relay"]),
]

LOCALES = [
    {"local_id": "NORTE", "nombre": "Local Norte"},
    {"local_id": "CENTRO", "nombre": "Local Centro"},
    {"local_id": "SUR", "nombre": "Local Sur"},
]

# Prefijos LOC/PLZ/URB = compra plaza (fórmula rápida)
SUPPLIERS = [
    ("IMP-ALPHA", 4),
    ("IMP-BETA", 5),
    ("IMP-GAMMA", 3),
    ("LOC-DELTA", 0),
    ("PLZ-ECHO", 0),
    ("URB-FOXTROT", 0),
]


def _sku_catalog(rng: np.random.Generator, n_skus: int = 100) -> pd.DataFrame:
    rows = []
    for i in range(1, n_skus + 1):
        fam, parts = FAMILIES[i % len(FAMILIES)]
        part = parts[i % len(parts)]
        supplier_code, lead = SUPPLIERS[i % len(SUPPLIERS)]
        # Cola larga: pocos SKUs "estrellas", muchos de baja rotación
        tier = rng.choice(["star", "mid", "tail"], p=[0.10, 0.30, 0.60])
        base_demand = {"star": rng.uniform(40, 120), "mid": rng.uniform(8, 35), "tail": rng.uniform(0.2, 6)}[tier]
        cost = float(np.round(rng.uniform(2.5, 180.0), 2))
        price = float(np.round(cost * rng.uniform(1.25, 1.85), 2))
        is_new = bool(rng.random() < 0.08)
        rows.append(
            {
                "sku": f"DP-{fam[:3]}-{i:04d}",
                "descripcion": f"{part.title()} {fam.title()} modelo {100 + i}",
                "familia": fam,
                "cod_proveedor": supplier_code,
                "proveedor": supplier_code.replace("-", " "),
                "lead_time": lead if not supplier_code.startswith(("LOC", "PLZ", "URB")) else 0,
                "costo_unitario": cost,
                "precio_mayor": price,
                "margen_esperado": float(np.round((price - cost) / price, 3)),
                "es_nuevo": is_new,
                "descontinuado": bool(rng.random() < 0.05),
                "tier_sintetico": tier,
                "base_demand": float(base_demand),
            }
        )
    return pd.DataFrame(rows)


def _sales_history(
    catalog: pd.DataFrame,
    rng: np.random.Generator,
    analysis_date: pd.Timestamp,
    months: int = 12,
) -> pd.DataFrame:
    """Genera líneas de venta diarias sintéticas por local."""
    end = analysis_date.normalize()
    start = (end - pd.DateOffset(months=months)).normalize()
    dates = pd.date_range(start, end, freq="D")
    rows = []

    # ~12% de SKUs sin ventas (inactivos) para demostrar ABCI I6m/I12m
    inactive_skus = set(
        catalog.sample(frac=0.12, random_state=int(rng.integers(0, 1_000_000)))["sku"]
    )

    for _, sku in catalog.iterrows():
        if sku["sku"] in inactive_skus and not sku["es_nuevo"]:
            continue
        # Probabilidad de venta por día según tier
        p = {"star": 0.55, "mid": 0.22, "tail": 0.05}[sku["tier_sintetico"]]
        seasonal = 1.0 + 0.15 * np.sin(np.arange(len(dates)) / 30.0)
        for loc in LOCALES:
            # Mix de demanda por local
            loc_factor = {"NORTE": 1.1, "CENTRO": 1.0, "SUR": 0.85}[loc["local_id"]]
            for d, seas in zip(dates, seasonal):
                if rng.random() > p * 0.35:  # sparse
                    continue
                qty = max(1, int(rng.poisson(sku["base_demand"] / 30 * loc_factor * seas) + 1))
                # Algunos días sin venta en cola: ya filtrado por p
                revenue = qty * sku["precio_mayor"] * rng.uniform(0.92, 1.05)
                rows.append(
                    {
                        "fecha": d,
                        "sku": sku["sku"],
                        "local_id": loc["local_id"],
                        "unidades": qty,
                        "ventas": float(np.round(revenue, 2)),
                        "tipo_cliente": rng.choice(["Mayorista", "Retail"], p=[0.7, 0.3]),
                    }
                )

    sales = pd.DataFrame(rows)
    if sales.empty:
        # Fallback mínimo para no romper demos
        sales = pd.DataFrame(
            [
                {
                    "fecha": end - pd.Timedelta(days=3),
                    "sku": catalog.iloc[0]["sku"],
                    "local_id": "CENTRO",
                    "unidades": 2,
                    "ventas": 100.0,
                    "tipo_cliente": "Mayorista",
                }
            ]
        )
    return sales


def _inventory(catalog: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    rows = []
    for _, sku in catalog.iterrows():
        months_cover = rng.uniform(0.2, 4.5)
        stock = max(0, int(sku["base_demand"] * months_cover + rng.integers(-3, 8)))
        ordered = max(0, int(rng.integers(0, 15) if sku["tier_sintetico"] != "tail" else rng.integers(0, 3)))
        shipped = max(0, int(rng.integers(0, 10) if ordered else 0))
        inbound = max(0, int(rng.integers(0, 8) if shipped else 0))
        rows.append(
            {
                "sku": sku["sku"],
                "stock_total": stock,
                "solicitados": ordered,
                "embarcados": shipped,
                "internados": inbound,
            }
        )
    return pd.DataFrame(rows)


def generate_all(
    seed: int = 42,
    n_skus: int = 100,
    n_locales: int = 3,
    months: int = 12,
    analysis_date: str = "2026-06-15",
    out_dir: Path | str | None = None,
) -> dict[str, pd.DataFrame]:
    """Genera y opcionalmente persiste el dataset sintético completo."""
    del n_locales  # fijo a 3 en LOCALES; parámetro documentado para claridad de API
    rng = np.random.default_rng(seed)
    analysis = pd.Timestamp(analysis_date)

    catalog = _sku_catalog(rng, n_skus)
    sales = _sales_history(catalog, rng, analysis, months)
    inventory = _inventory(catalog, rng)
    lead = catalog[["cod_proveedor", "lead_time"]].drop_duplicates()
    locales = pd.DataFrame(LOCALES)

    # Maestro productos (sin columnas internas de generación)
    products = catalog.drop(columns=["tier_sintetico", "base_demand"])

    tables = {
        "products": products,
        "sales": sales,
        "inventory": inventory,
        "lead_times": lead,
        "locales": locales,
        "meta": pd.DataFrame(
            [
                {
                    "seed": seed,
                    "n_skus": n_skus,
                    "n_locales": len(LOCALES),
                    "months": months,
                    "analysis_date": analysis.strftime("%Y-%m-%d"),
                    "nota": "Datos 100% ficticios. Escala demo: 100 SKUs. Lógica aplicada en producción sobre >70.000 SKUs.",
                }
            ]
        ),
    }

    if out_dir is not None:
        out = Path(out_dir)
        out.mkdir(parents=True, exist_ok=True)
        for name, frame in tables.items():
            frame.to_csv(out / f"{name}.csv", index=False)
        # Excel bundle para quien prefiera abrir en hoja de cálculo
        with pd.ExcelWriter(out / "dataset_sintetico.xlsx", engine="openpyxl") as xl:
            for name, frame in tables.items():
                frame.to_excel(xl, sheet_name=name[:31], index=False)

    return tables


if __name__ == "__main__":
    tables = generate_all(out_dir=DEFAULT_OUT)
    print("Generado en", DEFAULT_OUT)
    for k, v in tables.items():
        print(f"  {k}: {len(v):,} filas")
