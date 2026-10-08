from pathlib import Path
import re, html
root=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); out=root/"hi"; out.mkdir(exist_ok=True)
base="https://agurkin2021-gif.github.io/vps-for-n8n/"
pages=[
("index.html","n8n के लिए VPS: सही सर्वर कैसे चुनें","n8n के लिए VPS चुनते समय CPU, RAM, NVMe, Docker, PostgreSQL, HTTPS और workload को साथ में देखें।","n8n के लिए VPS: workload के हिसाब से सही सर्वर","हल्के automation के लिए 1–2 vCPU और 2 GB RAM चल सकती है। छोटे production के लिए 2 vCPU / 4 GB RAM एक व्यावहारिक शुरुआती बिंदु है; AI, बड़े payload और भारी Code nodes के लिए 4+ vCPU / 8 GB+ बेहतर है।","भारत में n8n VPS चुनते समय क्या देखें","केवल कम कीमत नहीं: NVMe, root access, Docker support, backups, upgrade path और users/API के पास server location देखें।"),
("best-vps-for-n8n.html","n8n के लिए Best VPS: production hosting guide","Best VPS for n8n workload, concurrency, storage और scaling पर निर्भर करता है।","n8n के लिए Best VPS कैसे चुनें","छोटे business automation के लिए 2 vCPU / 4 GB RAM से शुरू करें। अधिक concurrent executions, AI और file processing के लिए CPU/RAM बढ़ाएँ।","India workload के लिए selection criteria","₹/माह के साथ renewal price, NVMe, uptime, data-center latency, snapshots और vertical scaling की लागत देखें।"),
("n8n-vps-requirements.html","n8n VPS Requirements: RAM, CPU और storage","n8n के VPS requirements executions, payload, PostgreSQL, retention और binary data पर निर्भर करते हैं।","n8n VPS Requirements: RAM, CPU और NVMe","Testing: 1–2 vCPU / 2 GB. छोटा production: 2 vCPU / 4 GB. भारी workflows: 4+ vCPU / 8 GB+. 40–80 GB NVMe एक सामान्य शुरुआती range है, retention के अनुसार बढ़ाएँ।","कब resources बढ़ाने चाहिए","OOM/restarts, swapping, लगातार high CPU/RAM, बढ़ती execution latency और backlog स्पष्ट संकेत हैं।"),
("n8n-cloud-vs-self-hosted.html","n8n Cloud vs Self-Hosted: cost और control","n8n Cloud और self-hosted VPS को cost, maintenance, data control और scaling पर compare करें।","n8n Cloud vs Self-Hosted VPS","Cloud setup और maintenance आसान करता है; self-hosted अधिक control देता है लेकिन OS, Docker, updates, monitoring और recovery आपकी जिम्मेदारी होती है।","भारत में total cost कैसे compare करें","सिर्फ VPS rent नहीं: ₹/माह, admin time, backups, monitoring, traffic और scaling cost जोड़ें। अधिक executions पर self-hosted आर्थिक हो सकता है, लेकिन operational ownership जरूरी है।"),
("n8n-queue-mode.html","n8n Queue Mode: Redis, workers और scaling","n8n queue mode Redis और workers के साथ executions को scale करता है।","n8n Queue Mode और VPS Scaling","Queue mode में main instance triggers/webhooks लेता है, Redis queue संभालता है और workers executions चलाते हैं। Shared PostgreSQL आवश्यक है।","Queue mode कब उपयोग करें","जब optimized single instance पर backlog, webhook delay या concurrency bottleneck बना रहे। Workers की concurrency और DB connection pool साथ में size करें।"),
("n8n-vps-security.html","n8n VPS Security: production hardening","Self-hosted n8n के लिए HTTPS, firewall, SSH hardening, updates और secret protection जरूरी हैं।","n8n VPS Security: production checklist","Public production instance को HTTPS/reverse proxy के पीछे रखें, firewall से ports सीमित करें, SSH keys उपयोग करें और Docker/n8n/OS updates नियमित रखें।","Credentials और access","Secrets को source code में न रखें। Admin access सीमित रखें, logs monitor करें और backups को server से अलग सुरक्षित रखें।"),
("n8n-backup-restore.html","n8n Backup और Restore: production recovery","n8n backup में database, persistent data और encryption key को साथ सुरक्षित रखना जरूरी है।","n8n Backup और Restore","सिर्फ workflow export पर्याप्त नहीं। PostgreSQL/database, persistent volumes/config और encryption key का off-server backup रखें।","Restore test क्यों जरूरी है","Backup तभी उपयोगी है जब restore काम करे। नियमित test restore करें और encryption key खोने से credentials unreadable होने के जोखिम को रोकें।"),
("install-n8n-vps-docker.html","VPS पर n8n Install करें: Docker और PostgreSQL","VPS पर n8n को Docker, PostgreSQL, domain, HTTPS और reverse proxy के साथ production के लिए deploy करें।","VPS पर n8n कैसे Install करें","Ubuntu/Debian VPS तैयार करें, Docker/Compose install करें, PostgreSQL और persistent volumes configure करें, फिर domain DNS और HTTPS reverse proxy जोड़ें।","Production deployment order","Server → Docker → PostgreSQL → n8n environment → persistent storage → domain/DNS → HTTPS/reverse proxy → webhook test → backup. Default ports को बिना जरूरत public न रखें।")
]
links=" · ".join([f'<a href="{p[0]}">{p[2].split(":")[0]}</a>' for p in pages])
for fn,title,desc,h1,p1,h2,p2 in pages:
    url=base+"hi/"+("" if fn=="index.html" else fn)
    body=f'''<!doctype html><html lang="hi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="hi" href="{url}"><link rel="alternate" hreflang="en" href="{base}"><link rel="alternate" hreflang="x-default" href="{base}"><link rel="icon" href="../favicon.svg"><link rel="stylesheet" href="../styles.css"></head><body><header><a class="brand" href="index.html">n8n<span>VPS</span></a><div class="lang-switch"><button type="button">हिन्दी &#9662;</button><div class="lang-menu"><a href="../">English</a><a href="../es/">Español</a><a href="../ru/">Русский</a><a href="../pt-br/">Português</a><a href="../de/">Deutsch</a><a href="./">हिन्दी</a></div></div></header><main><section class="section"><h1>{h1}</h1><p class="lead">{desc}</p><div class="actions"><a class="primary" href="https://www.vdsina.com/?partner=ni8gzrvz75" rel="sponsored nofollow">VPS विकल्प देखें</a></div></section><section class="section dark"><h2>{h2}</h2><p>{p1}</p></section><section class="section"><h2>Production में मुख्य बातें</h2><p class="intro">{p2}</p></section><section class="section dark"><p>{links}</p></section></main></body></html>'''
    (out/fn).write_text(body,encoding="utf-8")
