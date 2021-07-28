FROM python:3.9-alpine

RUN echo 'Running upgrades ...'
RUN apk -U upgrade

RUN adduser -D standings_user
WORKDIR /home/backend

RUN echo 'Copying files ...'
COPY standings/ ./standings/
COPY app_config.yaml app_config.yaml
COPY log_config.yaml log_config.yaml
COPY requirements.txt requirements.txt

RUN echo 'Installing dependencies ...'
RUN pip install -r requirements.txt

RUN chmod +x standings/run.sh

RUN chown -R standings_user:standings_user ./
USER standings_user

EXPOSE 5000
ENTRYPOINT ["standings/run.sh"]