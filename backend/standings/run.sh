#!/bin/sh
source /home/backend/venv/bin/activate
#export PYTHONPATH=$PYTHONPATH:/home/backend
export PYTHONPATH="${PYTHONPATH}:/home/backend/"
export PYTHONPATH="${PYTHONPATH}:/home/backend/standings"
cd /home/backend/standings
#python -m http.server 8000
python -m main.py