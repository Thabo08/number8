#!/bin/sh
source /home/backend/venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:/home/"
export PYTHONPATH="${PYTHONPATH}:/home/backend/"
export PYTHONPATH="${PYTHONPATH}:/home/backend/standings/"
cd /home/backend/standings
export FLASK_APP=main.py
exec gunicorn -b :5000 --access-logfile - --error-logfile - main:app