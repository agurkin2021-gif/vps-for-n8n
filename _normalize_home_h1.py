from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
h1s={
"es":"VPS para <em>n8n</em>",
"pt-br":"VPS para <em>n8n</em>",
"de":"VPS für <em>n8n</em>",
"hi":"<em>n8n</em> के लिए VPS",
"bn":"<em>n8n</em>-এর জন্য VPS",
"ja":"<em>n8n</em>向けVPS",
"pa":"<em>n8n</em> ਲਈ VPS"
}
for lang,h1 in h1s.items():
 f=r/lang/"index.html";s=f.read_text(encoding="utf-8")
 s=re.sub(r'(<section class="hero">.*?<h1>).*?(</h1>)',lambda m:m.group(1)+h1+m.group(2),s,count=1,flags=re.S)
 f.write_text(s,encoding="utf-8")
 print(lang,re.search(r'<section class="hero">.*?<h1>(.*?)</h1>',s,re.S).group(1))
