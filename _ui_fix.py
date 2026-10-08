from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
# CSS: click-driven dropdown, header spacing
css=r/"styles.css"; s=css.read_text(encoding="utf-8")
s=s.replace("header{height:76px;display:flex;align-items:center;justify-content:space-between;gap:24px;width:100%;max-width:1180px;margin:0 auto;padding:0 28px}","header{height:76px;display:flex;align-items:center;width:100%;max-width:1180px;margin:0 auto;padding:0 28px;gap:42px}")
s=s.replace("nav{display:flex;gap:28px}","nav{display:flex;gap:28px;margin-left:auto}")
s=s.replace(".lang-switch{position:relative;margin-left:auto;padding-bottom:8px;margin-bottom:-8px}",".lang-switch{position:relative;margin-left:18px}")
s=s.replace(".lang-switch:hover .lang-menu,.lang-switch:focus-within .lang-menu{display:grid}",".lang-switch.open .lang-menu{display:grid}")
css.write_text(s,encoding="utf-8")
# JS click behavior on every page with lang switch
js='''<script>(function(){document.addEventListener("click",function(e){var sw=e.target.closest(".lang-switch");document.querySelectorAll(".lang-switch.open").forEach(function(x){if(x!==sw)x.classList.remove("open")});if(e.target.closest(".lang-switch button")){e.preventDefault();sw.classList.toggle("open")}});document.addEventListener("keydown",function(e){if(e.key==="Escape")document.querySelectorAll(".lang-switch.open").forEach(function(x){x.classList.remove("open")})})})();</script>'''
for f in r.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html":continue
 x=f.read_text(encoding="utf-8",errors="ignore")
 if 'class="lang-switch"' in x and 'closest(".lang-switch")' not in x:
  x=x.replace("</body>",js+"</body>")
 f.write_text(x,encoding="utf-8")
# localized homepages: give same hero/terminal visual structure as English while preserving localized H1/lead
for lang in ["es","ru","pt-br","de","hi","bn","ja","pa"]:
 f=r/lang/"index.html"
 if not f.exists():continue
 x=f.read_text(encoding="utf-8")
 h1=re.search(r"<h1>(.*?)</h1>",x,re.S); lead=re.search(r'<p class="lead">(.*?)</p>',x,re.S)
 if not h1 or not lead:continue
 hero=f'''<section class="hero"><div><p class="eyebrow">SELF-HOSTED AUTOMATION INFRASTRUCTURE</p><h1>{h1.group(1)}</h1><p class="lead">{lead.group(1)}</p><div class="actions"><a class="primary" href="https://www.vdsina.com/?partner=ni8gzrvz75" rel="sponsored nofollow">VPS</a></div><div class="proof"><span>Docker ready</span><span>PostgreSQL</span><span>NVMe storage</span></div></div><div class="visual hero-ref-wrap"><div class="terminal"><div class="dots">● ● ●</div><p>$ docker compose up -d</p><p class="ok">✓ n8n running</p><p class="ok">✓ postgres healthy</p><p class="ok">✓ https enabled</p><div class="metric"><b>Production baseline</b><strong>2 vCPU · 4 GB RAM</strong><small>40+ GB SSD / NVMe</small></div></div></div></section>'''
 x=re.sub(r'<main><section class="section">.*?</section>',"<main>"+hero,x,count=1,flags=re.S)
 f.write_text(x,encoding="utf-8")
print("UI_FIXED")
