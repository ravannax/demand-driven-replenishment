# Publicar / actualizar este repo en GitHub (`ravannax`)

El repositorio público ya existe:

https://github.com/ravannax/demand-driven-replenishment

Demo Streamlit:

https://ravannax-demand-driven-replenishment-appstreamlit-app-bjfgz0.streamlit.app/

## Actualizar código

```bash
cd /ruta/a/demand-driven-replenishment
git add -A
git commit -m "tu mensaje"
git push origin main
```

Streamlit Cloud redespliega desde `main` automáticamente (o usa Reboot en el panel).

## Si partieras de cero (referencia)

1. https://github.com/new → owner **ravannax**, nombre **demand-driven-replenishment**, público, sin README.
2. `git remote add origin https://github.com/ravannax/demand-driven-replenishment.git`
3. `git push -u origin main`
4. Conectar en [share.streamlit.io](https://share.streamlit.io) → `app/streamlit_app.py`
