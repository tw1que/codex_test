FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies separately for better caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY . .

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
