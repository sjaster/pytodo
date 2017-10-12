FROM python:3.6

WORKDIR /pytodo

ADD requirements /pytodo

RUN pip install -r requirements

EXPOSE 80

CMD python main.py