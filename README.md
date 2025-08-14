# Yealink Phonebook Server

Deze applicatie biedt een webinterface om een Yealink telefoonboek te beheren. De SQLite-database is de enige bron van waarheid; hieruit worden Yealink XML-bestanden, CSV en VCF on‑demand gegenereerd. De gebruikersinterface is opgezet met **Tailwind CSS** voor een moderne uitstraling zonder extra build-stap.

## Installatie

1. Installeer de vereisten.

```bash
pip install -r requirements.txt
```

2. Start de applicatie lokaal.

```bash
python run.py
```

## Gebruik

Bezoek `http://localhost:8080` voor een lijst van contacten. Gebruik de knop **Nieuwe contact** om een contact toe te voegen. Elk contact heeft een naam en nummer. Bestaande contacten kun je via de link **Bewerk** aanpassen. Wijzigingen worden direct in de database opgeslagen en de XML-exports worden automatisch hieruit gegenereerd.

Via de knop **Importeer CSV** kun je meerdere contacten ineens toevoegen. Upload een CSV-bestand met kolommen `name` en `telephone`. Alleen rijen met geldige waarden worden toegevoegd. Elk contact kan een categorie hebben: `practice`, `supplier` of `other`.

### JSON API

Een simpele JSON API is beschikbaar onder `/api/contacts`:

* `GET /api/contacts` – lijst van contacten gesorteerd op naam
* `POST /api/contacts` – maak een nieuw contact (`name`, `telephone`, optioneel `category`)
* `PUT /api/contacts/{id}` – update bestaand contact
* `DELETE /api/contacts/{id}` – verwijder contact

### Export

Naast de Yealink XML is er export naar CSV en VCF:

* `GET /export/contacts.csv`
* `GET /export/contacts.vcf`

## Docker Deployment

Gebruik de meegeleverde `docker-compose.yml` om de database te bewaren op een volume en een Python-based healthcheck te gebruiken:

```bash
docker compose up --build
```

De compose-file mount `./data` als volume zodat `phonebook.db` bewaard blijft tussen container herstarts. Voor een eenmalige import kan een legacy Yealink XML worden gemount en het pad via `INITIAL_PHONEBOOK_XML` worden doorgegeven.

## Tests


De makkelijkste manier om de test-suite uit te voeren is via de Makefile:

```bash
make test
```

Dit commando installeert automatisch de vereisten uit `requirements.txt` en draait daarna alle tests.

Je kunt de stappen ook handmatig uitvoeren:

```bash
pip install -r requirements.txt
python -m pytest
```

## Licentie

Deze software is beschikbaar onder de MIT-licentie. Zie [LICENSE](LICENSE) voor details.
