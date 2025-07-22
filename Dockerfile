FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt \
    && apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*
EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
