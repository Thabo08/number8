#!/bin/sh

export PYTHONPATH="${PYTHONPATH}:/app/"
export PYTHONPATH="${PYTHONPATH}:/app/backend/"
export PYTHONPATH="${PYTHONPATH}:/app/backend/standings/"

working_dir="/app/backend/standings"
if cd $working_dir;
then
  export FLASK_APP=main.py
  exec gunicorn -b :5000 --access-logfile - --error-logfile - main:app
else
  echo "$working_dir does not exist"
  return 1
fi