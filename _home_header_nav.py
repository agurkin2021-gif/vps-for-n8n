from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
homes=[r/"index.html"]+[r/x/"index.html" for x in ["es","ru","pt-br","de","hi","bn","ja","pa"]]
nav='<nav class="main-nav"><a href="#workloads">Sizing</a><a href="#requirements">Requirements</a><a href="#architecture">Architecture</a><a href="#faq">FAQ</a></nav>'
for f in homes:
 if not f.exists():continue
 s=f.read_text(encoding="utf-8")
 # normalize any existing nav
 s=re.sub(r'<nav(?: class="main-nav")?>.*?</nav>',nav,s,count=1,flags=re.S)
 if '<nav class="main-nav">' not in s:
  s=s.replace('</a><div class="lang-switch">','</a>'+nav+'<div class="lang-switch">',1)
 f.write_text(s,encoding="utf-8")
css=r/"styles.css";s=css.read_text(encoding="utf-8")
# replace header/nav rules with grid for stable geometry
s=re.sub(r'header\{[^}]*\}', 'header{height:76px;display:grid;grid-template-columns:180px 1fr 180px;align-items:center;width:100%;max-width:1180px;margin:0 auto;padding:0 28px;column-gap:32px}',s,count=1)
s=re.sub(r'nav\{[^}]*\}', 'nav{display:flex;justify-content:center;gap:32px;margin:0}',s,count=1)
s=s.replace(".lang-switch{position:relative;margin-left:18px}",".lang-switch{position:relative;justify-self:end;margin:0}")
# mobile grid reset
s=s.replace("@media(max-width:850px){.decision-row","@media(max-width:850px){header{grid-template-columns:1fr auto;column-gap:18px}.decision-row")
css.write_text(s,encoding="utf-8")
print("HOME_HEADERS",len([f for f in homes if f.exists()]))
