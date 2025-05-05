FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=/app/src
ENV FLASK_APP=/app/src/app.py
ENV FLASK_ENV=production

COPY . .

CMD [ "sh", "serve.sh"]
