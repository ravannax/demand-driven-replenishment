# Arquitectura

```text
┌─────────────────────┐
│  Generador sintético │  seed fijo → products / sales / inventory
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  KPIs por SKU        │  28d / 6m / 12m + est_demanda (unidades mensuales)
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Clasificación ABCI  │  Pareto ventas 6m + inactivos / nuevos
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Motor de reposición │  estándar | plaza | descontinuado (=0)
└──────────┬──────────┘
           ▼
     Excel / CSV          Dashboard Streamlit
     (output/)            (app/streamlit_app.py)
```

Reglas detalladas: [reglas-de-negocio.md](reglas-de-negocio.md).

## Módulos

| Módulo | Responsabilidad |
|---|---|
| `src/generate_synthetic.py` | Datos ficticios reproducibles |
| `src/commercial_month.py` | Mes comercial (corte día 21) |
| `src/kpis.py` | Indicadores de demanda/ventas |
| `src/abci.py` | Clasificación S/A/B/C/I* |
| `src/replenishment.py` | Cantidad a comprar (vectorizado) |
| `src/pipeline.py` | Orquestación + export |
| `app/streamlit_app.py` | Demo interactiva |
| `.github/workflows/ci.yml` | `pytest` en cada push/PR |

Los **notebooks** son la cara didáctica; la lógica testeable vive en `src/`.
