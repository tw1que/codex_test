#!/usr/bin/env bash
set -euo pipefail

# --- Backend (Python) ---
if [ -d "backend" ]; then
  cd backend
  python -m pip install --upgrade pip
  if [ -f "pyproject.toml" ]; then
    pip install -e ".[dev]" || pip install -e .
  elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
  else
    pip install fastapi uvicorn[standard] "SQLAlchemy>=2" alembic psycopg[binary] pydantic pytest
  fi
  cd -
fi

# --- Frontend (Node) ---
if [ -d "frontend" ]; then
  cd frontend
  if [ -f "package-lock.json" ]; then
    npm ci
  elif [ -f "package.json" ]; then
    npm install
  fi
  cd -
fi

echo "✅ Dev container setup complete."
