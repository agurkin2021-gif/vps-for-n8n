from pathlib import Path
f=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site\ru\index.html")
s=f.read_text(encoding="utf-8")
R={
"Выберите VPS под реальную нагрузку n8n — от лёгких автоматизаций до AI-workflows и production с queue mode.":"Выберите VPS под реальную нагрузку n8n — от лёгких автоматизаций до ИИ-сценариев и промышленной эксплуатации с режимом очереди.",
"AI, большие JSON, файлы, Code nodes и несколько одновременных executions.":"ИИ, большие JSON-данные, файлы, узлы Code и несколько одновременных выполнений.",
"Для queue mode добавляются Redis и workers. Все instances должны использовать общий N8N_ENCRYPTION_KEY.":"Для режима очереди добавляются Redis и рабочие процессы. Все экземпляры должны использовать общий N8N_ENCRYPTION_KEY.",
"Reverse proxy, домен и корректный WEBHOOK_URL.":"Обратный прокси, домен и корректный WEBHOOK_URL.",
"Контролируйте execution history и binary data, чтобы диск не рос бесконтрольно.":"Контролируйте историю выполнений и двоичные данные, чтобы диск не рос бесконтрольно.",
"OOM/restarts, swap, высокая CPU/RAM и рост latency — сигналы нехватки ресурсов.":"Ошибки нехватки памяти и перезапуски, подкачка, высокая загрузка CPU/RAM и рост задержки — сигналы нехватки ресурсов.",
"Больше контроля над инфраструктурой, данными и scaling. В TCO входят VPS, backups, monitoring и время администратора.":"Больше контроля над инфраструктурой, данными и масштабированием. В полную стоимость входят VPS, резервные копии, мониторинг и время администратора.",
"DB, volumes, encryption key и реальный test restore.":"База данных, тома, ключ шифрования и реальная проверка восстановления.",
"Да. Для production обычно используют Docker/Compose, PostgreSQL, reverse proxy, HTTPS и persistent volumes.":"Да. Для промышленной эксплуатации обычно используют Docker Compose, PostgreSQL, обратный прокси, HTTPS и постоянные тома."
}
for a,b in R.items():s=s.replace(a,b)
f.write_text(s,encoding="utf-8")
print("RU_CLEANED",sum(b in s for b in R.values()),"/",len(R))
