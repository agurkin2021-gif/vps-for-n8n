from pathlib import Path
f=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site\ru\index.html")
s=f.read_text(encoding="utf-8")
R={
"SELF-HOSTED AUTOMATION INFRASTRUCTURE":"ИНФРАСТРУКТУРА ДЛЯ САМОСТОЯТЕЛЬНОЙ АВТОМАТИЗАЦИИ",
"Self-hosted означает ответственность владельца":"Самостоятельное размещение означает ответственность владельца",
"Self-hosted VPS":"VPS с самостоятельным размещением",
"Cloud vs self-hosted":"Облачный сервис или самостоятельное размещение",
"self-hosted":"самостоятельное размещение"
}
for a,b in R.items():s=s.replace(a,b)
f.write_text(s,encoding="utf-8")
print("SELFHOST_LEFT",s.lower().count("self-hosted"))
