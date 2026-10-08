from pathlib import Path
import re,xml.etree.ElementTree as ET
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); fs=list((r/"ja").glob("*.html")); names={f.name for f in fs}; e=[]
for f in fs:
 s=f.read_text(encoding="utf-8")
 for k,v in {"lang":'<html lang="ja">' in s,"h1":len(re.findall(r"<h1>",s))==1,"title":len(re.findall(r"<title>",s))==1,"canonical":len(re.findall(r'rel="canonical"',s))==1,"ja":'hreflang="ja"' in s,"rel":'rel="sponsored nofollow"' in s}.items():
  if not v:e.append((f.name,k))
 for h in re.findall(r'href="([^"]+\.html)"',s):
  if "/" not in h and h not in names:e.append((f.name,"broken:"+h))
ET.parse(r/"sitemap.xml"); sm=(r/"sitemap.xml").read_text(encoding="utf-8")
print("JA",len(fs),"ERRORS",e,"SITEMAP",sm.count("/ja/"))
