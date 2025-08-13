# Yealink Phonebook Server

Deze applicatie biedt een webinterface om een Yealink telefoonboek te beheren. Contacten kunnen worden toegevoegd of verwijderd via de browser en worden opgeslagen in `phonebook.xml` in het Yealink-formaat. De gebruikersinterface is opgezet met **Tailwind CSS** voor een moderne uitstraling zonder extra build-stap.

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

Bezoek `http://localhost:8080` voor een lijst van contacten. Gebruik de knop **Nieuwe contact** om een contact toe te voegen. Elk contact heeft een naam en nummer. Bestaande contacten kun je via de link **Bewerk** aanpassen. Wijzigingen worden direct opgeslagen in `phonebook.xml`.

Via de knop **Importeer CSV** kun je meerdere contacten ineens toevoegen. Upload
een CSV-bestand met kolommen `name` en `telephone`. Alleen rijen met geldige waarden worden toegevoegd.

## Docker Deployment

De meegeleverde `Dockerfile` bouwt een image dat via Gunicorn op poort 8080 draait. Build en start bijvoorbeeld met:

```bash
docker build -t phonebook .
docker run -p 8080:8080 phonebook
```

Dit is gemakkelijk te deployen via Portainer of de CLI op een Synology NAS.

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
