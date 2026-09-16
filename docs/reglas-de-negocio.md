# Reglas de negocio

Documento de referencia para reclutadores y para quien lea el código.
La implementación vive en `src/`; los tests en `tests/` fijan el comportamiento.

## 1. KPIs de demanda (`src/kpis.py`)

Sobre ventas diarias, por SKU:

| Señal | Qué mide |
|---|---|
| `unidades_promedio_12m` / `_6m` | Promedio mensual (meses sin venta = 0) |
| `unidades_mediana_12m` / `_6m` | Mediana mensual (base de la fórmula estándar) |
| `unidades_28d` | Unidades en los últimos 28 días (total, no mensual) |
| `unidades_28d_mensual` | `unidades_28d × 30/28` (misma unidad que los promedios) |
| `est_demanda` | Media de promedio 12m, promedio 6m y `unidades_28d_mensual` |

La compra **estándar** usa la mediana 12m (no `est_demanda`).  
`est_demanda` es una señal de lectura / Tour en el dashboard.

Mes comercial: el “mes” de negocio corta el día 21 (configurable).

## 2. ABCI (`src/abci.py`)

1. Ordenar SKUs por `ventas_6m` descendente.
2. Acumulado Pareto:
   - **S** ≤ 65 %
   - **A** ≤ 80 %
   - **B** ≤ 95 %
   - resto **C**
3. Sin ventas: **I**; si además `es_nuevo` → **C**.
4. Inactivo largo: última venta antes del corte 12m → **I12m**; si no → **I6m**.

## 3. Cantidad a comprar (`src/replenishment.py`)

### Estándar (proveedor no plaza)

\[
\begin{aligned}
\text{stock\_ajustado} &= \text{stock} + \text{internados} - \text{demanda}\times\text{lead} \\
\text{cantidad} &= \max\bigl(0,\ \text{demanda}\times(\text{lead}+\text{colchón}) - \text{stock\_ajustado} - \text{solicitados} - \text{embarcados}\bigr)
\end{aligned}
\]

- `demanda` = mediana mensual 12m  
- `colchón` por defecto = 3 meses (slider en Streamlit)

### Plaza (`cod_proveedor` empieza con `LOC`, `PLZ` o `URB`)

\[
\text{cantidad} = \max(0,\ \text{promedio\_12m}\times 2 - \text{stock})
\]

Reposición rápida: objetivo ~2 meses con **promedio**, no mediana.

### Descontinuado

Si `descontinuado = True` → `cantidad_a_comprar = 0` y `modo_compra = descontinuado`.  
No se reponen ítems fuera de catálogo activo.

El cálculo está **vectorizado** (pandas/numpy) para que la misma idea escale a decenas de miles de SKUs.

## 4. Orden del sugerido (`src/pipeline.py`)

1. KPIs → merge productos/inventario → ABCI → reposición.  
2. Orden: ABCI (S → I12m) y, dentro de cada clase, mayor `cantidad_a_comprar`.  
3. Export: `output/sugerido_compras.csv|.xlsx` y `output/resumen.csv|.xlsx`.

## 5. Demo Streamlit (`app/streamlit_app.py`)

- **Colchón** y **corte** se reapican al instante (recalcula el pipeline).  
- **Regenerar datos sintéticos** solo si cambias el seed o quieres otro dataset.  
- Cold start en Streamlit Cloud: si no hay CSV, genera seed=42 y corre el pipeline.

## 6. Reproducibilidad

```bash
python -m src.generate_synthetic   # seed=42
python -m src.pipeline
pytest -q
```

Datos y outputs **no** van a git (`.gitignore`); cualquiera regenera lo mismo con el seed.
