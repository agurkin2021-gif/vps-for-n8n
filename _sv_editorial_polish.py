#!/usr/bin/env python3
"""Swedish editorial fixes after raw translation; no change to HTML, CSS, JS, prices or technical values."""
from __future__ import annotations
import re
from pathlib import Path
from _sv_publish_qa import signature, scripts, styles, prices

ROOT=Path(__file__).resolve().parent

# Only complete plain-text paragraphs are rewritten, preserving all surrounding HTML markup.
PARAGRAPHS=[
("Välj genom vad varje utförandeprocesser", "Utgå från vad varje arbetsflödeskörning behandlar och hur många körningar som pågår samtidigt. En liten kontaktsynkronisering, en omfattande dokumentimport och en plötslig ökning av webhook-anrop ställer olika krav på servern."),
("Kör små, pågående n8n automationer", "Kör mindre, kontinuerliga n8n-automatiseringar, till exempel schemalagda API-uppdateringar, aviseringar och enkla webhooks. En VPS med 1 GB RAM kan fungera bra i vardagen om minnesanvändningen och antalet samtidiga körningar håller sig inom dess kapacitet."),
("Välj för små API förfrågningar", "Passar mindre API-anrop, kontaktuppdateringar och aviseringar som sällan körs samtidigt. Håll n8n-installationen resurssnål och begränsa mängden sparad körningshistorik."),
("Välj mer RAM när: Du lägger till större nyttolast", "Välj mer RAM när du lägger till större datamängder, flera samtidiga jobb eller fler tjänster på samma server."),
("Vår rekommenderade konfiguration för en blygsam n8n", "Vår rekommenderade konfiguration för en mindre n8n-miljö med PostgreSQL och HTTPS som hanterar små JSON-datamängder och flera samtidiga integrationer."),
("Snabbt svar: För den lägsta kostnaden självstyrda rutten", "Kort svar: För den billigaste självhanterade lösningen bör du jämföra vårt Standard-VPS-alternativ. För n8n-installation med ett klick kan du jämföra Hostinger, OVHcloud, Bluehost och Contabo. Vill du ha n8n förinstallerat med PostgreSQL och HTTPS kan du överväga DreamHost. Det bästa valet beror på vem som sköter applikationen, vad säkerhetskopiorna faktiskt omfattar, priset efter kampanjperioden och hur återställning eller migrering går till. Rekommendationerna bygger på publicerade funktioner, inte prestandatester."),
("Dessa är olika hosting erbjudanden", "Det här är olika hostingerbjudanden, inte servrar som har jämförts i likvärdiga prestandatester. Jämför installationssättet, vem som ansvarar för n8n, möjligheterna till återställning och de faktiska betalningsvillkoren innan du bestämmer dig."),
("Publicerade produktdetaljer kontrollerade 8 oktober 2026", "Publicerade produktuppgifter kontrollerades den 8 oktober 2026. En färdig installation med ett klick betyder inte att n8n är fullt hanterat. Priser, tillgång till säkerhetskopior och faktureringsvillkor kan förändras. Kontrollera vald plan och villkoren i kassan. På mindre skärmar kan du rulla tabellen horisontellt för att se alla sex kriterierna."),
("Utplacering: en regelbunden självstyrd Linux VPS;", "Driftsättning: en vanlig självhanterad Linux-VPS där n8n inte är förinstallerat. Publicerade Standard-planer börjar vid $0.07/day med 1 vCPU, 1 GB RAM, 10 GB lagring och 1 TB trafik per månad. Det är en VPS som kan användas löpande för arbetsbelastningar inom dessa resursgränser, inte ett testabonnemang. Du ansvarar för n8n, säkerheten, uppdateringar, övervakning och återställning från externa säkerhetskopior. Kontrollera vald konfiguration, trafikvillkor, tilläggstjänster och region innan du beställer."),
("Utplacering: en n8n en-klicka VPS mall", "Driftsättning: en VPS-mall för n8n-installation med ett klick, med Docker-verktyg och publicerad vägledning för köläge. Hostinger uppger att veckovisa automatiska säkerhetskopior ingår i deras n8n-VPS-erbjudande. Det annonserade månadspriset kan kräva förskottsbetalning för en längre period och stiga vid förnyelse. Jämför därför den totala kostnaden för avtalstiden och förnyelsepriset, inte bara startpriset. Servern kan fortfarande anpassas med root-behörighet, men kontrollera vilka underhållsuppgifter för n8n som faktiskt ingår i supporten."),
("Utplacering: n8n är tillgänglig förinstallerad på en berättigad VPS", "Driftsättning: n8n kan levereras förinstallerat på en kvalificerad VPS. Det finns även dokumentation för manuell installation med Docker. OVHclouds amerikanska n8n-VPS-erbjudande visar en instegsserver med 2 vCores, 4 GB RAM och 40 GB NVMe-lagring samt daglig säkerhetskopiering av de senaste 24 timmarna. Ett så kort återställningsfönster motsvarar inte långsiktig lagring av kopior utanför servern. Granska migreringsanvisningar, ordinarie pris och tillgänglig region innan du köper."),
("Utplacering: Bluehost annonserar en enklicka n8n VPS bild", "Driftsättning: Bluehost marknadsför en VPS-avbildning för n8n-installation med ett klick, full root-behörighet och NVMe-lagring. Detta är en självhanterad lösning, inte ett löfte om att supporten sköter anpassade arbetsflöden eller Docker-konfigurationen. Kontrollera rabatter för den första avtalsperioden, förnyelsekostnaden, möjligheter till säkerhetskopiering och återställning samt ansvaret för applikationsuppdateringar. Passar dig som vill ha både enkel installation och kontroll över servern."),
("Utplacering: n8n förinstalleras med PostgreSQL och automatisk SSL", "Driftsättning: n8n levereras förinstallerat med PostgreSQL och automatisk SSL i den marknadsförda VPS-miljön, med bibehållen root-behörighet. I DreamHosts publicerade exempel kostar Stack 4 $8.99/month under de första tre månaderna och $15.99/month vid förnyelse. Det visar varför kampanjpriser måste skiljas från löpande priser. Du väljer själv när uppdateringar görs. Den dokumenterade databassäkerhetskopian skapas med ett kommando och ska inte förväxlas med verifierad, automatisk återställning från en extern säkerhetskopia."),
("Utplacering: Contabo erbjuder en förinstallerad n8n enklicksbild", "Driftsättning: Contabo erbjuder en förinstallerad n8n-avbildning för installation med ett klick på kvalificerade VPS-planer. Du behåller kontrollen över den egenhostade miljön, medan felsökning av n8n och det dagliga underhållet av applikationen inte automatiskt ingår i infrastruktursupporten. Contabo beskriver automatisk säkerhetskopiering som ett tillgängligt alternativ, inte som något som alltid ingår. Kontrollera om det är valt, priset, lagringstiden och återställningsrutinen i kassan. Jämför även första avtalsperioden med villkoren för förnyelse."),
("Separata tre erbjudanden innan du jämför", "Skilj mellan tre typer av erbjudanden: en vanlig Linux-VPS där du installerar n8n själv, en förinstallerad avbildning som förenklar starten och en faktiskt hanterad n8n-tjänst där leverantören uttryckligen ansvarar för uppdateringar eller återställning. Kontrollera vad som redan är konfigurerat (PostgreSQL, HTTPS och beständig datalagring) och vem som underhåller applikationen efter första inloggningen. En installation med ett klick innebär inte automatiskt löpande applikationshantering.")
]

