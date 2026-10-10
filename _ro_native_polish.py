#!/usr/bin/env python3
"""Conservative native-Romanian editorial polish; preserves HTML structure and technical values."""
from pathlib import Path
import re,sys
from _ro_translate_full import PAGES,ROOT,validate

GLOBAL=[
 ("Docker Compune","Docker Compose"),
 ("modul coadă","Queue Mode"),("Modul coadă","Queue Mode"),("Mod coadă","Queue Mode"),
 ("lucrătorii","workerii"),("Lucrătorii","Workerii"),
 ("lucrătorilor","workerilor"),("Lucrătorilor","Workerilor"),
 ("lucrătorului","workerului"),("Lucrătorului","Workerului"),
 ("lucrători","workeri"),("Lucrători","Workeri"),
 ("lucrător","worker"),("Lucrător","Worker"),
 ("muncitorii","workerii"),("Muncitorii","Workerii"),
 ("muncitori","workeri"),("Muncitori","Workeri"),
 ("muncitor","worker"),("Muncitor","Worker"),
 ("sarcinii utile","payloadului"),("Sarcinii utile","Payloadului"),
 ("sarcină utilă","payload"),("Sarcină utilă","Payload"),
 ("sarcini utile","payload-uri"),("Sarcini utile","Payload-uri"),
 ("locuri de muncă","joburi"),("Locuri de muncă","Joburi"),
 ("punctul final","endpoint-ul"),("Punctul final","Endpoint-ul"),
 ("punct final","endpoint"),("Punct final","Endpoint"),
 ("stiva","stack-ul"),("Stiva","Stack-ul"),
 ("stivă","stack"),("Stivă","Stack"),
 ("recipientele","containerele"),("Recipientele","Containerele"),
 ("recipient","container"),("Recipient","Container"),
 ("Nume de gazdă","Hostname"),("nume de gazdă","hostname"),
 ("auto-găzduit","self-hosted"),("Auto-găzduit","Self-hosted"),
 ("auto-găzduită","self-hosted"),("Auto-găzduită","Self-hosted"),
 ("auto-găzduirea","self-hosting"),("Auto-găzduirea","Self-hosting"),
 ("autogăzduiți","faceți self-hosting"),("Autogăzduiți","Faceți self-hosting"),
 ("indemnizație de execuție","cotă de execuții"),("Indemnizație de execuție","Cotă de execuții"),
 ("indemnizații de execuție","cote de execuții"),("Indemnizații de execuție","Cote de execuții"),
 ("Single VPS","Un singur VPS"),
]

