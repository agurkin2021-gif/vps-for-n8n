from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); fs=[f for f in r.rglob("*.html") if ".git" not in f.parts and f.name!="404.html" and "n8n<span>VPS</span>" in f.read_text(encoding="utf-8",errors="ignore")];e=[]
for f in fs:
 s=f.read_text(encoding="utf-8")
 for code in ["en","es","ru","pt-BR","de","hi","bn","ja","pa"]:
  if f'hreflang="{code}"' not in s:e.append((str(f.relative_to(r)),code))
 if "<footer" not in s:e.append((str(f.relative_to(r)),"footer"))
 menu=re.search(r'<div class="lang-menu">(.*?)</div>',s,re.S)
 if not menu or "../ja/" not in menu.group(1) and f.parent==r:e.append((str(f.relative_to(r)),"ja-menu"))
 if not menu or "../pa/" not in menu.group(1) and f.parent==r:e.append((str(f.relative_to(r)),"pa-menu"))
print("PAGES",len(fs),"ERRORS",len(e),e[:20])
