FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV FLASK_APP=/app/src/app.py
ENV FLASK_RUN_PORT=8080

COPY . .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]