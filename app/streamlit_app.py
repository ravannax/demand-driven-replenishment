"""Demo interactiva — Demand-Driven Replenishment.

Ejecutar local:
  streamlit run app/streamlit_app.py

Desplegar en Streamlit Community Cloud:
  conecta este repo público y apunta al archivo app/streamlit_app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.generate_synthetic import generate_all  # noqa: E402
from src.pipeline import run_pipeline  # noqa: E402

st.set_page_config(
    page_title="DDR — Reposición por demanda",
    page_icon="📦",
    layout="wide",
)

st.title("Reposición de stock por demanda y categorización ABCI")
st.caption(
    "Demo con 100 SKUs ficticios. La misma lógica se aplicó en producción sobre un catálogo de más de 70.000 SKUs."
)

with st.sidebar:
    st.header("Parámetros")
    seed = st.number_input("Seed (reproducibilidad)", min_value=1, value=42, step=1)
    buffer = st.slider("Colchón (meses)", min_value=1.0, max_value=6.0, value=3.0, step=0.5)
    cutoff = st.slider("Corte mes comercial (día)", min_value=1, max_value=28, value=21)
    if st.button("Regenerar datos + pipeline", type="primary"):
        with st.spinner("Generando..."):
            generate_all(seed=int(seed), out_dir=ROOT / "data" / "synthetic")
            run_pipeline(cutoff_day=int(cutoff), buffer_months=float(buffer))
        st.success("Listo")

data_dir = ROOT / "data" / "synthetic"
out_file = ROOT / "output" / "sugerido_compras.csv"

if not out_file.exists():
    generate_all(seed=42, out_dir=data_dir)
    run_pipeline()

df = pd.read_csv(out_file)
summary = pd.read_csv(ROOT / "output" / "resumen.csv")

c1, c2, c3, c4 = st.columns(4)
c1.metric("SKUs", int(summary.iloc[0]["skus"]))
c2.metric("Con compra > 0", int(summary.iloc[0]["skus_con_compra"]))
c3.metric("Unidades a comprar", f"{summary.iloc[0]['unidades_a_comprar']:,.0f}")
c4.metric("Costo total", f"${summary.iloc[0]['costo_total']:,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Resumen ABCI", "Sugerido de compras", "Tour 1 SKU", "Cómo leer esto"])

with tab1:
    counts = df["abci"].value_counts().reset_index()
    counts.columns = ["abci", "skus"]
    fig = px.bar(counts, x="abci", y="skus", title="Distribución ABCI", text="skus")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        """
        **ABCI en una frase:** ordenamos los productos por cuánto venden y los etiquetamos
        como en una despensa: lo crítico (S/A) no puede faltar; lo lento (C/I) se compra con más cuidado.
        """
    )

with tab2:
    show = df[df["cantidad_a_comprar"] > 0][
        [
            "sku",
            "descripcion",
            "familia",
            "abci",
            "modo_compra",
            "stock_total",
            "lead_time",
            "unidades_mediana_12m",
            "cantidad_a_comprar",
            "costo_total",
        ]
    ]
    st.dataframe(show, use_container_width=True, hide_index=True)
    st.download_button(
        "Descargar CSV del sugerido",
        data=show.to_csv(index=False).encode("utf-8"),
        file_name="sugerido_compras_filtrado.csv",
        mime="text/csv",
    )

with tab3:
    sku = st.selectbox("Elige un SKU", df.sort_values("ventas_6m", ascending=False)["sku"].tolist())
    row = df[df["sku"] == sku].iloc[0]
    st.subheader(f"{row['sku']} — {row['descripcion']}")
    left, right = st.columns(2)
    with left:
        st.write(
            {
                "ABCI": str(row["abci"]),
                "Modo compra": str(row["modo_compra"]),
                "Lead time (meses)": int(row["lead_time"]),
                "Stock": int(row["stock_total"]),
                "Solicitados": int(row["solicitados"]),
                "Embarcados": int(row["embarcados"]),
                "Internados": int(row["internados"]),
            }
        )
    with right:
        st.write(
            {
                "Mediana unidades 12m": round(float(row["unidades_mediana_12m"]), 2),
                "Promedio unidades 12m": round(float(row["unidades_promedio_12m"]), 2),
                "Unidades 28d": float(row["unidades_28d"]),
                "Est. demanda": round(float(row["est_demanda"]), 2),
                "Stock meses": round(float(row["stock_meses"]), 2),
                "Cantidad a comprar": round(float(row["cantidad_a_comprar"]), 2),
                "Costo total": round(float(row["costo_total"]), 2),
            }
        )
    st.info(
        "Si el modo es **estándar**: se cubre lead time + colchón, descontando stock y tránsito. "
        "Si es **plaza**: objetivo simplificado de ~2 meses con promedio (proveedor rápido)."
    )

with tab4:
    st.markdown(
        """
        ### Qué problema resuelve
        En un catálogo grande no puedes mirar SKU por SKU a ojo. Este motor resume demanda,
        clasifica importancia (ABCI) y propone **cuánto comprar**.

        ### Qué demuestra (CV)
        - Traducir reglas de negocio de supply chain a código reproducible
        - Ingeniería de datos con pandas (ventanas temporales, merges, exports)
        - Documentación didáctica y demo interactiva

        ### Escala
        Esta demo usa **100 SKUs** para que cualquiera la corra en minutos.
        La misma idea se usó en un entorno real con **más de 70.000 SKUs**.
        """
    )
