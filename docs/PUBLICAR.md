# Publicar este repo en tu GitHub (`ravannax`)

El entorno del agente **no puede crear** repositorios nuevos en tu cuenta (permiso `createRepository` bloqueado).
El proyecto ya está listo en local; solo falta crearlo en GitHub y hacer push.

## Opción rápida (GitHub web)

1. Abre: https://github.com/new
2. Owner: **ravannax**
3. Repository name: **demand-driven-replenishment**
4. Public
5. **No** marques README / .gitignore / license (el repo ya los trae)
6. Create repository

Luego, en la máquina donde tengas este proyecto:

```bash
cd /ruta/a/demand-driven-replenishment
git remote add origin https://github.com/ravannax/demand-driven-replenishment.git
git push -u origin main
```

Si me avisas cuando el repo vacío exista, puedo intentar el `git push` desde aquí.

## Después: demo Streamlit

1. https://share.streamlit.io → New app
2. Repo: `ravannax/demand-driven-replenishment`
3. File: `app/streamlit_app.py`
4. Deploy → copia el link `*.streamlit.app` a tu CV junto al link del repo
