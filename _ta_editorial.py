#!/usr/bin/env python3
"""Editorial Tamil polish for titles, H1 and metadata while preserving HTML structure."""
from pathlib import Path
import html,re,sys
from _ta_translate_full import PAGES,ROOT,validate

SEO=[
["n8n-க்கு VPS $0.07/நாள் முதல் — திட்டங்கள் மற்றும் சர்வர் தேர்வு","n8n-க்கு VPS","$0.07/நாள் முதல் கிடைக்கும் n8n VPS திட்டங்களை ஒப்பிடுங்கள். CPU, RAM, storage, traffic மற்றும் production workload தேவைகளுக்கு ஏற்ற server configuration-ஐ தேர்வு செய்யுங்கள்."],
["2026-ல் n8n-க்கு சிறந்த VPS — 6 வழங்குநர்கள் ஒப்பீடு","n8n-க்கு சிறந்த VPS","Setup, control, backup, support, migration, region மற்றும் scaling அடிப்படையில் n8n-க்கு ஏற்ற 6 VPS விருப்பங்களை ஒப்பிடுங்கள்."],
["n8nVPS பற்றி | n8nVPS","n8nVPS பற்றி","Self-hosted n8n-க்கு VPS sizing மற்றும் production infrastructure குறித்து வழங்கும் சுயாதீன வழிகாட்டியான n8nVPS பற்றி அறியுங்கள்."],
["n8n Backup மற்றும் Restore — முழுமையான வழிகாட்டி","n8n Backup மற்றும் Restore","Self-hosted n8n-க்கான database, workflows, credentials, encryption key, binary data, off-server copies மற்றும் restore testing பற்றிய backup வழிகாட்டி."],
["தொடர்பு | n8nVPS","தொடர்பு","திருத்தங்கள், திட்டம் தொடர்பான கேள்விகள் மற்றும் வணிக விசாரணைகளுக்காக n8nVPS-ஐ தொடர்புகொள்ளுங்கள்."],
["VPS-ல் n8n நிறுவுவது — Docker மற்றும் PostgreSQL","VPS-ல் n8n நிறுவுவது","Docker Compose, PostgreSQL, persistent storage, HTTPS, reverse proxy மற்றும் சரியான webhook configuration உடன் VPS-ல் n8n நிறுவுங்கள்."],
["n8n Cloud vs Self-Hosted — செலவு மற்றும் கட்டுப்பாடு","n8n Cloud vs Self-Hosted","செலவு, infrastructure control, maintenance, data location, scaling மற்றும் technical responsibility அடிப்படையில் n8n Cloud மற்றும் self-hosted VPS-ஐ ஒப்பிடுங்கள்."],
["n8n VPS தேவைகள் — RAM, CPU மற்றும் Storage","n8n VPS தேவைகள்","n8n VPS-க்கு தேவையான RAM, CPU, SSD storage, PostgreSQL, Docker, concurrency மற்றும் production workload sizing-ஐ அறியுங்கள்."],
["தனியுரிமைக் கொள்கை | n8nVPS","தனியுரிமை","Web analytics மற்றும் affiliate link disclosure உட்பட n8nVPS-ன் தனியுரிமைக் கொள்கை."],
["VPS-ல் n8n-ஐ பாதுகாப்பாக இயக்குவது","VPS-ல் n8n-ஐ பாதுகாப்பாக வைத்தல்","HTTPS, reverse proxy, firewall, SSH hardening, private PostgreSQL, encryption key protection, SSRF controls மற்றும் security checks மூலம் self-hosted n8n VPS-ஐ பாதுகாக்குங்கள்."],
["n8n Queue Mode — Redis மற்றும் Workers மூலம் Scaling","n8n Queue Mode","n8n-க்கு Queue Mode எப்போது தேவை, Redis மற்றும் workers எவ்வாறு scale செய்கின்றன, worker concurrency, PostgreSQL தேவைகள், monitoring மற்றும் VPS sizing குறித்து அறியுங்கள்."]
]

def signature(s):
    return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower()
            for m in re.finditer(r'</?([A-Za-z][\w-]*)\b[^>]*>',s)
            if m.group(1).lower() not in ("link","meta")]

def polish(i):
    enpath,tapath=PAGES[i]
    source=(ROOT/enpath).read_text(encoding="utf-8")
    target=ROOT/tapath
    text=target.read_text(encoding="utf-8")
    title,h1,desc=SEO[i]
    text=re.sub(r'<title>[\s\S]*?</title>',lambda m:"<title>"+html.escape(title,quote=False)+"</title>",text,count=1,flags=re.I)
    def meta(m):
        tag=m.group()
        a=re.search(r'\b(?:name|property)=["\']([^"\']+)["\']',tag,re.I)
        if not a:return tag
        field=a.group(1).lower()
        if field in ("og:title","twitter:title"):value=title
        elif field in ("description","og:description","twitter:description"):value=desc
        else:return tag
        return re.sub(r'\bcontent=(["\'])(.*?)\1',lambda x:'content='+x.group(1)+html.escape(value,quote=True)+x.group(1),tag,flags=re.I|re.S)
    text=re.sub(r'<meta\b[^>]*>',meta,text,flags=re.I)
    text=re.sub(r'(<h1\b[^>]*>)([\s\S]*?)(</h1>)',lambda m:m.group(1)+h1+m.group(3),text,count=1,flags=re.I)
    if signature(source)!=signature(text):raise AssertionError("HTML structure changed: "+tapath)
    validate(source,text,enpath,tapath)
    target.write_text(text,encoding="utf-8")
    print("TAMIL_EDITORIAL_PASS",tapath,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit("Usage: python _ta_editorial.py PAGE_INDEX")
    polish(int(sys.argv[1]))
