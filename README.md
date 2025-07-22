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

Bezoek `http://localhost:8080` voor een lijst van contacten. Gebruik de knop **Nieuwe contact** om een contact toe te voegen. Elk contact heeft een naam, nummer en optioneel label. Bestaande contacten kun je via de link **Bewerk** aanpassen. Wijzigingen worden direct opgeslagen in `phonebook.xml`.

## Docker Deployment

De meegeleverde `Dockerfile` bouwt een image dat via Gunicorn op poort 8080 draait. Build en start bijvoorbeeld met:

```bash
docker build -t phonebook .
docker run -p 8080:8080 phonebook
```

Dit is gemakkelijk te deployen via Portainer of de CLI op een Synology NAS.

## Hosting op Synology via Portainer

Onderstaande stappen beschrijven hoe je de applicatie op een Synology NAS kunt hosten met behulp van Portainer.

1. **Installeer Docker**
   - Open het *Package Center* in DSM en installeer het pakket **Docker**.

2. **Installeer Portainer**
   - Start de Docker-applicatie en ga naar **Registry**.
   - Zoek naar `portainer/portainer-ce` en download de nieuwste versie.
   - Kies daarna **Launch** om een nieuwe container aan te maken.
   - Geef de container een naam (bijv. `portainer`), publiceer poort `9000` en koppel twee volumes:
     - `/var/run/docker.sock` &rarr; `/var/run/docker.sock`
     - `/volume1/docker/portainer_data` &rarr; `/data`
   - Na het starten is Portainer bereikbaar via `http://<NAS-IP>:9000` en kun je een admin-account aanmaken.

3. **Bouw de phonebook-image**
   - In Portainer kies je **Images** &rarr; **Build a new image**.
   - Upload het project (bijvoorbeeld als zip) en geef als *Tag* `phonebook` op.
   - Na het bouwen staat er een image `phonebook:latest` klaar.

4. **Maak een map voor het telefoonboek**
   - Maak op de NAS een map aan, bijvoorbeeld `/volume1/docker/phonebook`, waarin `phonebook.xml` bewaard kan worden.

5. **Start de container**
   - Ga in Portainer naar **Containers** en kies **Add container**.
   - Vul in:
     - **Name**: `phonebook`
     - **Image**: `phonebook:latest`
     - **Restart policy**: `always`
     - **Publish a new network port**: host `8080` &rarr; container `8080`
     - **Volumes**: bind `/volume1/docker/phonebook/phonebook.xml` aan `/app/phonebook.xml`
   - Klik **Deploy container** om de applicatie te starten.

6. **Gebruik**
   - Bezoek `http://<NAS-IP>:8080` om contacten te beheren. Alle wijzigingen worden opgeslagen in de eerder aangemaakte map.

## Tests

Pytest-tests controleren de logica voor het toevoegen en verwijderen van contacten.

```bash
pytest
```
