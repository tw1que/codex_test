# Flask Telefoonboek Server – Nieuwe versie

Dit project richt zich op één centrale **bron van waarheid** voor al je contacten, met als extra functie het on-the-fly serveren van Yealink XML-phonebooks. Hierdoor blijft het contactbeheer flexibel en toekomstbestendig, en is de XML-uitvoer slechts een van de mogelijke exportvormen.

---

## Uitgangspunt

* **Centrale database**: alle contacten worden opgeslagen in een relationele database (SQLite voor simpel gebruik; uitbreidbaar naar PostgreSQL/MySQL).
* **Meerdere weergaven/exports**: naast de beheer-UI zijn er endpoints die XML (Yealink), CSV en VCF genereren vanuit dezelfde data.
* **Synology/Docker omgeving**: de hele app draait in een container, eenvoudig te deployen via Portainer, met persistente opslag voor de database.

---

## Doel van het project

1. **Gebruiksvriendelijke UI**

   * Overzichtspagina met zoek- en filteropties.
   * Formulieren voor toevoegen, bewerken, (soft) verwijderen van contacten.
   * Validatie op naam en telefoonnummer (formaat, duplicaten).
   * Groepering per praktijk, leverancier of andere categorie.

2. **Centrale database & API**

   * SQLAlchemy-modellen voor contacten, praktijken, leveranciers.
   * REST API voor CRUD-operaties op contacten.
   * Importfunctie vanuit bestaande XML- of CSV-bestanden.
   * Export naar Yealink XML, CSV en VCF.

3. **Yealink XML-uitvoer**

   * Endpoints als `/phonebook/root.xml`, `/phonebook/all.xml`, `/phonebook/practices.xml`, `/phonebook/suppliers.xml`.
   * Root-XML biedt menu-links naar sub-phonebooks.
   * XML voldoet aan Yealink-specificatie:

     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <YealinkIPPhoneDirectory>
       <DirectoryEntry>
         <Name>...</Name>
         <Telephone>...</Telephone>
       </DirectoryEntry>
     </YealinkIPPhoneDirectory>
     ```

4. **Architectuur & Best Practices**

   * **App-factory** patroon voor configureerbare deployment.
   * **Blueprints** voor UI-routes, API-routes en export-routes.
   * **Validators** voor telefoonnummerformaat en naam.
   * **pytest-tests** voor model- en endpoint-functionaliteit.
   * **ETag/Last-Modified** headers voor efficiënte XML-cache op telefoons.

5. **Eenvoudige deployment**

   * **Dockerfile** en `docker-compose.yml` aanwezig.
   * Persistente volume voor `/data/app.db`.
   * Healthcheck endpoint (`/health`).
   * Gunicorn als WSGI-server.

---

Met deze opzet heb je één centrale, uitbreidbare database voor al je contacten, en kan je eenvoudig meerdere uitvoerformaten aanbieden, waarbij Yealink XML slechts een van de opties is.
