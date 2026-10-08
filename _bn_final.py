from pathlib import Path
import re,xml.etree.ElementTree as ET
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); fs=list((r/"bn").glob("*.html")); names={f.name for f in fs}; e=[]
for f in fs:
 s=f.read_text(encoding="utf-8")
 tests={"lang":'<html lang="bn">' in s,"h1":len(re.findall(r"<h1>",s))==1,"title":len(re.findall(r"<title>",s))==1,"canonical":len(re.findall(r'rel="canonical"',s))==1,"bn":'hreflang="bn"' in s,"rel":'rel="sponsored nofollow"' in s}
 e += [(f.name,k) for k,v in tests.items() if not v]
 for h in re.findall(r'href="([^"]+\.html)"',s):
  if "/" not in h and h not in names:e.append((f.name,"broken:"+h))
ET.parse(r/"sitemap.xml"); sm=(r/"sitemap.xml").read_text(encoding="utf-8")
print("PAGES",len(fs),"ERRORS",e,"SITEMAP_BN",sm.count("/bn/"))
