from pathlib import Path
f=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site\ru\index.html")
s=f.read_text(encoding="utf-8")
repl={"✓ n8n running":"✓ n8n запущен","✓ postgres healthy":"✓ PostgreSQL работает","✓ https enabled":"✓ HTTPS включён","Production baseline":"Базовая конфигурация production","Docker ready":"Docker готов","NVMe storage":"NVMe-хранилище"}
for a,b in repl.items():s=s.replace(a,b)
f.write_text(s,encoding="utf-8")
print("OK",all(b in s for b in repl.values()),"COMMAND", "$ docker compose up -d" in s,"HERO", 'class="hero"' in s)
