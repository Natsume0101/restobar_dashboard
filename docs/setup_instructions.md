# 🔌 Guía de Conexión: GitHub + Streamlit Cloud

Sigue estos pasos para conectar tu repositorio y activar el despliegue automático.

## Paso 1: Subir código a GitHub
Asegúrate de que todos los archivos nuevos (carpeta `.github`, carpeta `docs`, etc.) estén en tu repositorio en GitHub.
*(Si estás trabajando localmente, necesitas hacer `git add .`, `git commit -m "Configurar despliegue"`, y `git push origin main`)*

## Paso 2: Crear cuenta en Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io/).
2. Haz clic en **"Sign up"** y selecciona **"Continue with GitHub"**.
3. Autoriza a Streamlit para acceder a tus repositorios públicos (o privados si es el caso).

## Paso 3: Desplegar la App
1. En el panel principal de Streamlit Cloud, haz clic en **"New app"**.
2. Selecciona tu repositorio: `Natsume0101/restobar_dashboard`.
3. Selecciona la rama: `main`.
4. **Main file path**: Escribe `dashboard.py` (o selecciónalo del menú).
5. Haz clic en **"Deploy!"**.

## Paso 4: ¡Listo!
- Streamlit comenzará a construir tu app (verás una consola negra a la derecha).
- Si todo sale bien, verás tu dashboard con globos de celebración.
- **Copia la URL** de la barra de direcciones. Esa es la que enviarás a tu equipo (pégala en `docs/whatsapp_template.md`).

## Cómo funciona la Automatización
A partir de ahora:
1. Tú haces cambios en tu computadora.
2. Haces **Push** a GitHub.
3. GitHub Actions (la automatización que creamos) verificará que no hayas roto nada importante.
4. Si GitHub aprueba, Streamlit Cloud actualizará tu app automáticamente en unos minutos.
