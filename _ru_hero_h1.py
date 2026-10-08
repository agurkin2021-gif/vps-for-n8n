from pathlib import Path
import re
f=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site\ru\index.html")
s=f.read_text(encoding="utf-8")
s=re.sub(r'(<section class="hero">.*?<h1>).*?(</h1>)',r'\1VPS для <em>n8n</em>\2',s,count=1,flags=re.S)
s=re.sub(r'(<section class="hero">.*?<p class="lead">).*?(</p>)',r'\1Выберите VPS под реальную нагрузку n8n — от лёгких автоматизаций до AI-workflows и production с queue mode.\2',s,count=1,flags=re.S)
f.write_text(s,encoding="utf-8")
print(re.search(r'<section class="hero">.*?<h1>(.*?)</h1>.*?<p class="lead">(.*?)</p>',s,re.S).groups())
