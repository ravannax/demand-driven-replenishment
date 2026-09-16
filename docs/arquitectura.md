# Arquitectura

```text
┌─────────────────────┐
│  Generador sintético │  seed fijo → products / sales / inventory
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  KPIs por SKU        │  ventanas 28d / 6m / 12m, est_demanda
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Clasificación ABCI  │  Pareto ventas 6m + inactivos / nuevos
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Motor de reposición │  fórmula estándar o plaza
└──────────┬──────────┘
           ▼
     Excel / CSV          Dashboard Streamlit
     (output/)            (app/streamlit_app.py)
```

## Módulos

| Módulo | Responsabilidad |
|---|---|
| `src/generate_synthetic.py` | Datos ficticios reproducibles |
| `src/commercial_month.py` | Mes comercial (corte día 21) |
| `src/kpis.py` | Indicadores de demanda/ventas |
| `src/abci.py` | Clasificación S/A/B/C/I* |
| `src/replenishment.py` | Cantidad a comprar |
| `src/pipeline.py` | Orquestación + export |

Los **notebooks** son la cara didáctica; la lógica testeable vive en `src/`.
