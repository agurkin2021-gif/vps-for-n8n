from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
langs=[("","English"),("es/","Español"),("ru/","Русский"),("pt-br/","Português"),("de/","Deutsch"),("hi/","हिन्दी"),("bn/","বাংলা"),("ja/","日本語"),("pa/","ਪੰਜਾਬੀ")]
dirs={"es","ru","pt-br","de","hi","bn","ja","pa"}
n=0
for f in r.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html":continue
 s=f.read_text(encoding="utf-8",errors="ignore")
 if "n8n<span>VPS</span>" not in s:continue
 pre="../" if f.parent.name in dirs else ""
 menu="".join(f'<a href="{pre+p if p else (pre or "./")}">{name}</a>' for p,name in langs)
 if '<div class="lang-menu">' in s:
  s=re.sub(r'(<div class="lang-menu">).*?(</div></div></header>)',lambda m:m.group(1)+menu+m.group(2),s,count=1,flags=re.S)
 elif "</header>" in s:
  s=s.replace("</header>",f'<div class="lang-switch"><button type="button">Language &#9662;</button><div class="lang-menu">{menu}</div></div></header>',1)
 f.write_text(s,encoding="utf-8");n+=1
css=r/"styles.css";s=css.read_text(encoding="utf-8")
s=s.replace("header{height:76px;display:flex;align-items:center;justify-content:space-between;max-width:1180px;margin:auto;padding:0 28px}", "header{height:76px;display:flex;align-items:center;justify-content:space-between;gap:24px;width:100%;max-width:1180px;margin:0 auto;padding:0 28px}")
s=s.replace(".lang-switch{position:relative;margin-left:auto}",".lang-switch{position:relative;margin-left:auto;padding-bottom:8px;margin-bottom:-8px}")
s=s.replace("top:calc(100% + 7px)","top:100%")
css.write_text(s,encoding="utf-8")
print("UPDATED",n)
