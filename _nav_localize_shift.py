from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
labels={
"en":["Sizing","Requirements","Architecture","FAQ"],
"ru":["Подбор VPS","Требования","Архитектура","Вопросы"],
"es":["Dimensionamiento","Requisitos","Arquitectura","Preguntas"],
"pt-br":["Dimensionamento","Requisitos","Arquitetura","Perguntas"],
"de":["Dimensionierung","Anforderungen","Architektur","FAQ"],
"hi":["साइज़िंग","आवश्यकताएँ","आर्किटेक्चर","सवाल"],
"bn":["সাইজিং","প্রয়োজনীয়তা","আর্কিটেকচার","প্রশ্ন"],
"ja":["サイジング","要件","構成","FAQ"],
"pa":["ਸਾਈਜ਼ਿੰਗ","ਲੋੜਾਂ","ਆਰਕੀਟੈਕਚਰ","ਸਵਾਲ"]}
for lang,labs in labels.items():
 f=r/"index.html" if lang=="en" else r/lang/"index.html"
 if not f.exists():continue
 s=f.read_text(encoding="utf-8")
 nav=f'<nav class="main-nav"><a href="#workloads">{labs[0]}</a><a href="#requirements">{labs[1]}</a><a href="#architecture">{labs[2]}</a><a href="#faq">{labs[3]}</a></nav>'
 s=re.sub(r'<nav class="main-nav">.*?</nav>',nav,s,count=1,flags=re.S)
 f.write_text(s,encoding="utf-8")
css=r/"styles.css";s=css.read_text(encoding="utf-8")
s=re.sub(r'header\{[^}]*\}','header{height:76px;display:grid;grid-template-columns:240px minmax(0,1fr) 180px;align-items:center;width:100%;max-width:1180px;margin:0 auto;padding:0 28px;column-gap:44px}',s,count=1)
s=s.replace("nav{display:flex;justify-content:center;gap:32px;margin:0}","nav{display:flex;justify-content:flex-end;gap:32px;margin:0}")
s=s.replace("@media(max-width:850px){header{grid-template-columns:1fr auto;column-gap:18px}","@media(max-width:850px){header{grid-template-columns:1fr auto;column-gap:18px}")
css.write_text(s,encoding="utf-8")
print("DONE")
