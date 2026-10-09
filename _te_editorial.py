#!/usr/bin/env python3
"""Editorial Telugu localization of headings and metadata, preserving source structure."""
from pathlib import Path
import html
import re
import sys
from _te_translate_full import PAGES, ROOT, validate

SEO=[["n8n కోసం VPS $0.07/Day నుంచి — ప్లాన్‌లు, సర్వర్ ఎంపిక మార్గదర్శిని","<em>n8n</em> కోసం VPS","రోజుకు $0.07 నుంచి లభించే n8n VPS కాన్ఫిగరేషన్‌లను పోల్చండి. చిన్న ఆటోమేషన్‌లు, ప్రొడక్షన్ వర్క్‌ఫ్లోలు, డేటా ప్రాసెసింగ్, AI పనుల కోసం CPU, RAM, స్టోరేజ్, ట్రాఫిక్ అవసరాలకు సరిపోయే ఎంపికను కనుగొనండి."],["2026లో n8n కోసం ఉత్తమ VPS: 6 ప్రొవైడర్ల పోలిక","n8n కోసం ఉత్తమ VPS: 6 ప్రొవైడర్ల ఎంపికలు","n8n కోసం 6 VPS ఎంపికలను సెటప్, నియంత్రణ, బ్యాకప్, సపోర్ట్, మైగ్రేషన్, ప్రాంతం, స్కేలింగ్ ఆధారంగా పోల్చండి. మీ వర్క్‌లోడ్‌కు సరిపోయే హోస్టింగ్ నమూనాను ఎంచుకోండి."],["మా గురించి | n8nVPS","n8nVPS గురించి","స్వయంగా హోస్ట్ చేసే n8n కోసం VPS సామర్థ్యం, ప్రొడక్షన్ మౌలిక సదుపాయాలపై స్వతంత్ర మార్గదర్శకమైన n8nVPS గురించి తెలుసుకోండి."],["n8n బ్యాకప్ మరియు పునరుద్ధరణ","n8n బ్యాకప్ మరియు పునరుద్ధరణ","VPSలో స్వయంగా హోస్ట్ చేసిన n8nకు బ్యాకప్, పునరుద్ధరణ: PostgreSQL లేదా SQLite, వర్క్‌ఫ్లోలు, క్రెడెన్షియల్స్, ఎన్‌క్రిప్షన్ కీ, బైనరీ డేటా, సర్వర్ వెలుపల కాపీలు, రీస్టోర్ పరీక్షలు."],["సంప్రదించండి | n8nVPS","సంప్రదించండి","సవరణలు, ప్రాజెక్ట్ సంబంధిత ప్రశ్నలు, వ్యాపార విచారణల కోసం n8nVPSను సంప్రదించండి."],["VPSలో n8n ఇన్‌స్టాల్ చేయడం — Docker, PostgreSQL","VPSలో n8n ఇన్‌స్టాల్ చేయండి","Docker Compose, PostgreSQL, శాశ్వత స్టోరేజ్, HTTPS, రివర్స్ ప్రాక్సీ, సరైన వెబ్‌హుక్ కాన్ఫిగరేషన్‌తో VPSలో n8n ఇన్‌స్టాల్ చేయండి."],["n8n Cloud vs Self-Hosted: ఖర్చు, నియంత్రణ","n8n Cloud vs Self-Hosted","ఖర్చు, మౌలిక సదుపాయాలపై నియంత్రణ, నిర్వహణ, డేటా స్థానం, స్కేలింగ్, సాంకేతిక బాధ్యతల ఆధారంగా n8n Cloudను స్వయంగా హోస్ట్ చేసే VPSతో పోల్చండి."],["n8n VPS అవసరాలు — RAM, CPU, స్టోరేజ్","n8n VPS అవసరాలు","n8n VPS కోసం RAM, CPU, SSD స్టోరేజ్, PostgreSQL, Docker, ఒకేసారి నడిచే పనుల సంఖ్య, ప్రొడక్షన్ వర్క్‌లోడ్‌కు తగిన సర్వర్ సామర్థ్యాన్ని తెలుసుకోండి."],["గోప్యతా విధానం | n8nVPS","గోప్యత","వెబ్ అనలిటిక్స్, అనుబంధ భాగస్వామి లింకుల ప్రకటనతో సహా n8nVPS గోప్యతా విధానం."],["VPSలో n8nను సురక్షితంగా నిర్వహించడం","VPSలో n8nను సురక్షితంగా ఉంచండి","HTTPS, రివర్స్ ప్రాక్సీ, ఫైర్‌వాల్, SSH భద్రత, ప్రైవేట్ PostgreSQL, ఎన్‌క్రిప్షన్ కీ రక్షణ, SSRF నియంత్రణలు, భద్రతా తనిఖీలతో స్వయంగా హోస్ట్ చేసిన n8n VPSను రక్షించండి."],["n8n Queue Mode — Redis, వర్కర్లతో స్కేలింగ్","n8n Queue Mode","n8nకు Queue Mode ఎప్పుడు అవసరమో, Redis, వర్కర్లు పనులను ఎలా స్కేల్ చేస్తాయో, వర్కర్ల సమాంతర సామర్థ్యం, PostgreSQL అవసరాలు, పర్యవేక్షణ, VPS పరిమాణం గురించి తెలుసుకోండి."]]
EYEBROWS={"CHOOSE THE RESOURCES YOUR WORKFLOWS NEED":"మీ వర్క్‌ఫ్లోలకు అవసరమైన వనరులను ఎంచుకోండి","FROM YOUR AUTOMATION TO YOUR SERVER":"ఆటోమేషన్ అవసరాల నుంచి సర్వర్ ఎంపిక వరకు","KNOW WHAT TO SELECT":"ఏది ఎంచుకోవాలో తెలుసుకోండి","CONTROL OR MANAGED CONVENIENCE":"సొంత నియంత్రణ లేదా నిర్వహిత సేవ","BUY THE RESOURCE YOUR WORKFLOWS USE":"మీ వర్క్‌ఫ్లోలకు సరిపోయే వనరులను కొనుగోలు చేయండి","A CLEAR GROWTH PATH":"విస్తరణకు స్పష్టమైన మార్గం","COMPLETE YOUR DEPLOYMENT":"డిప్లాయ్‌మెంట్‌ను పూర్తి చేయండి","PUT YOUR BUDGET WHERE IT HELPS":"అవసరమైన వనరులకే బడ్జెట్‌ను కేటాయించండి","A BUDGET YOU CAN FOLLOW":"స్పష్టమైన బడ్జెట్ ప్రణాళిక","BUILD YOUR REAL MONTHLY BUDGET":"వాస్తవ నెలవారీ వ్యయాన్ని లెక్కించండి","NEXT STEPS":"తర్వాతి దశలు","BUYING QUESTIONS ANSWERED":"కొనుగోలుకు సంబంధించిన ప్రశ్నలకు సమాధానాలు","CONFIGURATION REFERENCES":"కాన్ఫిగరేషన్‌కు సంబంధించిన ఆధారాలు","PROVIDER COMPARISON · REVIEWED 8 OCTOBER 2026":"ప్రొవైడర్ల పోలిక · 8 అక్టోబర్ 2026న సమీక్షించబడింది","SIX OPTIONS · ONE SET OF BUYING CRITERIA":"6 ఎంపికలు · ఒకే కొనుగోలు ప్రమాణాలు","QUICK SHORTLIST":"త్వరిత ఎంపికల జాబితా","WHAT TO COMPARE":"దేనిని పోల్చాలి","PRICE LENS":"ధరల పోలిక","DECIDE BY SCENARIO":"వాడుక ఆధారంగా నిర్ణయించండి","DO NOT MIX THE TWO DECISIONS":"రెండు వేర్వేరు నిర్ణయాలను కలపవద్దు","EDITORIAL METHOD":"మూల్యాంకన విధానం","BACKUP & RECOVERY":"బ్యాకప్ మరియు పునరుద్ధరణ","QUICK CHECKLIST":"త్వరిత తనిఖీ జాబితా","TWO BACKUP LEVELS":"రెండు బ్యాకప్ స్థాయిలు","DATABASE":"డేటాబేస్","CRITICAL SECRET":"అత్యంత ముఖ్యమైన రహస్య కీ","FILES & BINARY DATA":"ఫైళ్లు మరియు బైనరీ డేటా","OFF-SERVER STRATEGY":"సర్వర్ వెలుపల బ్యాకప్ వ్యూహం","RESTORE ORDER":"పునరుద్ధరణ క్రమం","RESTORE TEST":"పునరుద్ధరణ పరీక్ష","CLI BACKUP LIMITS":"CLI బ్యాకప్ పరిమితులు","RECOVERY OBJECTIVES":"పునరుద్ధరణ లక్ష్యాలు","RECOVERY KEY":"పునరుద్ధరణ కీ","DOCKER INSTALLATION":"Docker ఇన్‌స్టాలేషన్","PREREQUISITES":"ముందస్తు అవసరాలు","DEPLOYMENT STACK":"డిప్లాయ్‌మెంట్ నిర్మాణం","COPY-AND-ADAPT INSTALLATION":"ఉదాహరణ ఆధారంగా ఇన్‌స్టాలేషన్","CONFIGURATION":"కాన్ఫిగరేషన్","PERSISTENCE":"శాశ్వత డేటా నిల్వ","POSTGRESQL":"PostgreSQL","HTTPS & PROXY":"HTTPS మరియు రివర్స్ ప్రాక్సీ","FIRST START":"మొదటి ప్రారంభం","UPDATES":"అప్‌డేట్‌లు","COMMON FAILURES":"సాధారణ సమస్యలు","POST-DEPLOY VERIFICATION":"డిప్లాయ్‌మెంట్ తర్వాత తనిఖీ","HOSTING DECISION":"హోస్టింగ్ ఎంపిక","QUICK VERDICT":"సంక్షిప్త నిర్ణయం","SIDE-BY-SIDE":"పక్కపక్కనే పోలిక","ONE DECISION · TWO OPERATING MODELS":"ఒక నిర్ణయం · రెండు నిర్వహణ నమూనాలు","WORKFLOW FREQUENCY CHECK":"వర్క్‌ఫ్లో నడిచే తరచుదనాన్ని తనిఖీ చేయండి","A THIRD OPERATING MODEL":"మూడో నిర్వహణ నమూనా","REAL COST MODEL":"వాస్తవ ఖర్చు నమూనా","DECISION PATH":"నిర్ణయించే విధానం","TOTAL COST OF OWNERSHIP":"మొత్తం నిర్వహణ ఖర్చు","CONTROL & DATA":"నియంత్రణ మరియు డేటా","OPERATIONS":"రోజువారీ నిర్వహణ","SCALING":"సామర్థ్య విస్తరణ","DECISION FRAMEWORK":"నిర్ణయ ప్రమాణాలు","EDITION & LICENSE BOUNDARY":"ఎడిషన్ మరియు లైసెన్స్ పరిమితులు","LONG-TERM OPERATIONS":"దీర్ఘకాలిక నిర్వహణ","MIGRATION DECISION":"మైగ్రేషన్ నిర్ణయం","SERVER REQUIREMENTS":"సర్వర్ అవసరాలు","QUICK REQUIREMENTS":"ముఖ్యమైన అవసరాలు","RESOURCE BUNDLES · VERIFIED PRICING":"వనరుల ప్యాకేజీలు · ధృవీకరించిన ధరలు","MINIMUM VS PRACTICAL CAPACITY":"కనీస సామర్థ్యం మరియు ఆచరణయోగ్యమైన సామర్థ్యం","RAM & CPU":"RAM మరియు CPU","MEASURE BEFORE YOU UPGRADE":"అప్‌గ్రేడ్‌కు ముందు వినియోగాన్ని కొలవండి","DATABASE & STORAGE":"డేటాబేస్ మరియు స్టోరేజ్","DISK CAPACITY":"డిస్క్ సామర్థ్యం","SYSTEM REQUIREMENTS":"సిస్టమ్ అవసరాలు","CONCURRENCY":"ఒకేసారి నడిచే పనులు","SIZING CHECKLIST":"సర్వర్ సామర్థ్య తనిఖీ జాబితా","ENTRY TIER & STORAGE I/O":"ప్రారంభ ప్లాన్ మరియు స్టోరేజ్ I/O","PRODUCTION SECURITY":"ప్రొడక్షన్ భద్రత","NETWORK EDGE":"నెట్‌వర్క్ ప్రవేశ స్థాయి","VPS HARDENING":"VPS భద్రతను బలోపేతం చేయండి","DATABASE & REDIS":"డేటాబేస్ మరియు Redis","N8N SECRETS":"n8n రహస్య కీలు","WORKFLOW RISK":"వర్క్‌ఫ్లో ప్రమాదాలు","AUDIT & UPDATES":"ఆడిట్ మరియు అప్‌డేట్‌లు","DEPLOYMENT ORDER":"డిప్లాయ్‌మెంట్ క్రమం","ACCOUNT & PLATFORM CONTROLS":"ఖాతా మరియు ప్లాట్‌ఫారమ్ భద్రత","QUICK DECISION":"త్వరిత నిర్ణయం","ARCHITECTURE":"సిస్టమ్ నిర్మాణం","CORE REQUIREMENTS":"ప్రధాన అవసరాలు","WORKER CONCURRENCY":"వర్కర్ల సమాంతర సామర్థ్యం","WEBHOOKS":"వెబ్‌హుక్‌లు","BINARY DATA":"బైనరీ డేటా","MONITORING":"పర్యవేక్షణ","SCALING PATH":"సామర్థ్యం పెంచే మార్గం","HIGH AVAILABILITY BOUNDARY":"అధిక లభ్యత పరిమితులు","FAQ":"తరచుగా అడిగే ప్రశ్నలు","ABOUT":"మా గురించి","CONTACT":"సంప్రదించండి","PRIVACY":"గోప్యత"}
EYEBROW_RE=re.compile(r'(<p\b[^>]*class=["\'][^"\']*\beyebrow\b[^"\']*["\'][^>]*>)([\s\S]*?)(</p>)',re.I)
TAG_SEQ=re.compile(r'</?([A-Za-z][\w-]*)\b[^>]*>')
def signature(s):
    return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower() for m in TAG_SEQ.finditer(s) if m.group(1).lower() not in ('link','meta')]

