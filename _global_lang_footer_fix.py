from pathlib import Path
import re
root=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); base="https://agurkin2021-gif.github.io/vps-for-n8n/"
langs=[("en","English",""),("es","Español","es/"),("ru","Русский","ru/"),("pt-BR","Português","pt-br/"),("de","Deutsch","de/"),("hi","हिन्दी","hi/"),("bn","বাংলা","bn/"),("ja","日本語","ja/"),("pa","ਪੰਜਾਬੀ","pa/")]
dirs={"es","ru","pt-br","de","hi","bn","ja","pa"}
def relprefix(f): return "../" if f.parent.name in dirs else ""
def langmenu(f):
 pre=relprefix(f)
 items=[]
 for code,name,path in langs:
  href=(pre+path) if path else pre
  if not href: href="./"
  items.append(f'<a href="{href}">{name}</a>')
 return "".join(items)
footer='''<footer><b>n8nVPS</b><span>Independent infrastructure guide for self-hosted n8n.</span><p>Metro Manhattan Office Space, Inc.<br>122 East 42nd Street, Suite 446<br>New York, NY 10168<br>United States</p><p><a href="{P}about.html">About</a> · <a href="{P}contact.html">Contact</a> · <a href="{P}privacy.html">Privacy</a></p></footer>'''
count=0
for f in root.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html": continue
 s=f.read_text(encoding="utf-8",errors="ignore")
 if "n8n<span>VPS</span>" not in s: continue
 # replace menu content
 s=re.sub(r'(<div class="lang-menu">).*?(</div></div></header>)',lambda m:m.group(1)+langmenu(f)+m.group(2),s,count=1,flags=re.S)
 # add missing hreflangs using homepage language roots as fallback
 head_end=s.find("</head>")
 existing=s[:head_end]
 ins=""
 for code,name,path in langs:
  if f'hreflang="{code}"' not in existing:
   ins+=f'<link rel="alternate" hreflang="{code}" href="{base+path}">'
 if ins: s=s[:head_end]+ins+s[head_end:]
 # footer if missing
 if "<footer" not in s:
  pre=relprefix(f); ft=footer.replace("{P}",pre)
  s=s.replace("</body>",ft+"</body>")
 f.write_text(s,encoding="utf-8"); count+=1
print("UPDATED",count)
