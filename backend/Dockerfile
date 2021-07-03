FROM python:3.8-alpine

RUN adduser -D standings_user
WORKDIR /home/backend

COPY requirements.txt requirements.txt

RUN python -m venv venv
RUN pip install -r requirements.txt
RUN venv/bin/pip install -r requirements.txt
RUN venv/bin/pip install gunicorn

RUN echo 'Copying files ...'
COPY standings/ ./standings/
COPY app_config.yaml app_config.yaml
COPY log_config.yaml log_config.yaml

RUN chmod +x standings/run.sh

RUN chown -R standings_user:standings_user ./
USER standings_user

EXPOSE 5000
ENTRYPOINT ["standings/run.sh"]