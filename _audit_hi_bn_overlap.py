from pathlib import Path
import re
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
for lang in ["hi","bn"]:
 print("\nLANG",lang)
 for f in sorted((r/lang).glob("*.html")):
  s=f.read_text(encoding="utf-8")
  title=re.search(r"<title>(.*?)</title>",s,re.S).group(1)
  h1=re.search(r"<h1>(.*?)</h1>",s,re.S).group(1)
  print(f.name,"|",title,"|",h1)
