from pathlib import Path
import re, xml.etree.ElementTree as ET
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); fs=list((r/"hi").glob("*.html")); errs=[]
for f in fs:
 s=f.read_text(encoding="utf-8")
 checks={"lang":'<html lang="hi">' in s,"h1":len(re.findall(r"<h1>",s))==1,"title":"<title>" in s,"canonical":'rel="canonical"' in s,"sponsored":'rel="sponsored nofollow"' in s}
 errs += [(f.name,k) for k,v in checks.items() if not v]
ET.parse(r/"sitemap.xml"); sm=(r/"sitemap.xml").read_text(encoding="utf-8")
print("HI",len(fs),"ERRORS",errs,"HI_SITEMAP",sm.count("/hi/"),"XML_OK")
