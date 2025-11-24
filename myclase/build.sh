#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

# Recolectar estáticos
python manage.py collectstatic --no-input

# --- DEPURACIÓN: BÚSQUEDA IMPLACABLE ---
echo "---- ¿DÓNDE ESTÁ WALLY? (styles.css) ----"

# Buscamos 'styles.css' en CUALQUIER carpeta desde aquí
find . -name "styles.css"

echo "---- ¿DÓNDE ESTÁ LA CARPETA STATICFILES? ----"
# Buscamos cualquier carpeta que se llame 'staticfiles'
find . -type d -name "staticfiles"
# ----------------------------------------

python manage.py migrate