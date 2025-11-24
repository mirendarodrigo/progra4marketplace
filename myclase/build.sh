# #!/usr/bin/env bash
# set -e
# python -m pip install --upgrade pip
# pip install -r requirements.txt;
# python manage.py collectstatic --no-input;
# python manage.py migrate; 

#!/usr/bin/env bash
# exit on error
set -o errexit

python -m pip install --upgrade pip
pip install -r requirements.txt

# Recolectar estáticos
python manage.py collectstatic --no-input

# --- ZONA DE DEPURACIÓN (Borrar después) ---
echo "---- INICIO DE LISTADO DE ARCHIVOS ESTATICOS ----"
# Verificamos si la carpeta existe y qué tiene dentro
ls -R staticfiles
echo "---- FIN DE LISTADO ----"
# -------------------------------------------

python manage.py migrate