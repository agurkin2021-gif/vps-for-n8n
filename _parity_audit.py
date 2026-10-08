from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
langs=["en","es","ru","pt-br","de","hi","bn","ja","pa"]
required=["hero","workloads","save","requirements","architecture","production","operations","decision","environment","faq"]
for lang in langs:
 f=r/"index.html" if lang=="en" else r/lang/"index.html"
 s=f.read_text(encoding="utf-8",errors="ignore")
 missing=[]
 for x in required:
  if x=="hero":
   if 'class="hero"' not in s:missing.append(x)
  elif f'id="{x}"' not in s:missing.append(x)
 print(lang,"bytes",len(s.encode("utf-8")),"missing",",".join(missing) if missing else "NONE")
