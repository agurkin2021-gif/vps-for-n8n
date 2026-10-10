#!/usr/bin/env python3
"""Conservative native-Dutch editorial polish; preserves HTML structure and technical values."""
from pathlib import Path
import sys
from _nl_translate_full import PAGES,ROOT,validate

GLOBAL=[
 ("werknemers","workers"),("Werknemers","Workers"),
 ("werknemer","worker"),("Werknemer","Worker"),
 ("wachtrijmodus","Queue Mode"),("Wachtrijmodus","Queue Mode"),
 ("omgekeerde proxy","reverse proxy"),("Omgekeerde proxy","Reverse proxy"),
 ("Docker Componeren","Docker Compose"),
 ("knooppunten","nodes"),("Knooppunten","Nodes"),
 ("knooppunt","node"),("Knooppunt","Node"),
 ("coderingssleutel","encryptiesleutel"),("Coderingssleutel","Encryptiesleutel"),
 ("Encryptie sleutel","Encryptiesleutel"),
 ("eindpunt","endpoint"),("Eindpunt","Endpoint"),
 ("stapel","stack"),("Stapel","Stack"),
 ("zelfgehost","self-hosted"),("Zelfgehost","Self-Hosted"),
 ("zelf-gehost","self-hosted"),("Zelf-gehost","Self-Hosted"),
 ("Wolk","Cloud"),
 ("lading","payload"),("Lading","Payload"),
]

