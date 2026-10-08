from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
files=[r/"about.html",r/"contact.html",r/"privacy.html",r/"bn"/"n8n-hosting-bangladesh.html",r/"hi"/"n8n-hosting-india.html"]
for f in files:
 s=f.read_text(encoding="utf-8"); pre="../" if f.parent!=r else ""
 menu=''.join([f'<a href="{pre+p}">{n}</a>' for p,n in [("","English"),("es/","Español"),("ru/","Русский"),("pt-br/","Português"),("de/","Deutsch"),("hi/","हिन्दी"),("bn/","বাংলা"),("ja/","日本語"),("pa/","ਪੰਜਾਬੀ")]])
 if '<div class="lang-switch">' not in s:
  s=s.replace("</header>",f'<div class="lang-switch"><button type="button">Language &#9662;</button><div class="lang-menu">{menu}</div></div></header>',1)
 f.write_text(s,encoding="utf-8")
print("FIXED",len(files))
