# Yealink Phonebook Server

This project provides a web interface to manage a Yealink phonebook. The database is the source of truth; Yealink XML, CSV and VCF files are generated on demand.

## Contents
- [Quickstart](#quickstart)
- [Environment variables](#environment-variables)
- [Local development](#local-development)
- [Keycloak quickstart (local, dev-only)](#keycloak-quickstart-local-dev-only)
- [Synology Portainer](#synology-portainer)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [License](#license)

## Quickstart

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Start the services:

```bash
make up
```

3. Run database migrations:

```bash
make backend-migrate
```

4. Open <http://localhost:3000> in your browser.

## Environment variables

| Key | Example | Description |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://inventory:inventory@db:5432/inventory` | SQLAlchemy URL |
| `BACKEND_PORT` | `8000` | Uvicorn port |
| `FRONTEND_PORT` | `3000` | Next dev/serve port |
| `KEYCLOAK_URL` | `http://localhost:8080` | Auth server base URL |
| `KEYCLOAK_REALM` | `such-empty` | Realm name |
| `KEYCLOAK_CLIENT_ID` | `frontend` | OIDC client ID |
| `KEYCLOAK_CLIENT_SECRET` | `changeme` | OIDC secret (if confidential) |

## Local development

Common `make` targets:

```
make up              # start docker compose stack
make down            # stop stack and remove volumes
make logs            # tail container logs
make backend-migrate # apply database migrations
make backend-seed    # load demo data
make fmt             # auto-format code
make lint            # run linters
```

## Keycloak quickstart (local, dev-only)

1. Start a dev Keycloak instance:

```bash
docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:26.0 start-dev
```

2. Create realm `such-empty`, client `frontend` (public) and add redirect `http://localhost:3000/*`.
3. Create a user, set a password and assign default roles.
4. Update `.env` with these values and restart the stack.

## Synology Portainer

For Synology deployment, use `infra/portainer/stack.yml`. Place your `.env` file in `/volume1/docker/such_empty/.env` and bind a volume for Postgres under `/volume1/docker/such_empty/db`.

## Troubleshooting

- **Healthcheck failures:** run `docker compose ps` to inspect container health.
- **Port collisions:** ensure ports 3000, 8000 and 8080 are free.
- **Alembic migrations:** always run `make backend-migrate` after model changes.

## Testing

```bash
make test
```

## License

MIT
