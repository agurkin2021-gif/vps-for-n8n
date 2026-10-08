from pathlib import Path
import re,urllib.request,xml.etree.ElementTree as ET
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
langs={"en":"","es":"es","ru":"ru","pt-br":"pt-br","de":"de","hi":"hi","bn":"bn","ja":"ja","pa":"pa"}
required=["workloads","save","requirements","architecture","production","operations","decision","environment","faq"]
english_sentences=["Size the server from","Minimum specs are not","Queue mode adds","Persistent volumes and private","Domain, reverse proxy","Back up DB","Control execution history","OS, network, Docker","Stable public HTTPS","Pin versions and back up","Watch OOM","Firewall, SSH keys","Infrastructure and data control","Lower operational overhead","Linux, Docker, persistent","Ubuntu/Debian with root","Survive container recreation","Firewall control and stable","2 GB can suit","Not in regular mode","Docker/Compose with PostgreSQL"]
allerrs=[]
for lang,folder in langs.items():
 f=r/"index.html" if not folder else r/folder/"index.html";s=f.read_text(encoding="utf-8",errors="ignore");e=[]
 if len(re.findall(r"<h1>",s))!=1:e.append("H1_COUNT")
 if len(re.findall(r"<title>",s))!=1:e.append("TITLE_COUNT")
 if len(re.findall(r'rel="canonical"',s))!=1:e.append("CANONICAL")
 for sec in required:
  if f'id="{sec}"' not in s:e.append("MISSING_"+sec)
 if 'class="hero"' not in s:e.append("NO_HERO")
 if '<nav class="main-nav">' not in s:e.append("NO_NAV")
 if '<footer' not in s:e.append("NO_FOOTER")
 if '日本語' not in s or 'ਪੰਜਾਬੀ' not in s:e.append("MENU_LANGS")
 if lang!="en":
  hits=[x for x in english_sentences if x in s]
  if hits:e.append("EN_TEXT:"+str(len(hits)))
 # local links
 names={x.name for x in f.parent.glob("*.html")}
 for h in re.findall(r'href="([^"#?]+\.html)',s):
  if "/" not in h and h not in names:e.append("BROKEN:"+h)
 # live server
 url="http://127.0.0.1:8878/"+(folder+"/" if folder else "")
 try:
  live=urllib.request.urlopen(url,timeout=2).read().decode("utf-8")
  if len(live)!=len(s):e.append("LIVE_MISMATCH")
 except Exception:e.append("LIVE_FAIL")
 print(lang,"OK" if not e else "|".join(e))
 allerrs.extend((lang,x) for x in e)
ET.parse(r/"sitemap.xml")
print("TOTAL_ERRORS",len(allerrs))
