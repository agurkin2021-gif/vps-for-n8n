from pathlib import Path
import re,xml.etree.ElementTree as ET
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); sm=(r/"sitemap.xml").read_text(encoding="utf-8"); ET.parse(r/"sitemap.xml")
for lang in ["hi","bn"]:
 fs=list((r/lang).glob("*.html")); names={f.name for f in fs}; e=[]
 for f in fs:
  s=f.read_text(encoding="utf-8")
  for k,v in {"h1":len(re.findall(r"<h1>",s))==1,"title":len(re.findall(r"<title>",s))==1,"canonical":len(re.findall(r'rel="canonical"',s))==1,"lang":f'<html lang="{lang}">' in s,"sponsored":'rel="sponsored nofollow"' in s}.items():
   if not v:e.append((f.name,k))
  for h in re.findall(r'href="([^"]+\.html)"',s):
   if "/" not in h and h not in names:e.append((f.name,"broken"))
 print(lang,len(fs),len(e),sm.count("/"+lang+"/"))
