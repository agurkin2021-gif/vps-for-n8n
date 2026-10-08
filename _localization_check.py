from pathlib import Path
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site")
required=["hero","workloads","save","requirements","architecture","production","operations","decision","environment","faq"]
badphr=["n8n VPS sizing by workload","Reduce avoidable resource usage before scaling","CPU, RAM and storage","Build for reliability","Beyond CPU and RAM","Self-hosting means operational ownership","Compare total cost and responsibility","What the server must support","n8n VPS FAQ"]
for lang in ["es","pt-br","de","hi","bn","ja","pa"]:
 s=(r/lang/"index.html").read_text(encoding="utf-8"); missing=[x for x in required if ('class="hero"' not in s if x=="hero" else f'id="{x}"' not in s)]; eng=[x for x in badphr if x in s]
 print(lang,"missing",missing,"english_headings",eng)
