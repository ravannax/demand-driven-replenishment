# Desplegar la demo en Streamlit Community Cloud

Streamlit Community Cloud toma tu **repo público de GitHub** y levanta una app web gratuita.
No reemplaza al repo: es un **link extra** (tipo `https://share.streamlit.io/...` o `*.streamlit.app`) para que reclutadores jueguen con el dashboard sin instalar nada.

## Pasos

1. Publica este repositorio en GitHub (público).
2. Entra a [https://share.streamlit.io](https://share.streamlit.io) con tu cuenta de GitHub.
3. **New app** → elige el repo `demand-driven-replenishment`.
4. Main file path: `app/streamlit_app.py`
5. Python version: 3.11 (si te lo pide).
6. Deploy.

## Local (sin cloud)

```bash
pip install -r requirements.txt
python -m src.generate_synthetic
python -m src.pipeline
streamlit run app/streamlit_app.py
```

## Qué poner en el CV

- Link al **repo** (código + docs).
- Link a la **app Streamlit** (demo clicable).
