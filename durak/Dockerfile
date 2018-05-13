FROM python:3.6.5-alpine

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT python3 start.py mitm 0.0.0.0 10770 148.251.13.130 10770
