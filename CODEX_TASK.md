# CODEX\_TASK.md

**Doel:** Geef Codex een vaste, complete instructie zodat wijzigingen en uitbreidingen altijd in lijn zijn met de architectuur: **centrale database als bron van waarheid**, en **Yealink XML als export/view**.

---

## Context

* Framework: Flask (app-factory), SQLAlchemy, Alembic, Python 3.11.
* Productie: Gunicorn.
* Opslag: SQLite op `/data/app.db` (makkelijk te upgraden naar Postgres).
* Platform: Docker/Portainer op Synology (persistente volumes).
* Doel: Contacten centraal beheren via UI/API. On-the-fly exports: Yealink XML, CSV, VCF (XML is niet de opslagbron).

## Definition of Done (hoog niveau)

* `docker compose up` start de app en maakt `/data/app.db` aan.
* `pytest` draait groen.
* `GET /phonebook/all.xml` retourneert valide Yealink XML, gegenereerd vanuit de DB.
* `flask import-yealink path/to/phonebook.xml` importeert zonder duplicaten (merge op `(number, display_name)`).
* UI laat toevoegen/bewerken/(soft)verwijderen zien; zoeken/filteren werkt.

---

## Te implementeren/handhaven

### 1) Datamodel (SQLAlchemy)

Bestand: `app/models.py`

* `Practice(id, name unique)`
* `Supplier(id, name unique)`
* `Contact(id, display_name, number, label?, practice_id?, supplier_id?, active bool default True, created_at, updated_at)`
* Relaties: `Contact.practice`, `Contact.supplier`
* Uniek: `UniqueConstraint(number, display_name)`
* Indexen op `display_name`, `number`

### 2) Validatie & helpers

Bestand: `app/validators.py`

* `normalize_number(s: str) -> str`

  * Strip spaties/strepen, alleen `+` en cijfers, min 3 digits.
  * Raise `ValueError` bij ongeldige invoer.

### 3) App-factory & config

Bestand: `app/__init__.py`

* `create_app()` leest env var `DB_URL` (default `sqlite:////data/app.db`).
* Registreer blueprints: UI, API, XML, health.
* Init Alembic/SQLAlchemy.

### 4) UI (beheer)

Bestand: `app/routes_ui.py` (+ bijbehorende templates/static)

* Routes: lijst/zoek/filter, create, edit, soft delete (`active=False`).
* CSRF-bescherming op POST.
* Foutafhandeling met flash-berichten.

### 5) API (JSON)

Bestand: `app/routes_api.py`

* `GET /api/contacts` → lijst; filters: `q`, `active` (true/false)
* `POST /api/contacts` → create (validatie + normalisatie)
* `PUT /api/contacts/<id>` → update
* `DELETE /api/contacts/<id>` → soft delete
* Statuscodes: 200/201/204; duidelijke foutcodes 400/404

### 6) Yealink XML-exports (view)

Bestand: `app/routes_xml.py`

* `GET /phonebook/root.xml` → `<YealinkIPPhoneBook>` met `<Menu Name=".." Url=".."/>` naar subboeken.
* `GET /phonebook/all.xml` → `<YealinkIPPhoneDirectory>` met `<DirectoryEntry>`
* `GET /phonebook/practices.xml` → alleen contacten met `practice_id`
* `GET /phonebook/suppliers.xml` → alleen contacten met `supplier_id`
* Alias: `GET /phonebook.xml` → gelijk aan `all`
* Sorteer: `label NULLS FIRST`, daarna `display_name ASC`
* Headers: `Content-Type: text/xml; charset=utf-8`, `ETag`, `Last-Modified`

### 7) Import CLI

Bestand: `app/cli_import.py`

* CLI-commando: `flask import-yealink <pad-naar-xml>`
* Leest `<DirectoryEntry><Name>..</Name><Telephone>..</Telephone></DirectoryEntry>`
* Normaliseert nummers; merge op `(number, display_name)`
* Geen duplicaten toevoegen

### 8) Healthcheck

Bestand: `app/routes_health.py`

* `GET /health` → `{ "status": "ok" }`

### 9) Migrations (Alembic)

* `alembic.ini` + `migrations/` met eerste migratie
* Commands in `Makefile`: `init`, `migrate`, `upgrade`

---

## Tests (pytest)

Map: `tests/`

* `test_validators.py` → `normalize_number`
* `test_api_contacts.py` → create/update/delete, query filters, soft delete
* `test_xml_endpoints.py` → status, mimetype, root tags, sortering; `If-None-Match` → `304`
* `test_import_xml.py` → import zonder duplicaten; foutpad netjes afvangen
* `tests/fixtures/expected_all.xml` → klein voorbeeldbestand; vergelijk canonicalized XML

**Doel:** alle tests groen.

---

## Docker & Run

### Dockerfile (indicatief)

```
FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8080
CMD ["gunicorn", "-w", "3", "-b", "0.0.0.0:8080", "app:create_app()"]
```

### docker-compose.yml (indicatief)

```
services:
  phonebook:
    build: .
    image: yourrepo/phonebook:latest
    ports:
      - "8080:8080"
    environment:
      - DB_URL=sqlite:////data/app.db
      - FLASK_ENV=production
    volumes:
      - ./data:/data
    healthcheck:
      test: ["CMD", "curl", "-fsS", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Lokale commando’s (indicatief)

* `make init` → Alembic init/migrate/upgrade
* `make run` → dev server
* `pytest` → tests

---

## Coding style & kwaliteit

* PEP8 + type hints.
* Duidelijke foutmeldingen; geen stacktraces naar eindgebruiker.
* Kleine, samenhangende commits.

---

## Pull Request richtlijnen

1. Voeg een PR-beschrijving toe met: hoe draaien, hoe testen, voorbeeld-URLs.
2. Commitvolgorde (advies):

   * scaffolding (app-factory, deps, docker)
   * modellen + migratie
   * UI + validators
   * XML-exports + ETag/Last-Modified
   * import CLI
   * tests + fixtures
3. Alle tests moeten groen zijn; `docker compose up` moet werken.

---

## Notities voor uitbreidingen

* CSV/VCF export endpoints (`/export.csv`, `/export.vcf`).
* Eenvoudige auth/token voor XML-views of IP-allowlist.
* Overstap naar Postgres: alleen `DB_URL` wijzigen + nieuwe migratie.

> **Belangrijk:** XML is een **exportlaag**. De **database** is de enige bron van waarheid. Alle features moeten deze scheiding expliciet respecteren.