# Limited recurring terminology corrections, applied only to user-visible text segments.
WORDS=[
("PROVIDER COMPARISON · REVIEWED 8 OKTOBER 2026","LEVERANTÖRSJÄMFÖRELSE · GRANSKAD 8 OKTOBER 2026"),
("SIX OPTIONS · EN SET OF BUYING CRITERIA","SEX ALTERNATIV · GEMENSAMMA BEDÖMNINGSKRITERIER"),
("QUICK SHORTLIST","SNABB ÖVERSIKT"),
("Vad för att möta","VAD DU BÖR JÄMFÖRA"),
("Self-managed","Självhanterad"),
("Självstyrd","Självhanterad"),
("självstyrda","självhanterade"),
("självstyrd","självhanterad"),
("självvärda","egenhostade"),
("självvärd","egenhostad"),
("Utplacera","Driftsätt"),
("Utplacering","Driftsättning"),
("utplacering","driftsättning"),
("avrättningar","körningar"),
("utförandehistorik","körningshistorik"),
("verkställande historia","körningshistorik"),
("API uppdateringar","API-uppdateringar"),
("API förfrågningar","API-anrop"),
("JSON nyttolast","JSON-datamängder"),
("Docker Komponera","Docker Compose"),
("Inställningar checklist","installationschecklistan"),
("Connect HTTPS + webhooks","Anslut HTTPS + webhooks"),
("Partnerdisclosure: The ","Partnerinformation: Länken till "),
(" länken sponsras. Jämförelsen betyder inte "," är sponsrad. Jämförelsen innebär inte att "),
(" förinstallerad."," förinstallerat."),
("Välj genom vad varje utförandeprocesser","Utgå från vad varje arbetsflöde behandlar"),
("standard planer","Standard-planer"),
("Standard planer","Standard-planer"),
("en-klicka","installation med ett klick")
]

