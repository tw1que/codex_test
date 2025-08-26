.PHONY: up down logs fmt lint backend-migrate backend-seed test

up:
	docker compose up -d --build

down:
	docker compose down -v

logs:
	docker compose logs -f --tail=200

backend-migrate:
	docker compose exec backend alembic -c /app/alembic.ini upgrade head

backend-seed:
	docker compose exec backend python -m app.scripts.seed

fmt:
	ruff check backend --fix || true
	black backend || true
	oneslint --fix frontend || true

lint:
	ruff check backend
	mypy backend
	npx tsc -p frontend

test:
	pip install -r requirements.txt
	python -m pytest
