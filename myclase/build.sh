#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

# Recolectar estáticos
python manage.py collectstatic --no-input

# Migraciones
python manage.py migrate