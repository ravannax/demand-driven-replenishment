# Desplegar la demo en Streamlit Community Cloud

Streamlit Community Cloud toma tu **repo público de GitHub** y levanta una app web gratuita.
No reemplaza al repo: es un **link extra** para que reclutadores jueguen con el dashboard sin instalar nada.

## Demo publicada

https://ravannax-demand-driven-replenishment-appstreamlit-app-bjfgz0.streamlit.app/

Main file: `app/streamlit_app.py` · Repo: `ravannax/demand-driven-replenishment`.

Tras un `git push` a `main`, Streamlit Cloud suele redesplegar solo (o “Reboot app” en el panel).

## Redesplegar / crear otra app

1. [https://share.streamlit.io](https://share.streamlit.io) con tu GitHub.
2. **New app** → repo `demand-driven-replenishment`.
3. Main file path: `app/streamlit_app.py`
4. Python: 3.11 (si lo pide) · Deploy.

## Local (sin cloud)

```bash
pip install -r requirements.txt
python -m src.generate_synthetic
python -m src.pipeline
streamlit run app/streamlit_app.py
```

En la sidebar: **colchón** y **corte** recalculan al instante; el botón regenera solo los sintéticos (seed).

## Qué poner en el CV

- Link al **repo** (código + docs + CI).
- Link a la **app Streamlit** (demo clicable).
