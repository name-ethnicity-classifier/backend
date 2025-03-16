FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=/app/src

COPY . .

CMD [ "sh", "serve.sh"]