from pathlib import Path
import re,xml.etree.ElementTree as ET
root=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); fs=list((root/"hi").glob("*.html")); errs=[]
names={f.name for f in fs}
for f in fs:
 s=f.read_text(encoding="utf-8")
 checks={"lang":'<html lang="hi">' in s,"h1":len(re.findall(r"<h1>",s))==1,"title":len(re.findall(r"<title>",s))==1,"canonical":len(re.findall(r'rel="canonical"',s))==1,"hi_hreflang":'hreflang="hi"' in s,"sponsored":'rel="sponsored nofollow"' in s}
 for k,v in checks.items():
  if not v: errs.append((f.name,k))
 for href in re.findall(r'href="([^"]+\.html)"',s):
  if "/" not in href and href not in names: errs.append((f.name,"broken:"+href))
ET.parse(root/"sitemap.xml"); sm=(root/"sitemap.xml").read_text(encoding="utf-8")
print("PAGES",len(fs),"ERRORS",len(errs),errs,"SITEMAP_HI",sm.count("/hi/"))
