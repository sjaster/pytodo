FROM python:3.6

WORKDIR /pytodo

ADD requirements /pytodo

RUN pip install -r requirements

ENV FLASK_APP=main.py

ENV FLASK_DEBUG=1

EXPOSE 80
