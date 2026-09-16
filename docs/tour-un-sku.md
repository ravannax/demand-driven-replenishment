# Tour de 1 SKU (numérico)

Supongamos el SKU `DP-FRE-0007` (ficticio):

| Dato | Valor |
|---|---|
| Demanda mediana 12m | 10 unidades/mes |
| Lead time | 2 meses |
| Stock hoy | 5 |
| Internados | 0 |
| Solicitados | 0 |
| Embarcados | 0 |
| Colchón | 3 meses |

### Paso a paso

1. **Stock proyectado al final del lead time**  
   `stock_ajustado = 5 + 0 - 10*2 = -15`  
   (durante 2 meses se “comen” 20 unidades; solo tienes 5 → quedas corto).

2. **Cobertura objetivo**  
   `lead + colchón = 2 + 3 = 5 meses` → `10 * 5 = 50` unidades deseadas al pedir.

3. **Cantidad a comprar**  
   `50 - (-15) - 0 - 0 = 65`

4. **ABCI** (aparte): si este SKU está entre el top de ventas acumuladas 6m, será S o A y lo priorizas en el presupuesto de compra.

### Excepción plaza

Si el proveedor empieza con `LOC` / `PLZ` / `URB`:

`cantidad = promedio_12m * 2 - stock`

Porque el reabastecimiento es rápido y no necesitas proyectar un lead largo.

### Excepción descontinuado

Si el SKU tiene `descontinuado = True`, la cantidad a comprar es **0** aunque la fórmula diga otra cosa (no se reponen ítems fuera de catálogo).

### Nota sobre `est_demanda`

En el Tour del dashboard aparece una estimación mensual que promedia promedio 12m, promedio 6m y el run-rate de 28 días escalado a mes (`×30/28`).  
La **compra estándar** sigue usando la **mediana 12m**, no esa estimación.
