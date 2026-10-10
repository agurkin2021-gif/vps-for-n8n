#!/usr/bin/env python3
"""Czech editorial corrections, preserving English DOM, CSS, JS, and prices."""
from pathlib import Path
import re, html, collections

ROOT=Path(__file__).resolve().parent
META={
"index.html":("VPS pro n8n od $0.07/Day – tarify a výběr konfigurace","Porovnejte konfigurace VPS pro n8n od $0.07/day. Vyberte CPU, RAM, úložiště a přenos dat podle potřeb menších automatizací, produkčních workflow, zpracování dat a AI."),
"best-vps-for-n8n.html":("Nejlepší VPS pro n8n v roce 2026: srovnání 6 poskytovatelů","Porovnejte 6 poskytovatelů VPS pro n8n podle způsobu nasazení, míry kontroly, záloh, podpory, migrace, lokality a škálování. Vyberte řešení pro své workflow."),
"about.html":("O projektu | n8nVPS","Informace o n8nVPS, nezávislém průvodci výběrem parametrů VPS a produkční infrastrukturou pro vlastní provoz n8n."),
"n8n-backup-and-restore.html":("Zálohování a obnova n8n","Zálohování a obnova n8n na vlastním VPS: PostgreSQL nebo SQLite, workflow, přihlašovací údaje, šifrovací klíč, binární data, zálohy mimo server a testování obnovy."),
"contact.html":("Kontakt | n8nVPS","Kontaktujte n8nVPS kvůli opravám, dotazům k projektu a obchodním poptávkám."),
"install-n8n-on-a-vps.html":("Jak nainstalovat n8n na VPS","Postup instalace n8n na VPS pomocí Docker Compose, PostgreSQL, trvalého úložiště, HTTPS a reverzní proxy, včetně správného nastavení webhooků."),
"n8n-cloud-vs-self-hosted.html":("n8n Cloud vs. vlastní hosting: náklady a kontrola","Srovnejte n8n Cloud s vlastním provozem n8n na VPS podle nákladů, kontroly nad infrastrukturou, údržby, umístění dat, škálování a technické odpovědnosti."),
"n8n-vps-requirements.html":("Požadavky n8n na VPS","Požadavky n8n na VPS: RAM, CPU, SSD úložiště, PostgreSQL, Docker, souběžná spuštění a výběr kapacity pro produkční provoz."),
"privacy.html":("Zásady ochrany osobních údajů | n8nVPS","Zásady ochrany soukromí na webu n8nVPS včetně informací o webové analytice a partnerských odkazech."),
"secure-n8n-on-a-vps.html":("Jak zabezpečit n8n na VPS","Zabezpečení n8n na vlastním VPS: HTTPS, reverzní proxy, firewall, ochrana SSH, privátní PostgreSQL, ochrana šifrovacího klíče, prevence SSRF a bezpečnostní audity."),
"n8n-queue-mode.html":("Režim fronty v n8n","Kdy využít režim fronty v n8n, jak Redis a workery škálují spouštění workflow, souběžnost workerů, požadavky na PostgreSQL, monitorování a výběr VPS.")
}
REPLACE={
"index.html":[
("Spusťte webhooky, plánovanou automatizaci a integraci AI na svém vlastním serveru Linux.","Provozujte webhooky, plánované automatizace a integrace AI na vlastním linuxovém serveru."),
("Přizpůsobte svou pracovní zátěž konfiguraci VPS a vložte svůj rozpočet do zdrojů, na kterých záleží.","Zvolte konfiguraci VPS podle zátěže a investujte do prostředků, které vaše workflow skutečně potřebují."),
("Samoobslužné Linux VPS.","Samostatně spravované VPS s Linuxem."),
("Nasaďte n8n s Docker pomocí","Nainstalujte n8n pomocí Dockeru podle"),
("kontrolní seznam nastavení","instalačního kontrolního seznamu"),
("Čtyři skutečné, samostatně spravované konfigurace Standard VPS počínaje $0.07/day.","Čtyři skutečné konfigurace samostatně spravovaných VPS řady Standard od $0.07/day."),
("Každá karta se otevírá VDSina prostřednictvím našeho partnerského odkazu; v katalogu poskytovatelů vyberte plán Standard odpovídající zde uvedeným CPU, RAM a úložiště. Server se nedodává s předinstalovaným n8n.","Každá karta vede na VDSina přes náš partnerský odkaz. V katalogu poskytovatele vyberte tarif Standard s uvedeným CPU, RAM a úložištěm. Server se dodává bez předinstalovaného n8n."),
("00 · ROZPOČET VPS","00 · ÚSPORNÉ VPS"),
("A 1 GB VPS může být praktickou každodenní možností, když využití paměti a souběžné spouštění zůstávají v mezích.","VPS s 1 GB RAM může pro běžný provoz stačit, pokud spotřeba paměti a počet souběžných spuštění nepřekračují jeho možnosti."),
("10 GB úložiště · 1 TB provoz","10 GB úložiště · 1 TB přenos dat"),
(">Měřítko<",">Škálování<")
],
"about.html":[
(">O<",">O PROJEKTU<"),
(">O n8nVPS<",">O projektu n8nVPS<"),
("n8nVPS je nezávislý průvodce výběrem zdrojů VPS pro vlastní hostování n8n podle pracovního zatížení, souběžnosti a požadavků na produkci.","n8nVPS je nezávislý průvodce výběrem prostředků VPS pro vlastní provoz n8n podle náročnosti workflow, souběžných spuštění a požadavků produkčního prostředí."),
("Redakční rozsah","Redakční zaměření"),
("n8nVPS zveřejňuje pokyny k infrastruktuře pro vlastní hostování n8n. Odkazy na komerční partnery jsou zveřejněny tam, kde se objevují.","n8nVPS publikuje informace o infrastruktuře pro vlastní provoz n8n. Partnerské komerční odkazy jsou označeny na místech, kde se vyskytují.")
],
"contact.html":[
("Použijte tuto stránku pro opravy, projektové otázky a obchodní dotazy související s n8nVPS.","Tato stránka slouží k hlášení chyb, dotazům k projektu a obchodním poptávkám týkajícím se n8nVPS."),
("Stav kontaktu","Kontaktní informace"),
("Pro tento projekt není uvedena žádná adresa veřejné kanceláře. Neposílejte hesla, soukromé klíče ani platební údaje.","U tohoto projektu není zveřejněna adresa kanceláře. Neposílejte hesla, soukromé klíče ani platební údaje."),
("Pro opravy určete adresu URL stránky a konkrétní prohlášení nebo technické podrobnosti, které je třeba zkontrolovat.","Při upozornění na chybu uveďte URL stránky a konkrétní tvrzení nebo technický údaj, který je třeba prověřit.")
],
"privacy.html":[
("Analytics a přidružené odkazy","Webová analytika a partnerské odkazy"),
("Tento web v současné době v kódu stránky nenačítá sledovač webové analýzy. Některé odchozí odkazy jsou přidružené odkazy a mohou poskytovateli destinace umožnit přiřadit doporučení podle jeho vlastních postupů ochrany soukromí a souborů cookie.","Tento web v současnosti v kódu stránek nenačítá nástroj pro webovou analytiku. Některé odchozí odkazy jsou partnerské a cílovému poskytovateli mohou umožnit připsat doporučení podle jeho vlastních zásad ochrany soukromí a používání souborů cookie."),
("Pokud později přidáte analytiku, reklamní značky nebo další soubory cookie, je nutné tyto zásady aktualizovat, aby popisovaly skutečnou implementaci.","Pokud budou později přidány analytické či reklamní značky nebo další soubory cookie, je nutné tyto zásady aktualizovat tak, aby odpovídaly skutečnému způsobu jejich použití.")
],
"n8n-backup-and-restore.html":[("<h3>databáze</h3>","<h3>Databáze</h3>"),("Trvalé soubory","Trvale ukládané soubory")],
"install-n8n-on-a-vps.html":[("Připravte si VPS před zahájením n8n","Připravte VPS před spuštěním n8n")],
"n8n-cloud-vs-self-hosted.html":[("Vyberte n8n Cloud když","Zvolte n8n Cloud, pokud"),("Vyberte si vlastní hostování VPS kdy","Zvolte vlastní provoz na VPS, pokud"),("Obojí může být připraveno k výrobě","Obě možnosti mohou být vhodné pro produkční provoz")],
"n8n-vps-requirements.html":[("Minimální, praktická výroba a větší pracovní zátěž","Minimální nároky, menší produkční nasazení a náročnější úlohy"),("Lehký, vždy zapnutý příklad","Nenáročná nepřetržitě běžící instance"),("Praktická drobná výroba","Menší produkční nasazení"),("Těžké nebo datově náročné","Náročné úlohy nebo zpracování velkých objemů dat"),(">Skladování<",">Úložiště<")],
"secure-n8n-on-a-vps.html":[("Minimální bezpečnostní základ před vystavením veřejnosti","Základní zabezpečení před zpřístupněním internetu"),("Kalení SSH","Zabezpečení SSH")],
"n8n-queue-mode.html":[("Měřítko nejprve vertikálně, když","Nejprve navyšujte výkon jednoho serveru, pokud"),("Změřte před změnou architektury","Před změnou architektury nejprve měřte"),("Zůstaňte v běžném režimu, když","Zůstaňte v běžném režimu, pokud"),("Zvažte režim fronty, když","Zvažte režim fronty, pokud")]
}
def script_parts(s,tag):
    rx=rf'<{tag}\\b[^>]*>([\\s\\S]*?)</{tag}>'
    return re.findall(rx,s,re.I)
