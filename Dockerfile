FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV PYTHONPATH=/app/src
ENV FLASK_APP=/app/src/app.py
ENV FLASK_ENV=production

COPY . .

CMD ["gunicorn", "-w", "8", "-b", "0.0.0.0:8080", "src.app:app"]