from pathlib import Path
import re,xml.etree.ElementTree as ET
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); q=r/"pa"
adds={
"n8n-hosting-india.html":"India SERP ਵਿੱਚ one-click n8n templates, managed updates, SSL ਅਤੇ automated backups ਵੱਖਰੇ commercial differentiators ਹਨ। ਇਹਨਾਂ ਨੂੰ ਸਿਰਫ “VPS included” ਨਾ ਸਮਝੋ—provider ਕਿਹੜੀ application-level support ਦਿੰਦਾ ਹੈ, ਇਹ plan-by-plan verify ਕਰੋ।",
"best-vps-for-n8n.html":"India locations ਜਿਵੇਂ Mumbai/Delhi/Bangalore ਦੀ proximity API/webhook latency ਘਟਾ ਸਕਦੀ ਹੈ। NVMe, bandwidth ਅਤੇ ₹/month ਦੇ ਨਾਲ actual region availability ਅਤੇ renewal price verify ਕਰੋ।",
"n8n-cloud-vs-self-hosted.html":"Self-hosted offers ਅਕਸਰ execution-count billing ਤੋਂ ਬਿਨਾਂ ਚੱਲਣ ਨੂੰ commercial benefit ਵਜੋਂ ਪੇਸ਼ ਕਰਦੇ ਹਨ; ਪਰ CPU/RAM/storage ਅਤੇ admin time practical limits ਬਣਦੇ ਹਨ। ਇਸ ਲਈ “unlimited executions” ਨੂੰ unlimited capacity ਨਾ ਸਮਝੋ।",
"index.html":"Self-hosted n8n ਵਿੱਚ infrastructure, OS, network, performance, updates ਅਤੇ disaster recovery owner/team ਦੀ responsibility ਹੁੰਦੀ ਹੈ। Managed hosting ਵਿੱਚ ਇਹਨਾਂ ਵਿੱਚੋਂ ਕੁਝ ਕੰਮ provider ਲੈ ਸਕਦਾ ਹੈ; support scope ਪਹਿਲਾਂ verify ਕਰੋ।"
}
for fn,text in adds.items():
 p=q/fn;s=p.read_text(encoding="utf-8")
 if text not in s:
  s=s.replace('<section class="section dark"><p>',f'<section class="section"><h2>SERP gap</h2><p class="intro">{text}</p></section><section class="section dark"><p>',1)
  p.write_text(s,encoding="utf-8")
fs=list(q.glob("*.html"));names={f.name for f in fs};e=[]
for f in fs:
 s=f.read_text(encoding="utf-8")
 for k,v in {"lang":'<html lang="pa">' in s,"h1":len(re.findall(r"<h1>",s))==1,"title":len(re.findall(r"<title>",s))==1,"canonical":len(re.findall(r'rel="canonical"',s))==1,"rel":'rel="sponsored nofollow"' in s}.items():
  if not v:e.append((f.name,k))
 for h in re.findall(r'href="([^"]+\.html)"',s):
  if "/" not in h and h not in names:e.append((f.name,"broken:"+h))
ET.parse(r/"sitemap.xml");sm=(r/"sitemap.xml").read_text(encoding="utf-8")
print("PA",len(fs),"UPDATED",len(adds),"ERRORS",e,"SITEMAP",sm.count("/pa/"))
