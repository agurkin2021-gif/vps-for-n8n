from pathlib import Path
import re,html
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
for lang in ["es","ru","pt-br","de","hi","bn","ja","pa"]:
 s=(r/lang/"index.html").read_text(encoding="utf-8")
 # visible text
 t=re.sub(r'<script.*?</script>|<style.*?</style>',' ',s,flags=re.S|re.I); t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
 lines=[re.sub(r'\s+',' ',x).strip() for x in t.splitlines() if re.sub(r'\s+',' ',x).strip()]
 suspects=[]
 for x in lines:
  words=re.findall(r"[A-Za-z]{3,}",x)
  # ignore short UI/tech-only lines
  allowed={"VPS","n8n","Docker","PostgreSQL","HTTPS","NVMe","CPU","RAM","Redis","API","FAQ","SSH","MFA","Cloud","Self","Hosted","Production","Queue","Mode","Workers","Linux","Ubuntu","Debian","Webhooks","Storage","Network","Monitoring","Backup","Architecture","Requirements"}
  natural=[w for w in words if w not in allowed]
  if len(natural)>=4:suspects.append(x)
 print("\n",lang,"SUSPECTS",len(suspects))
 for x in suspects[:30]:print(" -",x[:220])
