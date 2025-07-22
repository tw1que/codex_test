# Yealink Phonebook Server

Deze applicatie biedt een webinterface om een Yealink telefoonboek te beheren. Contacten kunnen worden toegevoegd of verwijderd via de browser en worden opgeslagen in `phonebook.xml` in het Yealink-formaat.

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

Bezoek `http://localhost:8080` voor een lijst van contacten. Gebruik de knop **Nieuwe contact** om een contact toe te voegen. Elk contact heeft een naam, nummer en optioneel label. Wijzigingen worden direct opgeslagen in `phonebook.xml`.

## Docker deployment

De meegeleverde `Dockerfile` bouwt een image dat via Gunicorn op poort 8080 draait. Build en start bijvoorbeeld met:

```bash
docker build -t phonebook .
docker run -p 8080:8080 phonebook
```

Dit is gemakkelijk te deployen via Portainer of de CLI op een Synology NAS.

## Tests

Pytest-tests controleren de logica voor het toevoegen en verwijderen van contacten.

```bash
pytest
```