# Add hi to language menus and hreflang on existing commercial pages
for f in [x for x in root.rglob("*.html") if "hi" not in x.parts]:
    s=f.read_text(encoding="utf-8",errors="ignore")
    if "n8n<span>VPS</span>" not in s: continue
    rel="../" if f.parent!=root else ""
    if 'hreflang="hi"' not in s:
        target=base+"hi/"
        s=s.replace('<link rel="alternate" hreflang="x-default"',f'<link rel="alternate" hreflang="hi" href="{target}"><link rel="alternate" hreflang="x-default"',1)
    if ">हिन्दी<" not in s and "</div></div></header>" in s:
        s=s.replace("</div></div></header>",f'<a href="{rel}hi/">हिन्दी</a></div></div></header>',1)
    f.write_text(s,encoding="utf-8")
# rebuild valid sitemap from known commercial + utility files
urls=[]
for f in root.rglob("*.html"):
    if ".git" in f.parts or f.name=="404.html": continue
    rel=f.relative_to(root).as_posix()
    if rel.endswith("/index.html"): rel=rel[:-10]
    elif rel=="index.html": rel=""
    urls.append(base+rel)
xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f'  <url><loc>{u}</loc></url>' for u in sorted(set(urls)))+'\n</urlset>\n'
(root/"sitemap.xml").write_text(xml,encoding="utf-8")
print("HI_CREATED",len(list(out.glob("*.html"))),"SITEMAP_URLS",len(set(urls)))