PER_PAGE={
"ro/index.html":[
 ("VPS pentru n8n din $0.07/Day - Ghid pentru planuri și dimensiuni","VPS pentru n8n de la $0.07/zi — Planuri și ghid de dimensionare"),
 ("Care VPS se potrivește sarcinii dvs. de lucru n8n?","Ce VPS se potrivește volumului dvs. de lucru n8n?"),
 ("Mici automatizări și fluxuri de lucru mereu activate","Automatizări mici și workflow-uri mereu active"),
 ("Fluxuri de lucru CRM, clienți potențiali și magazine online","Workflow-uri pentru CRM, lead-uri și magazine online"),
 ("Importuri, documente și locuri de muncă mai grele","Importuri, documente și joburi mai solicitante"),
 ("Transformați configurația într-o ordine VPS","Transformați configurația într-o comandă VPS"),
 ("Alegeți configurația dvs. Linux","Alegeți configurația Linux"),
 ("Conectați-vă automatizările","Conectați automatizările"),
 ("Alege-ți propriul VPS pentru control","Alegeți propriul VPS pentru control"),
 ("Alegeți Cloud pentru găzduire gestionată","Alegeți n8n Cloud pentru găzduire gestionată"),
 ("Ce să cauți într-un n8n VPS","Ce trebuie urmărit la un VPS pentru n8n"),
 ("Începeți cu o singură instanță. Adăugați lucrători atunci când este necesar.","Începeți cu o singură instanță. Adăugați workeri când este necesar."),
 ("Pregătește-ți configurația n8n pentru munca zilnică","Pregătiți configurația n8n pentru utilizarea zilnică"),
 ("Conectați un punct final securizat","Conectați un endpoint securizat"),
 ("Programează întreținerea","Programați mentenanța"),
 ("Mai multe RAM, mai multe CPU sau o modificare a fluxului de lucru?","Mai mult RAM, mai mult CPU sau o modificare a workflow-ului?"),
 ("Pentru explozii suprapuse","Pentru vârfuri de sarcină suprapuse"),
 ("Pentru ce plătiți când vă autogăzduiți n8n","Pentru ce plătiți când faceți self-hosting pentru n8n"),
 ("Estimați cât va costa de fapt luna dvs. n8n VPS","Estimați costul lunar real al VPS-ului pentru n8n"),
 ("Implementează n8n","Implementați n8n"),
 ("Securitatea producției","Securitate pentru producție"),
 ("Modul coadă și lucrători","Queue Mode și workeri"),
 ("Resurse din spatele recomandărilor","Sursele care stau la baza recomandărilor"),
],
"ro/cel-mai-bun-vps-pentru-n8n.html":[
 ("Cel mai bun VPS pentru n8n în 2026: 6 Furnizori comparați","Cel mai bun VPS pentru n8n în 2026: comparație între 6 furnizori"),
 ("Comparați furnizorii n8n VPS dintr-o privire","Comparați rapid furnizorii VPS pentru n8n"),
 ("Criteriile care separă un n8n VPS bun de o potrivire proastă","Criteriile care diferențiază un VPS bun pentru n8n de o alegere nepotrivită"),
 ("Configurați calea","Metoda de configurare"),
 ("Limită de sprijin","Limitele suportului"),
 ("Reînnoire și extra","Reînnoire și costuri suplimentare"),
 ("Vreau pornirea cu cea mai mică frecare","Vreau cea mai simplă pornire"),
 ("Mă aștept la modul coadă mai târziu","Plănuiesc să folosesc Queue Mode mai târziu"),
 ("Cel mai mult îmi pasă de migrație","Migrarea este prioritatea mea principală"),
 ("Alegerea furnizorului nu este dimensionarea serverului","Alegerea furnizorului și dimensionarea serverului sunt decizii diferite"),
 ("Cum a fost construită această listă scurtă","Cum a fost alcătuită această selecție"),
 ("Continuați prin decizie","Continuați în funcție de decizie"),
],
"ro/despre.html":[
 ("Domeniul editorial","Domeniul editorial"),
],
"ro/backup-restaurare-n8n.html":[
 ("n8n Copiere de rezervă și restaurare","Backup și restaurare n8n"),
 ("Ce ar trebui să protejeze o copie de rezervă n8n","Ce trebuie să protejeze un backup n8n"),
 ("Flux de lucru și export de acreditări","Export de workflow-uri și acreditări"),
 ("Export de entitate","Export de entități"),
 ("Instantaneu furnizor","Snapshot al furnizorului"),
 ("Faceți o copie de rezervă a bazei de date în mod constant","Faceți backup consistent bazei de date"),
 ("Este posibil ca backupul bazei de date să nu acopere fiecare dependență de flux de lucru","Backupul bazei de date poate să nu acopere toate dependențele workflow-urilor"),
 ("O copie de rezervă pe același VPS este doar o copie locală","Un backup pe același VPS este doar o copie locală"),
 ("O copie de rezervă nu este dovedită până când restaurarea are succes","Un backup nu este verificat până când restaurarea nu reușește"),
 ("Aflați exact ce flux de lucru și exporturile de acreditări nu se restaurează","Aflați exact ce nu restaurează exporturile de workflow-uri și acreditări"),
 ("Exporturile CLI nu sunt o copie de rezervă completă a instanței","Exporturile CLI nu reprezintă un backup complet al instanței"),
 ("Restaurarea în instanță proaspătă necesită un proprietar","Restaurarea pe o instanță nouă necesită configurarea proprietarului"),
 ("n8n backup și restaurare: întrebări frecvente","Backup și restaurare n8n: întrebări frecvente"),
 ("Definiți RPO și RTO înainte de un incident","Stabiliți RPO și RTO înainte de un incident"),
 ("Compararea furnizorilor?","Comparați furnizorii?"),
],
"ro/contact.html":[
 ("Starea contactului","Informații de contact"),
],
"ro/instalare-n8n-vps-docker.html":[
 ("Instalați n8n pe un VPS","Instalați n8n pe VPS"),
 ("Pregătiți VPS înainte de a începe n8n","Pregătiți VPS-ul înainte de instalarea n8n"),
 ("Docker Compune","Docker Compose"),
 ("1. Pregătiți Docker, DNS și accesați","1. Pregătiți Docker, DNS și accesul"),
 ("4. Creați HTTPS Caddyfile","4. Creați Caddyfile-ul HTTPS"),
 ("5. Porniți recipientele și testați din exterior","5. Porniți containerele și testați din exterior"),
 ("Setați secrete și adrese URL publice în mod deliberat","Configurați explicit secretele și URL-urile publice"),
 ("PostgreSQL acreditări","Acreditări PostgreSQL"),
 ("Nume de gazdă public","Hostname public"),
 ("Adresa URL a webhook","URL webhook"),
 ("Persistați n8n și PostgreSQL separat","Păstrați persistent datele n8n și PostgreSQL, separat"),
 ("n8n date","Date n8n"),
 ("PostgreSQL date","Date PostgreSQL"),
 ("Conectați n8n la serviciul de bază de date privată","Conectați n8n la serviciul privat de bază de date"),
 ("Puneți adresa URL publică n8n în spatele HTTPS","Plasați URL-ul public n8n în spatele HTTPS"),
 ("Actualizați implementarea Docker fără a trata containerele ca copii de rezervă","Actualizați deployment-ul Docker fără a considera containerele backup-uri"),
 ("Mai întâi faceți backup","Faceți mai întâi backup"),
 ("Recreează-te în siguranță","Recreați în siguranță"),
 ("Verificați starea de sănătate înainte de a conecta fluxuri de lucru reale","Verificați funcționarea înainte de a conecta workflow-uri reale"),
 ("Verificați punctul final de sănătate n8n","Verificați endpoint-ul de health n8n"),
 ("Fixați versiunile aplicației","Folosiți versiuni fixe ale aplicației"),
 ("Do not bump PostgreSQL major versions in place","Nu actualizați direct versiunea majoră PostgreSQL pe datele existente"),
 ("Compararea furnizorilor?","Comparați furnizorii?"),
],
"ro/n8n-cloud-vs-self-hosted.html":[
 ("n8n Cloud vs auto-găzduit: cost și control","n8n Cloud vs Self-Hosted: cost și control"),
 ("n8n Cloud vs auto-găzduit","n8n Cloud vs Self-Hosted"),
 ("Alegeți auto-găzduit VPS când","Alegeți un VPS self-hosted când"),
 ("n8n Cloud vs auto-găzduit VPS: tabel de comparație","n8n Cloud vs VPS self-hosted: tabel comparativ"),
 ("Cum un program simplu poate folosi o indemnizație de execuție Cloud","Cum poate un program simplu să consume cota de execuții Cloud"),
 ("Un singur clic n8n VPS nu este întotdeauna un serviciu gestionat","Un VPS n8n cu instalare într-un clic nu este întotdeauna un serviciu gestionat"),
 ("Exemplu: cât costă de fapt o lună n8n auto-găzduită?","Exemplu: cât costă de fapt o lună de n8n self-hosted?"),
 ("Alegeți în funcție de cine deține munca operațională","Alegeți în funcție de cine gestionează operațiunile"),
 ("Unde auto-găzduirea schimbă arhitectura","Unde self-hosting-ul schimbă arhitectura"),
 ("Ce vă asumați când vă autogăzduiți","Ce responsabilități vă asumați cu self-hosting"),
 ("Confortul în cloud vs controlul de scalare auto-găzduit","Comoditatea Cloud vs controlul scalării în self-hosted"),
 ("nor","Cloud"),
 ("Modul coadă","Queue Mode"),
 ("Comunitate auto-găzduită","Community Self-Hosted"),
 ("Afaceri/Întreprinderi auto-găzduite","Business/Enterprise Self-Hosted"),
 ("Gazduire n8n pentru alti utilizatori","Găzduire n8n pentru alți utilizatori"),
 ("n8n Cloud vs auto-găzduit: întrebări frecvente","n8n Cloud vs Self-Hosted: întrebări frecvente"),
 ("Pentru oficial n8n Cloud","Pentru n8n Cloud oficial"),
 ("Pentru un auto-găzduit VPS","Pentru un VPS self-hosted"),
 ("Inventariază-ți implementarea","Inventariați deployment-ul"),
],
"ro/cerinte-vps-n8n.html":[
 ("n8n VPS Cerințe","Cerințe VPS pentru n8n"),
 ("Producție minimă, practică și sarcini de lucru mai grele","Minim, producție practică și sarcini de lucru mai solicitante"),
 ("Exemplu ușor, mereu pornit","Instanță ușoară, mereu activă"),
 ("Greu sau consumator de date","Sarcini grele sau intensive în date"),
 ("Depozitare","Stocare"),
 ("Dimensiunea sarcinii utile","Dimensiunea payloadului"),
 ("CPU-noduri grele","Noduri intensive CPU"),
 ("Estimați n8n stocarea istoricului de execuție înainte de a comanda","Estimați stocarea istoricului de execuție n8n înainte de comandă"),
 ("Docker și cheltuielile generale de producție","Docker și overhead-ul de producție"),
 ("Docker & Compune","Docker & Compose"),
 ("Când un VPS mai mare încetează să mai fie întregul răspuns","Când un VPS mai mare nu mai este singurul răspuns"),
 ("Definiți-le înainte de a alege un VPS","Stabiliți aceste lucruri înainte de a alege un VPS"),
 ("Cum se utilizează o intrare 1 GB VPS","Cum să folosiți opțiunea VPS de 1 GB"),
 ("n8n VPS cerinte: intrebari frecvente","Cerințe VPS pentru n8n: întrebări frecvente"),
 ("Compararea furnizorilor?","Comparați furnizorii?"),
],
"ro/confidentialitate.html":[],
"ro/securitate-n8n-vps.html":[
 ("Securizat n8n pe un VPS","Securitate n8n pe VPS"),
 ("Linia de referință minimă de securitate înainte de expunerea publică","Nivelul minim de securitate înainte de expunerea publică"),
 ("numai HTTPS","Doar HTTPS"),
 ("Întăriți SSH","Hardening SSH"),
 ("TLS rezilierea","Terminare TLS"),
 ("Adresa URL a webhook","URL webhook"),
 ("Protejați cheia de criptare și limita de acreditări","Protejați cheia de criptare și domeniul acreditărilor"),
 ("Secretele mediului","Secrete de mediu"),
 ("Domeniul de aplicare a acreditării","Domeniul acreditărilor"),
 ("Nodurile pot extinde granița de securitate","Nodurile pot extinde perimetrul de securitate"),
 ("Securitatea este un proces de operare","Securitatea este un proces operațional continuu"),
 ("Pregătiți derularea și recuperarea","Pregătiți rollback-ul și recuperarea"),
 ("Securizați stiva înainte de a activa fluxurile de lucru de producție","Securizați stack-ul înainte de a activa workflow-urile de producție"),
 ("Necesită o protecție mai puternică de conectare","Impuneți protecție mai puternică la autentificare"),
 ("Utilizați SSRF și controalele secrete în mod deliberat","Folosiți explicit controale SSRF și pentru secrete"),
 ("n8n VPS securitate: întrebări frecvente","Securitate VPS pentru n8n: întrebări frecvente"),
 ("Compararea furnizorilor?","Comparați furnizorii?"),
],
"ro/n8n-queue-mode.html":[
 ("n8n Mod coadă","n8n Queue Mode"),
 ("Chiar ai nevoie de modul coadă?","Aveți cu adevărat nevoie de Queue Mode?"),
 ("Rămâneți în modul normal când","Rămâneți în modul obișnuit când"),
 ("Luați în considerare modul coadă când","Luați în considerare Queue Mode când"),
 ("Scala pe verticală mai întâi când","Scalați vertical mai întâi când"),
 ("Cum funcționează modul coadă n8n","Cum funcționează Queue Mode în n8n"),
 ("De ce are nevoie orice implementare în modul coadă","De ce are nevoie orice deployment Queue Mode"),
 ("Se potrivește configurația n8n","Configurație n8n identică"),
 ("Capacitatea muncitorului","Capacitatea workerului"),
 ("Lucrătorii cresc atât în funcție de număr, cât și de locuri de muncă per lucrător","Capacitatea crește prin numărul de workeri și concurența per worker"),
 ("Adăugați lucrători când","Adăugați workeri când"),
 ("Urmăriți PostgreSQL","Monitorizați PostgreSQL"),
 ("Modul coadă poate adăuga latență de transfer de execuție","Queue Mode poate adăuga latență la transferul execuției"),
 ("Planificați înainte de a distribui lucrătorii","Planificați înainte de a distribui workerii"),
 ("Aflați dacă coada vă ajută","Măsurați dacă Queue Mode ajută efectiv"),
 ("Adâncimea cozii","Adâncimea cozii"),
 ("Muncitor CPU & RAM","CPU & RAM per worker"),
 ("Controale de sănătate","Verificări de health"),
 ("Amplasați câte un blocaj la un moment dat","Scalați câte un bottleneck pe rând"),
 ("Modul coadă scala execuțiile, dar nu face automat procesul principal foarte disponibil","Queue Mode scalează execuțiile, dar nu face automat procesul principal high-availability"),
 ("Procesoarele Webhook sunt un strat de scalare separat","Procesoarele webhook reprezintă un strat separat de scalare"),
 ("Multi-principal este o caracteristică diferită","Multi-main este o funcționalitate diferită"),
 ("n8n modul coadă: întrebări frecvente","n8n Queue Mode: întrebări frecvente"),
 ("Compararea furnizorilor?","Comparați furnizorii?"),
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
    print("ROMANIAN_NATIVE_POLISH",i+1,"/11",target,"replacements",hits,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _ro_native_polish.py PAGE_INDEX")
    i=int(sys.argv[1])
    if not 0<=i<len(PAGES):
        raise SystemExit("Page out of range")
    polish(i)
