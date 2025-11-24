#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

# Recolectar estáticos
python manage.py collectstatic --no-input

# --- DEPURACIÓN: LA HORA DE LA VERDAD ---
echo "1. ¿Dónde estoy parado?"
pwd

echo "2. ¿Qué carpetas hay aquí en la raíz?"
ls -F

echo "3. Vamos a mirar dentro de la ruta que salió en los logs:"
# Usamos la ruta que vimos en tu log anterior
ls -R myclase/staticfiles || echo "⚠️ No se pudo acceder a myclase/staticfiles"
# ----------------------------------------

python manage.py migrate