def sig(s):
    return [('/' if m.group().startswith('</') else '')+m.group(1).lower()
        for m in re.finditer(r'</?([a-z][\\w-]*)\\b[^>]*>',s,re.I)
        if m.group(1).lower() not in ('link','meta')]
def prices(s):
    s=re.sub(r'<(?:script|style)\\b[^>]*>[\\s\\S]*?</(?:script|style)>','',s,flags=re.I)
    s=html.unescape(re.sub(r'<[^>]*>',' ',s))
    return collections.Counter(re.findall(r'\\$\\s*\\d+(?:[.,]\\d+)*(?:/(?:day|month|year|mo))?',s,re.I))
def set_meta(s,key,value):
    def change(m):
        tag=m.group()
        field=re.search(r'\\b(?:name|property)=(["\\\'])(.*?)\\1',tag,re.I)
        if not field or field.group(2)!=key:return tag
        return re.sub(r'\\bcontent=(["\\\'])(.*?)\\1',lambda x:'content='+x.group(1)+html.escape(value,quote=True)+x.group(1),tag,count=1,flags=re.I)
    return re.sub(r'<meta\\b[^>]*>',change,s,flags=re.I)
def main():
    assert len(META)==11
    warnings=[]
    for i,(filename,(title,description)) in enumerate(META.items(),1):
        en=(ROOT/filename).read_text(encoding='utf-8')
        target=ROOT/'cs'/filename
        cs=target.read_text(encoding='utf-8')
        assert re.search(r'<title>.*?</title>',cs,re.I|re.S),filename
        cs=re.sub(r'<title>.*?</title>',lambda m:'<title>'+html.escape(title)+'</title>',cs,count=1,flags=re.I|re.S)
        for key,val in (('description',description),('og:description',description),('twitter:description',description),('og:title',title),('twitter:title',title)):
            cs=set_meta(cs,key,val)
        for old,new in REPLACE.get(filename,[]):
            if old not in cs:warnings.append(filename+': '+old[:50])
            cs=cs.replace(old,new)
        assert sig(en)==sig(cs),filename+' DOM changed'
        assert script_parts(en,'style')==script_parts(cs,'style'),filename+' CSS changed'
        def js(s):return re.findall(r'<script\\b(?![^>]*application/ld\\+json)[^>]*>([\\s\\S]*?)</script>',s,re.I)
        assert js(en)==js(cs),filename+' JavaScript changed'
        assert prices(en)==prices(cs),filename+' price change: '+repr((prices(en),prices(cs)))
        assert len(re.findall(r'<h1(?:\\s|>)',cs,re.I))==1,filename+' H1'
        target.write_text(cs,encoding='utf-8')
        print('CS_EDITORIAL',i,'/11',filename,'PASS',flush=True)
    print('CS_EDITORIAL_WARNINGS',warnings,flush=True)
if __name__=='__main__':main()