PER_PAGE={
"nl/index.html":[
 ("VPS voor n8n vanaf $0.07/Day - Plannen- en maatgids","VPS voor n8n vanaf $0.07/Day — Plannen en sizing-gids"),
 ("CRM, leads en online winkelworkflows","CRM, leads en e-commerceworkflows"),
 ("Invoer, documenten &amp; zwaardere klussen","Imports, documenten &amp; zwaardere taken"),
 ("Bereid de aanvraag voor","Bereid de applicatie voor"),
 ("Kies uw eigen VPS voor bediening","Kies uw eigen VPS voor maximale controle"),
 ("Kies Cloud voor beheerde hosting","Kies n8n Cloud voor beheerde hosting"),
 ("Waar u op moet letten in een n8n VPS","Waar u op moet letten bij een VPS voor n8n"),
 ("Begin met één exemplaar. Voeg werknemers toe wanneer dat nodig is.","Begin met één instantie. Voeg workers toe wanneer dat nodig is."),
 ("Maak uw n8n opstelling gereed voor dagelijks werk","Maak uw n8n-setup klaar voor dagelijks gebruik"),
 ("Verbind een veilig eindpunt","Verbind een beveiligd endpoint"),
 ("Voor groeiende uitvoeringsgeschiedenis","Voor een groeiende uitvoeringsgeschiedenis"),
 ("Voor overlappende uitbarstingen","Voor overlappende piekbelastingen"),
 ("Waar u voor betaalt als u zelf host n8n","Waar u voor betaalt bij self-hosting van n8n"),
 ("Schat in wat uw n8n VPS maand daadwerkelijk gaat kosten","Schat de werkelijke maandelijkse kosten van uw n8n-VPS"),
 ("Ga verder met de taak die u nodig hebt","Ga verder met wat u wilt doen"),
 ("Implementeren n8n","n8n implementeren"),
 ("Wachtrijmodus en werknemers","Queue Mode en workers"),
 ("Bronnen achter de aanbevelingen","Bronnen waarop de aanbevelingen zijn gebaseerd"),
],
"nl/beste-vps-voor-n8n.html":[
 ("Beste VPS voor n8n in 2026: 6 Providers vergeleken","Beste VPS voor n8n in 2026: vergelijking van 6 providers"),
 ("Vergelijk n8n VPS aanbieders in één oogopslag","Vergelijk VPS-providers voor n8n in één oogopslag"),
 ("De criteria die een goede n8n VPS onderscheiden van een slechte fit","Criteria die een goede VPS voor n8n onderscheiden van een slechte match"),
 ("Instellingspad","Installatiepad"),
 ("Ondersteuning grens","Grenzen van support"),
 ("Schaalpad","Schaalpad"),
 ("Verlenging en extra's","Verlenging en extra kosten"),
 ("Ik wil een start met de laagste wrijving","Ik wil de eenvoudigste start"),
 ("Ik verwacht later de wachtrijmodus","Ik verwacht later Queue Mode te gebruiken"),
 ("Het gaat mij het meeste om migratie","Migratie is mijn hoogste prioriteit"),
 ("De keuze van de provider is niet de grootte van de server","Providerkeuze en server-sizing zijn twee verschillende beslissingen"),
 ("Ga verder bij besluit","Ga verder met uw keuze"),
],
"nl/over-ons.html":[
 ("Over | n8nVPS","Over ons | n8nVPS"),
 ("Over n8nVPS","Over n8nVPS"),
 ("Redactionele reikwijdte","Redactionele scope"),
],
"nl/n8n-backup-herstel.html":[
 ("n8n Back-up en herstel","Back-up en herstel van n8n"),
 ("Encryptie sleutel","Encryptiesleutel"),
 ("Workflow en referentie-export","Export van workflows en credentials"),
 ("Entiteit exporteren","Entiteitsexport"),
 ("Volledig exemplaarherstel","Volledig instantieherstel"),
 ("Momentopname van de provider","Snapshot van de provider"),
 ("De coderingssleutel maakt deel uit van het herstel","De encryptiesleutel maakt deel uit van het herstel"),
 ("Een back-up is pas bewezen als de restauratie slaagt","Een back-up is pas betrouwbaar nadat herstel succesvol is getest"),
 ("Weet precies welke workflow- en referentie-exports niet worden hersteld","Weet precies wat workflow- en credential-exports niet herstellen"),
 ("CLI-exports vormen geen volledige back-up van het exemplaar","CLI-exports vormen geen volledige back-up van de instantie"),
 ("Herstel van nieuwe exemplaren heeft een eigenaar nodig","Herstel naar een nieuwe instantie vereist een eigenaar"),
 ("Zoek de originele coderingssleutel voordat u deze opnieuw opbouwt","Zoek de originele encryptiesleutel voordat u opnieuw opbouwt"),
],
"nl/contact.html":[
 ("Contactstatus","Contactinformatie"),
],
"nl/n8n-installeren-vps-docker.html":[
 ("Bereid de VPS voor voordat u met n8n begint","Bereid de VPS voor voordat u n8n installeert"),
 ("Docker Componeren","Docker Compose"),
 ("1. Docker, DNS voorbereiden en openen","1. Bereid Docker, DNS en toegang voor"),
 ("2. Creëer omgevingswaarden en behoud de sleutel","2. Stel omgevingsvariabelen in en bewaar de sleutel"),
 ("4. Maak het HTTPS Caddybestand aan","4. Maak het HTTPS-Caddyfile aan"),
 ("Stel bewust geheimen en openbare URL's in","Stel secrets en openbare URL's bewust in"),
 ("PostgreSQL-gegevens","PostgreSQL-credentials"),
 ("Openbare hostnaam","Publieke hostname"),
 ("n8n en PostgreSQL afzonderlijk aanhouden","Houd n8n- en PostgreSQL-data persistent en gescheiden"),
 ("n8n gegevens","n8n-data"),
 ("PostgreSQL gegevens","PostgreSQL-data"),
 ("File permissions","Bestandsrechten"),
 ("Verbind n8n met de privédatabaseservice","Verbind n8n met de private databaseservice"),
 ("Zet de openbare n8n URL achter HTTPS","Plaats de publieke n8n-URL achter HTTPS"),
 ("Gebrek aan doorzettingsvermogen","Ontbrekende persistentie"),
 ("Controleer het n8n gezondheidseindpunt","Controleer het n8n health-endpoint"),
 ("Stoot PostgreSQL hoofdversies niet op hun plaats","Upgrade PostgreSQL-hoofdversies niet in-place"),
],
"nl/n8n-cloud-vs-self-hosted.html":[
 ("n8n Cloud versus zelfgehost: kosten en controle","n8n Cloud vs Self-Hosted: kosten en controle"),
 ("n8n Cloud versus zelfgehost","n8n Cloud vs Self-Hosted"),
 ("Kies wanneer zelf-gehost VPS","Kies een self-hosted VPS wanneer"),
 ("n8n Cloud versus zelfgehost VPS: vergelijkingstabel","n8n Cloud vs self-hosted VPS: vergelijkingstabel"),
 ("Hoe een eenvoudig schema gebruik kan maken van een clouduitvoeringsvergoeding","Hoe een eenvoudig schema uw Cloud-uitvoeringsquotum kan gebruiken"),
 ("Eén klik n8n VPS is niet altijd een beheerde dienst","Een n8n-VPS met one-click installatie is niet altijd een managed service"),
 ("Voorbeeld: wat kost een zelfgehoste n8n maand eigenlijk?","Voorbeeld: wat kost een maand self-hosted n8n werkelijk?"),
 ("Kies op basis van wie eigenaar is van het operationele werk","Kies op basis van wie het operationele werk beheert"),
 ("Wat je op je neemt als je zelf host","Welke verantwoordelijkheden u op zich neemt bij self-hosting"),
 ("Cloudgemak versus zelfgehoste schaalcontrole","Cloudgemak vs schaalcontrole bij self-hosting"),
 ("Enkel VPS","Eén VPS"),
 ("Wachtrijmodus","Queue Mode"),
 ("Zelf-gehoste community","Community Self-Hosted"),
 ("Zelf-gehost bedrijf/onderneming","Business/Enterprise Self-Hosted"),
 ("n8n Cloud versus zelfgehost: veelgestelde vragen","n8n Cloud vs Self-Hosted: veelgestelde vragen"),
 ("Voor een door uzelf gehoste VPS","Voor een self-hosted VPS"),
],
"nl/n8n-vps-vereisten.html":[
 ("n8n VPS Vereisten","VPS-vereisten voor n8n"),
 ("Lichte, altijd-aan-instantie","Lichte, altijd actieve instantie"),
 ("Grootte van de lading","Payloadgrootte"),
 ("CPU-zware knooppunten","CPU-intensieve nodes"),
 ("Schat n8n opslag van de uitvoeringsgeschiedenis voordat u bestelt","Schat de opslag voor n8n-uitvoeringsgeschiedenis voordat u bestelt"),
 ("Docker &amp; Componeren","Docker &amp; Compose"),
 ("Een 1 GB-invoer VPS gebruiken","Een VPS met 1 GB RAM gebruiken"),
 ("n8n VPS vereisten: veelgestelde vragen","VPS-vereisten voor n8n: veelgestelde vragen"),
],
"nl/privacy.html":[],
"nl/n8n-vps-beveiliging.html":[
 ("Veilig n8n op een VPS","n8n beveiligen op een VPS"),
 ("Minimale beveiligingsbasislijn vóór blootstelling aan het publiek","Minimale beveiligingsbaseline vóór publieke blootstelling"),
 ("Verharden SSH","SSH hardening"),
 ("TLS beëindiging","TLS-terminatie"),
 ("Bescherm de coderingssleutel en de referentiegrens","Bescherm de encryptiesleutel en de credential-scope"),
 ("Encryptie sleutel","Encryptiesleutel"),
 ("Milieugeheimen","Omgevingssecrets"),
 ("Referentiebereik","Credential-scope"),
 ("Knooppunten kunnen de beveiligingsgrens uitbreiden","Nodes kunnen de beveiligingsgrens uitbreiden"),
 ("Beveiliging is een operationeel proces","Beveiliging is een continu operationeel proces"),
 ("Bereid terugdraaien en herstel voor","Bereid rollback en herstel voor"),
 ("Beveilig de stapel voordat u de productieworkflows activeert","Beveilig de stack voordat u productieworkflows activeert"),
 ("Maak bewust gebruik van SSRF en geheime controles","Gebruik SSRF- en secret-controls bewust"),
 ("n8n VPS beveiliging: veelgestelde vragen","VPS-beveiliging voor n8n: veelgestelde vragen"),
],
"nl/n8n-queue-mode.html":[
 ("n8n Wachtrijmodus","n8n Queue Mode"),
 ("Heb je eigenlijk de wachtrijmodus nodig?","Hebt u Queue Mode echt nodig?"),
 ("Blijf in de normale modus wanneer","Blijf in de normale modus wanneer"),
 ("Overweeg de wachtrijmodus wanneer","Overweeg Queue Mode wanneer"),
 ("Hoe de wachtrijmodus n8n werkt","Hoe Queue Mode in n8n werkt"),
 ("Wat elke implementatie in wachtrijmodus nodig heeft","Wat elke Queue Mode-deployment nodig heeft"),
 ("Capaciteit van werknemers","Worker-capaciteit"),
 ("Werknemers schalen zowel op aantal als op basis van banen per werknemer","Schaal met het aantal workers en concurrency per worker"),
 ("Voeg werknemers toe wanneer","Voeg workers toe wanneer"),
 ("Bekijk PostgreSQL","Monitor PostgreSQL"),
 ("De wachtrijmodus kan latentie voor uitvoeringsoverdracht toevoegen","Queue Mode kan latency toevoegen aan execution handoff"),
 ("Plan voordat u werknemers distribueert","Plan voordat u workers distribueert"),
 ("Weet of de wachtrij helpt","Meet of Queue Mode daadwerkelijk helpt"),
 ("Diepte van wachtrij","Queue depth"),
 ("Werknemer CPU &amp; RAM","CPU &amp; RAM per worker"),
 ("Gezondheidscontroles","Health checks"),
 ("Schaal één knelpunt tegelijk","Schaal één bottleneck tegelijk"),
 ("De wachtrijmodus schaalt uitvoeringen, maar zorgt er niet automatisch voor dat het hoofdproces maximaal beschikbaar is","Queue Mode schaalt executies, maar maakt het hoofdproces niet automatisch high-availability"),
 ("n8n wachtrijmodus: veelgestelde vragen","n8n Queue Mode: veelgestelde vragen"),
],
}

def polish(i):
    en,target=PAGES[i]
    p=ROOT/target
    text=p.read_text(encoding="utf-8")
    before=text;hits=0
    for old,new in PER_PAGE.get(target,[]):
        n=text.count(old)
        if n:
            text=text.replace(old,new);hits+=n
    for old,new in GLOBAL:
        n=text.count(old)
        if n:
            text=text.replace(old,new);hits+=n
    validate((ROOT/en).read_text(encoding="utf-8"),text,en,target)
    if text!=before:
        p.write_text(text,encoding="utf-8")
    print("DUTCH_NATIVE_POLISH",i+1,"/11",target,"replacements",hits,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _nl_native_polish.py PAGE_INDEX")
    i=int(sys.argv[1])
    if not 0<=i<len(PAGES):
        raise SystemExit("Page out of range")
    polish(i)
