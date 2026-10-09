#!/usr/bin/env python3
"""Editorial Marathi localization of headings and metadata, preserving source structure."""
from pathlib import Path
import html
import re
import sys
from _mr_translate_full import PAGES, ROOT, validate

SEO=[["n8n साठी VPS $0.07/Day पासून — प्लॅन व सर्व्हर निवड मार्गदर्शक","<em>n8n</em> साठी VPS","$0.07/day पासून उपलब्ध n8n VPS पर्यायांची तुलना करा. साधी ऑटोमेशन, उत्पादनातील वर्कफ्लो, डेटा प्रक्रिया आणि AI साठी CPU, RAM, स्टोरेज व ट्रॅफिकनुसार योग्य पर्याय निवडा."],["2026 मध्ये n8n साठी सर्वोत्तम VPS: 6 प्रदात्यांची तुलना","n8n साठी सर्वोत्तम VPS: 6 प्रदात्यांचे पर्याय","n8n साठी 6 VPS पर्यायांची सेटअप पद्धत, नियंत्रण, बॅकअप, सहाय्य, स्थलांतर, सर्व्हरचे स्थान आणि स्केलिंग यांनुसार तुलना करा. तुमच्या कामासाठी योग्य प्रदाता निवडा."],["आमच्याबद्दल | n8nVPS","n8nVPS बद्दल","n8nVPS बद्दल माहिती: स्वतः होस्ट केलेल्या n8n साठी VPS संसाधनांची निवड आणि उत्पादनातील पायाभूत सुविधांबाबत स्वतंत्र मार्गदर्शक."],["n8n बॅकअप आणि पुनर्संचयन","n8n बॅकअप आणि पुनर्संचयन","VPS वरील स्वतः होस्ट केलेल्या n8n चा बॅकअप आणि पुनर्संचयन: PostgreSQL किंवा SQLite, वर्कफ्लो, क्रेडेन्शियल्स, एन्क्रिप्शन की, बायनरी डेटा, सर्व्हरबाहेरील प्रती आणि पुनर्संचयन चाचणी."],["संपर्क | n8nVPS","संपर्क","दुरुस्त्या, प्रकल्पाविषयी प्रश्न आणि व्यावसायिक चौकशीसाठी n8nVPS शी संपर्क साधा."],["VPS वर n8n इन्स्टॉल करा — Docker व PostgreSQL","VPS वर n8n इन्स्टॉल करा","Docker Compose, PostgreSQL, कायमस्वरूपी स्टोरेज, HTTPS, रिव्हर्स प्रॉक्सी आणि योग्य वेबहुक कॉन्फिगरेशनसह VPS वर n8n इन्स्टॉल करा."],["n8n Cloud विरुद्ध Self-Hosted: खर्च आणि नियंत्रण","n8n Cloud विरुद्ध Self-Hosted","खर्च, पायाभूत सुविधांवरील नियंत्रण, देखभाल, डेटाचे स्थान, स्केलिंग आणि तांत्रिक जबाबदाऱ्या यांच्या आधारावर n8n Cloud व स्वतः होस्ट केलेल्या VPS ची तुलना करा."],["n8n VPS आवश्यकता — RAM, CPU आणि स्टोरेज","n8n VPS आवश्यकता","n8n VPS साठी RAM, CPU, SSD स्टोरेज, PostgreSQL, Docker, समांतर अंमलबजावणी आणि उत्पादनातील वर्कलोडनुसार सर्व्हरची क्षमता कशी ठरवावी ते जाणून घ्या."],["गोपनीयता धोरण | n8nVPS","गोपनीयता","n8nVPS चे गोपनीयता धोरण: विश्लेषण साधने आणि संलग्न भागीदारांच्या लिंकबाबतची माहिती."],["VPS वरील n8n सुरक्षित करा — सुरक्षा मार्गदर्शक","VPS वरील n8n सुरक्षित करा","HTTPS, रिव्हर्स प्रॉक्सी, फायरवॉल, SSH सुरक्षा, खाजगी PostgreSQL, एन्क्रिप्शन कीचे संरक्षण, SSRF नियंत्रण आणि सुरक्षा तपासण्यांनी स्वतः होस्ट केलेला n8n VPS सुरक्षित ठेवा."],["n8n Queue Mode — Redis आणि वर्कर्स","n8n Queue Mode","n8n ला Queue Mode कधी आवश्यक असतो, Redis आणि वर्कर्समुळे अंमलबजावणी कशी वाढवता येते, वर्कर कॉन्करन्सी, PostgreSQL आवश्यकता, निरीक्षण आणि VPS सायझिंग समजून घ्या."]]
EYEBROWS={"CHOOSE THE RESOURCES YOUR WORKFLOWS NEED":"तुमच्या वर्कफ्लोसाठी आवश्यक संसाधने निवडा","FROM YOUR AUTOMATION TO YOUR SERVER":"ऑटोमेशनच्या गरजांपासून सर्व्हरच्या निवडीपर्यंत","KNOW WHAT TO SELECT":"योग्य पर्याय कसा निवडावा","CONTROL OR MANAGED CONVENIENCE":"स्वतःचे नियंत्रण की व्यवस्थापित सोय","BUY THE RESOURCE YOUR WORKFLOWS USE":"वर्कफ्लोसाठी आवश्यक तेवढीच संसाधने घ्या","A CLEAR GROWTH PATH":"वाढीसाठी स्पष्ट मार्ग","COMPLETE YOUR DEPLOYMENT":"डिप्लॉयमेंट पूर्ण करा","PUT YOUR BUDGET WHERE IT HELPS":"बजेट योग्य ठिकाणी वापरा","A BUDGET YOU CAN FOLLOW":"समजण्याजोगे बजेट","BUILD YOUR REAL MONTHLY BUDGET":"खरा मासिक खर्च मोजा","NEXT STEPS":"पुढील पावले","BUYING QUESTIONS ANSWERED":"खरेदीविषयी प्रश्नांची उत्तरे","CONFIGURATION REFERENCES":"कॉन्फिगरेशन संदर्भ","PROVIDER COMPARISON · REVIEWED 8 OCTOBER 2026":"प्रदात्यांची तुलना · 8 ऑक्टोबर 2026 रोजी पुनरावलोकन","SIX OPTIONS · ONE SET OF BUYING CRITERIA":"6 पर्याय · निवडीचे एकसमान निकष","QUICK SHORTLIST":"झटपट निवडक पर्याय","WHAT TO COMPARE":"कशाची तुलना करावी","PRICE LENS":"किमतीचा दृष्टिकोन","DECIDE BY SCENARIO":"वापरानुसार निर्णय घ्या","DO NOT MIX THE TWO DECISIONS":"दोन वेगळे निर्णय एकत्र करू नका","EDITORIAL METHOD":"मूल्यांकन पद्धत","BACKUP & RECOVERY":"बॅकअप आणि पुनर्प्राप्ती","QUICK CHECKLIST":"झटपट तपासणी यादी","TWO BACKUP LEVELS":"बॅकअपचे दोन स्तर","DATABASE":"डेटाबेस","CRITICAL SECRET":"अत्यावश्यक गुप्त की","FILES & BINARY DATA":"फाईल्स आणि बायनरी डेटा","OFF-SERVER STRATEGY":"सर्व्हरबाहेरील बॅकअप योजना","RESTORE ORDER":"पुनर्संचयनाचा क्रम","RESTORE TEST":"पुनर्संचयन चाचणी","CLI BACKUP LIMITS":"CLI बॅकअपच्या मर्यादा","RECOVERY OBJECTIVES":"पुनर्प्राप्तीची उद्दिष्टे","RECOVERY KEY":"पुनर्प्राप्ती की","DOCKER INSTALLATION":"Docker इन्स्टॉलेशन","PREREQUISITES":"पूर्वअटी","DEPLOYMENT STACK":"डिप्लॉयमेंटची रचना","COPY-AND-ADAPT INSTALLATION":"उदाहरण वापरून कॉन्फिगरेशन जुळवा","CONFIGURATION":"कॉन्फिगरेशन","PERSISTENCE":"कायमस्वरूपी डेटा साठवण","POSTGRESQL":"PostgreSQL","HTTPS & PROXY":"HTTPS आणि रिव्हर्स प्रॉक्सी","FIRST START":"पहिली सुरुवात","UPDATES":"अपडेट्स","COMMON FAILURES":"नेहमीच्या अडचणी","POST-DEPLOY VERIFICATION":"डिप्लॉयमेंटनंतरची पडताळणी","HOSTING DECISION":"होस्टिंगचा निर्णय","QUICK VERDICT":"थोडक्यात निष्कर्ष","SIDE-BY-SIDE":"शेजारील तुलना","ONE DECISION · TWO OPERATING MODELS":"एक निर्णय · कामकाजाच्या दोन पद्धती","WORKFLOW FREQUENCY CHECK":"वर्कफ्लोची वारंवारता तपासा","A THIRD OPERATING MODEL":"कामकाजाची तिसरी पद्धत","REAL COST MODEL":"प्रत्यक्ष खर्चाचे गणित","DECISION PATH":"निर्णय घेण्याची पद्धत","TOTAL COST OF OWNERSHIP":"एकूण मालकीचा खर्च","CONTROL & DATA":"नियंत्रण आणि डेटा","OPERATIONS":"दैनंदिन व्यवस्थापन","SCALING":"क्षमता वाढवणे","DECISION FRAMEWORK":"निर्णयाचे निकष","EDITION & LICENSE BOUNDARY":"आवृत्ती आणि परवान्याच्या मर्यादा","LONG-TERM OPERATIONS":"दीर्घकालीन देखभाल","MIGRATION DECISION":"स्थलांतराचा निर्णय","SERVER REQUIREMENTS":"सर्व्हरच्या आवश्यकता","QUICK REQUIREMENTS":"मुख्य आवश्यकता","RESOURCE BUNDLES · VERIFIED PRICING":"संसाधनांचे पर्याय · पडताळलेल्या किमती","MINIMUM VS PRACTICAL CAPACITY":"किमान विरुद्ध व्यवहार्य क्षमता","RAM & CPU":"RAM आणि CPU","MEASURE BEFORE YOU UPGRADE":"अपग्रेड करण्याआधी वापर मोजा","DATABASE & STORAGE":"डेटाबेस आणि स्टोरेज","DISK CAPACITY":"डिस्कची क्षमता","SYSTEM REQUIREMENTS":"प्रणालीच्या आवश्यकता","CONCURRENCY":"समांतर अंमलबजावणी","SIZING CHECKLIST":"क्षमता निवडीची तपासणी यादी","ENTRY TIER & STORAGE I/O":"प्रारंभिक प्लॅन आणि स्टोरेज I/O","PRODUCTION SECURITY":"उत्पादनासाठी सुरक्षा","NETWORK EDGE":"नेटवर्कची सीमा","VPS HARDENING":"VPS अधिक सुरक्षित करा","DATABASE & REDIS":"डेटाबेस आणि Redis","N8N SECRETS":"n8n च्या गुप्त की","WORKFLOW RISK":"वर्कफ्लोचे धोके","AUDIT & UPDATES":"तपासणी आणि अपडेट्स","DEPLOYMENT ORDER":"डिप्लॉयमेंटचा क्रम","ACCOUNT & PLATFORM CONTROLS":"खाते आणि प्लॅटफॉर्म सुरक्षा","QUICK DECISION":"झटपट निर्णय","ARCHITECTURE":"प्रणालीची रचना","CORE REQUIREMENTS":"मूलभूत आवश्यकता","WORKER CONCURRENCY":"वर्कर्सची समांतर क्षमता","WEBHOOKS":"वेबहुक","BINARY DATA":"बायनरी डेटा","MONITORING":"निरीक्षण","SCALING PATH":"क्षमता वाढवण्याचा मार्ग","HIGH AVAILABILITY BOUNDARY":"उच्च उपलब्धतेच्या मर्यादा","FAQ":"वारंवार विचारले जाणारे प्रश्न","ABOUT":"आमच्याबद्दल","CONTACT":"संपर्क","PRIVACY":"गोपनीयता"}
EYEBROW_RE=re.compile(r'(<p\b[^>]*class=["\'][^"\']*\beyebrow\b[^"\']*["\'][^>]*>)([\s\S]*?)(</p>)',re.I)
TAG_SEQ=re.compile(r'</?([A-Za-z][\w-]*)\b[^>]*>')
def signature(s):
    return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower() for m in TAG_SEQ.finditer(s)]

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
    print("MARATHI_EDITORIAL_PASS",mrpath,"labels",len(targets),flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit("Usage: python _mr_editorial.py PAGE_INDEX")
    polish(int(sys.argv[1]))
