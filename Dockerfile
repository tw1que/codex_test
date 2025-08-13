FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed for health checks.
# See TODO.md: Evaluate lighter health-check tooling to avoid installing curl in production images.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies separately for better caching.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source.
COPY . .

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
