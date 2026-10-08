from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site");e=[];n=0
for f in r.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html":continue
 s=f.read_text(encoding="utf-8",errors="ignore")
 if "n8n<span>VPS</span>" not in s:continue
 n+=1;m=re.search(r'<div class="lang-menu">(.*?)</div>',s,re.S)
 if not m:e.append((str(f.relative_to(r)),"menu"));continue
 menu=m.group(1)
 if "ja/" not in menu:e.append((str(f.relative_to(r)),"ja"))
 if "pa/" not in menu:e.append((str(f.relative_to(r)),"pa"))
 if s.count("<footer")!=1:e.append((str(f.relative_to(r)),"footer"))
 if s.count("</footer>")!=1:e.append((str(f.relative_to(r)),"footer-close"))
print("PAGES",n,"ERRORS",len(e),e[:10])