WORDS.extend([
  [
    "AI arbetsflöden: välj var modellen körs",
    "AI-arbetsflöden: välj var modellen ska köras"
  ],
  [
    "Varför arbetsflödesräkning ensam är fel sätt att välja en plan",
    "Varför antalet arbetsflöden inte räcker för att välja VPS-plan"
  ],
  [
    "Uppskatta din execution-historia lagring",
    "Beräkna lagringsbehovet för körningshistorik"
  ],
  [
    "Jag vill ha den lägsta friktionsstarten",
    "Jag vill komma igång med så lite arbete som möjligt"
  ],
  [
    "Jag förväntar mig köläge senare",
    "Jag räknar med att använda köläge senare"
  ],
  [
    "Vilken n8n backup bör skydda",
    "Vad en säkerhetskopia av n8n måste skydda"
  ],
  [
    "Distributionskonfiguration",
    "Driftsättningskonfiguration"
  ],
  [
    "Logisk export mot fullständig katastrofåtervinning",
    "Logisk export jämfört med fullständig katastrofåterställning"
  ],
  [
    "Workflow och credential export",
    "Export av arbetsflöden och inloggningsuppgifter"
  ],
  [
    "Entity export",
    "Export av objekt"
  ],
  [
    "Fullständig återhämtning",
    "Fullständig återställning"
  ],
  [
    "Leverantören snapshot",
    "Ögonblicksbild från leverantören"
  ],
  [
    "Exekveringshistoria",
    "Körningshistorik"
  ],
  [
    "Databasbackup kanske inte täcker varje arbetsflödesberoende",
    "En databassäkerhetskopia kanske inte omfattar alla beroenden i arbetsflödet"
  ],
  [
    "ihållande .n8n",
    "Beständig .n8n-katalog"
  ],
  [
    "gemenskapsnoder",
    "community-noder"
  ],
  [
    "Säkerhetskopiera databasen konsekvent",
    "Skapa konsekventa säkerhetskopior av databasen"
  ],
  [
    "Förbered VPS innan du börjar n8n",
    "Förbered VPS:en innan du installerar n8n"
  ],
  [
    "1. Förbered Docker, DNS och tillgång",
    "1. Förbered Docker, DNS och åtkomst"
  ],
  [
    "2Skapa miljövärden och bevara nyckeln",
    "2. Skapa miljövariabler och spara krypteringsnyckeln"
  ],
  [
    "3. Skriv compose.yaml för en ny installation",
    "3. Skapa compose.yaml för en ny installation"
  ],
  [
    "4. Skapa HTTPS Caddyfile",
    "4. Skapa en Caddyfile för HTTPS"
  ],
  [
    "5. Starta behållarna och testa utifrån",
    "5. Starta containrarna och testa extern åtkomst"
  ],
  [
    "6. Back up innan du ändrar stiftade versioner",
    "6. Säkerhetskopiera innan du ändrar låsta versioner"
  ],
  [
    "Offentlig värdnamn",
    "Offentligt värdnamn"
  ],
  [
    "Webhook URL",
    "Webhook-URL"
  ],
  [
    "Persist n8n och PostgreSQL separat",
    "Spara data för n8n och PostgreSQL separat"
  ],
  [
    "n8n data",
    "n8n-data"
  ],
  [
    "PostgreSQL data",
    "PostgreSQL-data"
  ],
  [
    "n8n Cloud vs Self-Hosted: Kostnad och kontroll",
    "n8n Cloud kontra egen drift: kostnad och kontroll"
  ],
  [
    "Välj genom ansvar, inte av serverpriset ensam",
    "Välj utifrån ansvar, inte enbart serverpris"
  ],
  [
    "Antingen kan produktionsklart",
    "Båda alternativen kan användas i produktion"
  ],
  [
    "One-click n8n VPS är inte alltid en förvaltad tjänst",
    "En n8n-VPS med ettklicksinstallation är inte alltid en hanterad tjänst"
  ],
  [
    "Exempel: Vad kostar egentligen en egen värd n8n månad?",
    "Exempel: Vad kostar en egenhostad n8n-instans per månad?"
  ],
  [
    "Självvärdering är inte bara VPS faktura",
    "Egen drift handlar inte bara om VPS-fakturan"
  ],
  [
    "Misslyckande kostnad",
    "Kostnaden för driftstopp"
  ],
  [
    "Där egenhostadering förändrar arkitekturen",
    "När egen drift förändrar arkitekturen"
  ],
  [
    "Vad du tar på när du själv värd",
    "Vilket ansvar du tar vid egen drift"
  ],
  [
    "Minsta, praktisk produktion och tyngre arbetsbelastningar",
    "Minimikrav, praktisk produktionsmiljö och tyngre arbetsbelastningar"
  ],
  [
    "Ljus, alltid-på instans",
    "Lättviktig instans som alltid är igång"
  ],
  [
    "Real VPS specifikationer för att jämföra din n8n arbetsbelastning",
    "Verkliga VPS-specifikationer för din n8n-belastning"
  ],
  [
    "Har n8n ett officiellt minimum VPS?",
    "Har n8n officiella minimikrav för VPS?"
  ],
  [
    "Payload storlek",
    "Storlek på datamängder"
  ],
  [
    "Hur man berättar om n8n behöver mer RAM, CPU eller disk",
    "Så avgör du om n8n behöver mer RAM, CPU eller lagring"
  ],
  [
    "CPU/samvaluta",
    "CPU och samtidighet"
  ],
  [
    "SQLite, PostgreSQL och ihållande uppgifter",
    "SQLite, PostgreSQL och beständig datalagring"
  ],
  [
    "Disk tillväxt",
    "Lagringsbehov över tid"
  ],
  [
    "Uppskattning n8n exekveringshistorik lagring innan beställning",
    "Beräkna lagringsutrymmet för n8n-körningshistorik före beställning"
  ],
  [
    "Analytics och affiliate länkar",
    "Analysverktyg och affiliatelänkar"
  ],
  [
    "HTTPS Endast",
    "Endast HTTPS"
  ],
  [
    "Harden SSH",
    "Säkra SSH"
  ],
  [
    "Skydda referenser",
    "Skydda inloggningsuppgifter"
  ],
  [
    "Proxy konfiguration",
    "Proxykonfiguration"
  ],
  [
    "Säker cookies",
    "Säkra cookies"
  ],
  [
    "Container exponering",
    "Exponering av containrar"
  ],
  [
    "Håll backend tjänster privat",
    "Håll backendtjänster privata"
  ],
  [
    "Skydda krypteringsnyckeln och kreditgränsen",
    "Skydda krypteringsnyckeln och åtkomstuppgifterna"
  ],
  [
    "Miljöhemligheter",
    "Hemligheter i miljövariabler"
  ],
  [
    "Behörig omfattning",
    "Behörigheternas omfattning"
  ],
  [
    "Noder kan utöka säkerhetsgränsen",
    "Noder kan öka angreppsytan"
  ],
  [
    "Stanna i vanlig läge när",
    "Behåll vanligt läge när"
  ],
  [
    "Skala vertikalt först när",
    "Skala upp servern först när"
  ],
  [
    "Vad varje queue-mode distribution behöver",
    "Vad varje installation med köläge behöver"
  ],
  [
    "Matcha n8n konfiguration",
    "Anpassa n8n-konfigurationen"
  ],
  [
    "Arbetsförmåga",
    "Worker-kapacitet"
  ],
  [
    "Arbetare skala både genom räkning och av jobb per arbetstagare",
    "Skala med fler workers och rätt antal jobb per worker"
  ],
  [
    "Öka valutan när",
    "Öka samtidigheten när"
  ],
  [
    "Lägg till arbetstagare när",
    "Lägg till workers när"
  ],
  [
    "Minska valutan när",
    "Minska samtidigheten när"
  ],
  [
    "Se PostgreSQL",
    "Övervaka PostgreSQL"
  ],
  [
    "Queue mode kan lägga till exekvering handoff latens",
    "Köläge kan ge extra fördröjning när körningar lämnas över"
  ],
  [
    "Förbise inte delad lagring",
    "Glöm inte delad lagring"
  ],
  [
    "Filsystembegränsning",
    "Begränsningar i filsystemet"
  ],
  [
    "Stora webhook svar",
    "Stora webhook-svar"
  ],
  [
    "Planera innan de distribuerar arbetare",
    "Planera innan du driftsätter workers"
  ]
])

