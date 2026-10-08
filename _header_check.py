from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site");e=[];n=0
for f in r.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html":continue
 s=f.read_text(encoding="utf-8",errors="ignore")
 if "n8n<span>VPS</span>" not in s:continue
 n+=1;m=re.search(r'<div class="lang-menu">(.*?)</div>',s,re.S)
 if not m:e.append((str(f.relative_to(r)),"no-menu"));continue
 z=m.group(1)
 for needle in ["English","Español","Русский","Português","Deutsch","हिन्दी","বাংলা","日本語","ਪੰਜਾਬੀ"]:
  if needle not in z:e.append((str(f.relative_to(r)),needle))
css=(r/"styles.css").read_text(encoding="utf-8")
print("PAGES",n,"MENU_ERRORS",len(e),"CSS_GAP_FIXED", "top:100%" in css and "padding-bottom:8px" in css,"ERROR_SAMPLE",e[:5])
