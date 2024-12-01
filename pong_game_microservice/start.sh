chmod 700 -R venv

. venv/bin/activate

pip install -r requirements.txt

python manage.py runserver 0.0.0.0:9002
