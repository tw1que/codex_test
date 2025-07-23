# Flask Telefoonboek Server

Dit project voorziet in een **centrale beheeromgeving** voor je Yealink XML-telefoonboeken, waardoor je eenvoudig contacten kunt toevoegen, bewerken en verwijderen via een webinterface. De gegenereerde XML conform de Yealink IP Phone Directory-specificatie serveer je rechtstreeks aan je Yealink-telefoons (W70B, T58W) als Remote Phonebook.

---

## Uitgangspunt

* **Yealink XML-structuur**: de telefoons verwachten een XML waarbij elke contact entry een `<DirectoryEntry>` is met `<Name>` en één of meer `<Telephone>` elementen.
* **Decentrale configuratie**: zonder handmatig uploaden van XML-bestanden op je provisioning-server wil je via één centrale applicatie de data beheren.
* **Synology/Docker omgeving**: de beheer-UI en XML-serve logica draait in een Docker-container (bijv. op een Synology NAS), eenvoudig te deployen via Portainer.

---

## Doel van het project

1. **Gebruiksvriendelijke UI**

   * Webpagina met overzicht van bestaande contacten.
   * Formulieren voor toevoegen en verwijderen van contacten.
   * Flash-berichten voor validatie-feedback (naam verplicht, geldig nummer).

2. **Centrale XML-uitvoer**

   * Elke wijziging in de UI schrijft direct naar één `phonebook.xml`.
   * De XML voldoet automatisch aan de Yealink-specificatie:

     ```xml
     <?xml version="1.0" encoding="UTF-8"?>
     <YealinkIPPhoneDirectory>
       <DirectoryEntry>
         <Name>...</Name>
        <Telephone>...</Telephone>
         <!-- Extra nummers -->
       </DirectoryEntry>
       <!-- Meer entries -->
     </YealinkIPPhoneDirectory>
     ```

3. **Scalability & Best Practices**

   * **App-factory** patroon (Flask) voor duidelijke configuratie.
   * **Blueprints** voor losse routes (`/`, `/add`, `/delete/<index>`).
   * **Modulaire code**: `models.py` (XML-datalayer), `utils.py` (validatie), `routes.py`.
   * **pytest-tests** voor betrouwbare add/delete-functionaliteit.
   * **Gunicorn** als WSGI-server in productie.

4. **Eenvoudige deployment**

   * **Dockerfile** aanwezig:

     ```dockerfile
     FROM python:3.11-slim
     WORKDIR /app
     COPY . /app
     RUN pip install -r requirements.txt
     EXPOSE 8080
     CMD ["gunicorn", "-b", "0.0.0.0:8080", "run:app"]
     ```
   * Deploy via Portainer of CLI op Synology NAS.

---

Met deze opzet beheer je centraal je telefoonboek, zonder handmatige XML-aanpassingen en verzekerd van een consistente, Yealink-compatibele output voor al je toestellen.
