#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

# --- EL CAMBIO CLAVE ---
# --clear: Borra la carpeta de destino y fuerza la copia desde cero
# --no-input: No preguntes "estás seguro?"
python manage.py collectstatic --no-input --clear

# Migraciones
python manage.py migrate