P_RE = re.compile(r'(<p\b[^>]*>)([^<]*)(</p>)',re.I|re.S)
TOKENS = re.compile(r'(<[^>]*>)',re.S)

def polish(text):
    def rewrite(m):
        raw=m.group(2)
        for prefix, replacement in PARAGRAPHS:
            if raw.startswith(prefix):
                return m.group(1)+replacement+m.group(3)
        return m.group(0)
    text=P_RE.sub(rewrite,text)
    # Protect literal script/style/technical code blocks while editing text nodes.
    parts=TOKENS.split(text)
    skip=None
    for i,part in enumerate(parts):
        if part.startswith('<'):
            op=re.match(r'<(script|style|pre|code)\b',part,re.I)
            cl=re.match(r'</(script|style|pre|code)\s*>',part,re.I)
            if op:skip=op.group(1).lower()
            elif cl and skip==cl.group(1).lower():skip=None
        elif skip is None:
            for before,after in WORDS:
                part=part.replace(before,after)
            parts[i]=part
    return ''.join(parts)

def run():
    translated=sorted((ROOT/'sv').glob('*.html'))
    if len(translated)!=11:raise AssertionError('Swedish editorial pass requires exactly 11 completed pages')
    updated=0
    for f in translated:
        before=f.read_text(encoding='utf-8')
        after=polish(before)
        if signature(before)!=signature(after):raise AssertionError(f'HTML changed: {f}')
        if scripts(before)!=scripts(after):raise AssertionError(f'JS changed: {f}')
        if styles(before)!=styles(after):raise AssertionError(f'CSS changed: {f}')
        if prices(before)!=prices(after):raise AssertionError(f'Prices changed: {f}')
        if after!=before:
            f.write_text(after,encoding='utf-8')
            updated+=1
        print('SV_EDITORIAL',f.name,'PASS',flush=True)
    print('SV_EDITORIAL_COMPLETE',updated,'of',len(translated),flush=True)

if __name__=='__main__':run()