def polish(index):
    enpath,mrpath=PAGES[index]
    source=(ROOT/enpath).read_text(encoding="utf-8")
    target=ROOT/mrpath
    initial=target.read_text(encoding="utf-8")
    title,h1,desc=SEO[index]
    text=re.sub(r'<title>[\s\S]*?</title>',lambda m:"<title>"+html.escape(title,quote=False)+"</title>",initial,count=1,flags=re.I)
    def rewrite_meta(m):
        tag=m.group()
        match=re.search(r'\b(?:name|property)=["\']([^"\']+)["\']',tag,re.I)
        if not match:return tag
        field=match.group(1).lower()
        if field in ("og:title","twitter:title"): value=title
        elif field in ("description","og:description","twitter:description"): value=desc
        else:return tag
        return re.sub(r'\bcontent=(["\'])(.*?)\1',lambda x:'content='+x.group(1)+html.escape(value,quote=True)+x.group(1),tag,flags=re.I|re.S)
    text=re.sub(r'<meta\b[^>]*>',rewrite_meta,text,flags=re.I)
    if len(re.findall(r'<h1\b',text,re.I))!=1:raise ValueError("Must have one H1: "+mrpath)
    text=re.sub(r'(<h1\b[^>]*>)([\s\S]*?)(</h1>)',lambda m:m.group(1)+h1+m.group(3),text,count=1,flags=re.I)
    original_en=EYEBROW_RE.findall(source)
    targets=EYEBROW_RE.findall(text)
    if len(targets)!=len(original_en):raise AssertionError("Eyebrow count mismatch: "+mrpath)
    cursor=[0]
    def replace_eyebrow(m):
        i=cursor[0];cursor[0]+=1
        original=html.unescape(re.sub(r'<[^>]*>','',original_en[i][1])).strip()
        translation=EYEBROWS.get(original)
        if translation is None or re.search(r'<[^>]+>',m.group(2)):return m.group()
        return m.group(1)+html.escape(translation,quote=False)+m.group(3)
    text=EYEBROW_RE.sub(replace_eyebrow,text)
    if signature(source)!=signature(text):raise AssertionError("Editorial modified HTML structure "+mrpath)
    validate(source,text,enpath,mrpath)
    target.write_text(text,encoding="utf-8")
    print("TELUGU_EDITORIAL_PASS",mrpath,"labels",len(targets),flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit("Usage: python _te_editorial.py PAGE_INDEX")
    polish(int(sys.argv[1]))
