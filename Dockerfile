FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libgomp1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

COPY . .

ENV PYTHONPATH=/app/src
ENV FLASK_APP=/app/src/app.py
ENV FLASK_ENV=production

COPY . .

CMD [ "sh", "serve.sh"]
