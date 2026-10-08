from pathlib import Path
root=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); base="https://agurkin2021-gif.github.io/vps-for-n8n/"
data={
"hi":("n8n-hosting-india.html","n8n Hosting India: Managed और Self-Hosted VPS","n8n hosting India में managed hosting, self-managed VPS, one-click deployment, ₹ pricing, backups, support और data residency की तुलना करें।","n8n Hosting India: Managed या Self-Managed?","Managed n8n hosting में provider setup, updates, SSL, monitoring और backups संभाल सकता है। Self-managed VPS में root control अधिक होता है, लेकिन Docker, PostgreSQL, security, updates और recovery आपकी जिम्मेदारी होती है।","India commercial criteria","₹/माह और renewal price के साथ included backups, support, execution limits, root access, server location/data residency, migration और scaling देखें। One-click deployment सुविधा है; production quality का विकल्प नहीं।","n8n Hosting India"),
"bn":("n8n-hosting-bangladesh.html","n8n Hosting Bangladesh: Managed ও Self-Hosted VPS","বাংলাদেশে n8n hosting বাছাইয়ে managed বনাম self-managed VPS, ৳ pricing, BDIX, local support/payment, backup এবং one-click deployment তুলনা করুন।","n8n Hosting Bangladesh: Managed নাকি Self-Managed?","Managed hosting setup, SSL, updates, monitoring ও backup সামলাতে পারে। Self-managed VPS-এ root control বেশি, কিন্তু Docker, PostgreSQL, security এবং recovery আপনার দায়িত্ব।","Bangladesh commercial criteria","৳/মাস, renewal, bKash/local payment, BDIX/latency, support, execution limits, backups, root access এবং scaling তুলনা করুন।","n8n Hosting Bangladesh")}
for lang,(fn,title,desc,h1,p1,h2,p2,anchor) in data.items():
 out=root/lang; url=base+lang+"/"+fn
 s=f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="{lang}" href="{url}"><link rel="alternate" hreflang="en" href="{base}"><link rel="alternate" hreflang="x-default" href="{base}"><link rel="icon" href="../favicon.svg"><link rel="stylesheet" href="../styles.css"></head><body><header><a class="brand" href="index.html">n8n<span>VPS</span></a></header><main><section class="section"><h1>{h1}</h1><p class="lead">{desc}</p><div class="actions"><a class="primary" href="https://www.vdsina.com/?partner=ni8gzrvz75" rel="sponsored nofollow">VPS</a></div></section><section class="section dark"><h2>{h2}</h2><p>{p1}</p></section><section class="section"><h2>{h2}</h2><p class="intro">{p2}</p></section><section class="section dark"><p><a href="index.html">VPS for n8n</a> · <a href="best-vps-for-n8n.html">Best VPS</a> · <a href="n8n-cloud-vs-self-hosted.html">Cloud vs self-hosted</a></p></section></main></body></html>'''
 (out/fn).write_text(s,encoding="utf-8")
 # add internal link to every language page
 for f in out.glob("*.html"):
  if f.name==fn: continue
  x=f.read_text(encoding="utf-8")
  marker='</p></section></main>'
  if fn not in x and marker in x: x=x.replace(marker,f' · <a href="{fn}">{anchor}</a></p></section></main>',1)
  f.write_text(x,encoding="utf-8")
# sitemap
urls=[]
for f in root.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html": continue
 rel=f.relative_to(root).as_posix()
 if rel.endswith("/index.html"): rel=rel[:-10]
 elif rel=="index.html": rel=""
 urls.append(base+rel)
(root/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f'  <url><loc>{u}</loc></url>' for u in sorted(set(urls)))+'\n</urlset>\n',encoding="utf-8")
print("HI",len(list((root/"hi").glob("*.html"))),"BN",len(list((root/"bn").glob("*.html"))),"URLS",len(set(urls)))
