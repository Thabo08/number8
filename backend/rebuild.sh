#!/bin/sh
docker rm -f standings
docker image rm -f standings:latest
docker build -t standings:latest .
docker compose up -d