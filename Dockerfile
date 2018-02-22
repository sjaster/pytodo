FROM python:alpine

WORKDIR /pytodo

COPY ./src /pytodo

ADD requirements /pytodo

RUN pip install -r requirements

ENV FLASK_APP=/pytodo/main.py

ENV FLASK_DEBUG=0

EXPOSE 80

CMD ["flask","run","--host=0.0.0.0","--port=5001"]
