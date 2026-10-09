#!/usr/bin/env python3
"""Native Punjabi SEO/heading corrections after page translation; HTML/CSS/JS invariant."""
from pathlib import Path
import html
import re
import sys
from _pa_translate_full import PAGES,ROOT

SEO=[
("n8n ਲਈ VPS $0.07/Day ਤੋਂ — ਪਲਾਨ ਅਤੇ ਸਰਵਰ ਸਾਈਜ਼ ਗਾਈਡ",
 "<em>n8n</em> ਲਈ VPS",
 "n8n ਲਈ $0.07/day ਤੋਂ VPS ਕਨਫਿਗਰੇਸ਼ਨਾਂ ਦੀ ਤੁਲਨਾ ਕਰੋ। ਹਲਕੇ ਆਟੋਮੇਸ਼ਨ, ਪ੍ਰੋਡਕਸ਼ਨ ਵਰਕਫਲੋ, ਡਾਟਾ ਪ੍ਰੋਸੈਸਿੰਗ ਅਤੇ AI ਲਈ CPU, RAM, ਸਟੋਰੇਜ ਅਤੇ ਟ੍ਰੈਫ਼ਿਕ ਮੁਤਾਬਕ ਚੋਣ ਕਰੋ।"),
("2026 ਵਿੱਚ n8n ਲਈ ਵਧੀਆ VPS — 6 ਪ੍ਰਦਾਤਾਵਾਂ ਦੀ ਤੁਲਨਾ",
 "n8n ਲਈ ਵਧੀਆ VPS: 6 ਪ੍ਰਦਾਤਾਵਾਂ ਦੀ ਤੁਲਨਾ",
 "n8n ਲਈ 6 VPS ਵਿਕਲਪਾਂ ਦੀ ਸੈਟਅੱਪ, ਕੰਟਰੋਲ, ਬੈਕਅੱਪ, ਸਹਾਇਤਾ, ਮਾਈਗ੍ਰੇਸ਼ਨ, ਖੇਤਰ ਅਤੇ ਸਕੇਲਿੰਗ ਮੁਤਾਬਕ ਤੁਲਨਾ ਕਰੋ। ਆਪਣੇ ਵਰਕਲੋਡ ਲਈ ਢੁਕਵਾਂ ਪ੍ਰਦਾਤਾ ਮਾਡਲ ਚੁਣੋ।"),
("ਸਾਡੇ ਬਾਰੇ | n8nVPS",
 "n8nVPS ਬਾਰੇ",
 "n8nVPS ਬਾਰੇ ਜਾਣੋ — ਸੈਲਫ-ਹੋਸਟਡ n8n ਲਈ VPS ਦੀ ਸਾਈਜ਼ਿੰਗ ਅਤੇ ਪ੍ਰੋਡਕਸ਼ਨ ਇਨਫ੍ਰਾਸਟਰਕਚਰ ਦੀ ਸੁਤੰਤਰ ਗਾਈਡ।"),
("n8n ਬੈਕਅੱਪ ਅਤੇ ਰੀਸਟੋਰ",
 "n8n ਦਾ ਬੈਕਅੱਪ ਅਤੇ ਰੀਸਟੋਰ",
 "VPS ਉੱਤੇ ਸੈਲਫ-ਹੋਸਟਡ n8n ਦਾ ਬੈਕਅੱਪ ਅਤੇ ਰੀਸਟੋਰ: PostgreSQL ਜਾਂ SQLite, ਵਰਕਫਲੋ, ਕਰੀਡੈਂਸ਼ਲ, ਇਨਕ੍ਰਿਪਸ਼ਨ ਕੁੰਜੀ, ਬਾਈਨਰੀ ਡਾਟਾ, ਸਰਵਰ ਤੋਂ ਬਾਹਰ ਕਾਪੀਆਂ ਅਤੇ ਰੀਸਟੋਰ ਟੈਸਟ।"),
("ਸੰਪਰਕ | n8nVPS",
 "ਸੰਪਰਕ ਕਰੋ",
 "ਸੁਧਾਰਾਂ, ਪ੍ਰੋਜੈਕਟ ਸੰਬੰਧੀ ਸਵਾਲਾਂ ਅਤੇ ਕਾਰੋਬਾਰੀ ਪੁੱਛਗਿੱਛ ਲਈ n8nVPS ਨਾਲ ਸੰਪਰਕ ਕਰੋ।"),
("VPS ਉੱਤੇ n8n ਇੰਸਟਾਲ ਕਿਵੇਂ ਕਰੀਏ",
 "VPS ਉੱਤੇ n8n ਇੰਸਟਾਲ ਕਰੋ",
 "Docker Compose, PostgreSQL, ਸਥਾਈ ਸਟੋਰੇਜ, HTTPS, ਰਿਵਰਸ ਪ੍ਰੌਕਸੀ ਅਤੇ ਸਹੀ ਵੈੱਬਹੁੱਕ ਕਨਫਿਗਰੇਸ਼ਨ ਨਾਲ VPS ਉੱਤੇ n8n ਇੰਸਟਾਲ ਕਰੋ।"),
("n8n Cloud ਬਨਾਮ ਸੈਲਫ-ਹੋਸਟਡ — ਲਾਗਤ ਅਤੇ ਕੰਟਰੋਲ",
 "n8n Cloud ਬਨਾਮ ਸੈਲਫ-ਹੋਸਟਡ",
 "ਲਾਗਤ, ਇਨਫ੍ਰਾਸਟਰਕਚਰ ਕੰਟਰੋਲ, ਦੇਖਭਾਲ, ਡਾਟਾ ਦੀ ਸਥਿਤੀ, ਸਕੇਲਿੰਗ ਅਤੇ ਤਕਨੀਕੀ ਜ਼ਿੰਮੇਵਾਰੀ ਮੁਤਾਬਕ n8n Cloud ਅਤੇ VPS ਉੱਤੇ ਸੈਲਫ-ਹੋਸਟਡ n8n ਦੀ ਤੁਲਨਾ ਕਰੋ।"),
("n8n ਲਈ VPS ਦੀਆਂ ਲੋੜਾਂ",
 "n8n ਲਈ VPS ਦੀਆਂ ਲੋੜਾਂ",
 "n8n ਲਈ VPS ਦੀ RAM, CPU, SSD ਸਟੋਰੇਜ, PostgreSQL, Docker, ਸਮਕਾਲੀ ਐਗਜ਼ਿਕਿਊਸ਼ਨ ਅਤੇ ਪ੍ਰੋਡਕਸ਼ਨ ਵਰਕਲੋਡ ਸਾਈਜ਼ਿੰਗ ਦੀਆਂ ਲੋੜਾਂ।"),
("ਪਰਦੇਦਾਰੀ ਨੀਤੀ | n8nVPS",
 "ਪਰਦੇਦਾਰੀ ਨੀਤੀ",
 "n8nVPS ਦੀ ਪਰਦੇਦਾਰੀ ਨੀਤੀ — ਐਨਾਲਿਟਿਕਸ ਅਤੇ ਐਫੀਲੀਏਟ ਲਿੰਕਾਂ ਬਾਰੇ ਖੁਲਾਸਿਆਂ ਸਮੇਤ।"),
("VPS ਉੱਤੇ n8n ਦੀ ਸੁਰੱਖਿਆ ਕਿਵੇਂ ਕਰੀਏ",
 "VPS ਉੱਤੇ n8n ਨੂੰ ਸੁਰੱਖਿਅਤ ਕਰੋ",
 "HTTPS, ਰਿਵਰਸ ਪ੍ਰੌਕਸੀ, ਫਾਇਰਵਾਲ, SSH ਹਾਰਡਨਿੰਗ, ਨਿੱਜੀ PostgreSQL, ਇਨਕ੍ਰਿਪਸ਼ਨ ਕੁੰਜੀ ਦੀ ਸੁਰੱਖਿਆ, SSRF ਕੰਟਰੋਲ ਅਤੇ ਸੁਰੱਖਿਆ ਆਡਿਟ ਨਾਲ ਸੈਲਫ-ਹੋਸਟਡ n8n VPS ਨੂੰ ਸੁਰੱਖਿਅਤ ਕਰੋ।"),
("n8n ਕਿਊ ਮੋਡ — Redis ਅਤੇ ਵਰਕਰਾਂ ਨਾਲ ਸਕੇਲਿੰਗ",
 "n8n ਕਿਊ ਮੋਡ",
 "ਜਾਣੋ n8n ਨੂੰ ਕਦੋਂ ਕਿਊ ਮੋਡ ਦੀ ਲੋੜ ਹੁੰਦੀ ਹੈ, Redis ਅਤੇ ਵਰਕਰ ਐਗਜ਼ਿਕਿਊਸ਼ਨ ਕਿਵੇਂ ਸਕੇਲ ਕਰਦੇ ਹਨ, ਵਰਕਰ ਕੰਕਰੰਸੀ, PostgreSQL ਦੀਆਂ ਲੋੜਾਂ, ਨਿਗਰਾਨੀ ਅਤੇ VPS ਸਾਈਜ਼ਿੰਗ ਬਾਰੇ।")
]

EYEBROWS={
"CHOOSE THE RESOURCES YOUR WORKFLOWS NEED":"ਆਪਣੇ ਵਰਕਫਲੋ ਲਈ ਲੋੜੀਂਦੇ ਸਰੋਤ ਚੁਣੋ",
"FROM YOUR AUTOMATION TO YOUR SERVER":"ਆਟੋਮੇਸ਼ਨ ਦੀ ਲੋੜ ਤੋਂ ਸਰਵਰ ਦੀ ਚੋਣ ਤੱਕ",
"KNOW WHAT TO SELECT":"ਕੀ ਚੁਣਨਾ ਹੈ, ਸਮਝੋ",
"CONTROL OR MANAGED CONVENIENCE":"ਆਪਣਾ ਕੰਟਰੋਲ ਜਾਂ ਮੈਨੇਜਡ ਸਹੂਲਤ",
"BUY THE RESOURCE YOUR WORKFLOWS USE":"ਵਰਕਫਲੋ ਲਈ ਲੋੜੀਂਦੇ ਸਰੋਤ ਹੀ ਖਰੀਦੋ",
"A CLEAR GROWTH PATH":"ਅੱਗੇ ਵਧਣ ਦਾ ਸਪਸ਼ਟ ਰਾਹ",
"COMPLETE YOUR DEPLOYMENT":"ਡਿਪਲੌਇਮੈਂਟ ਪੂਰੀ ਕਰੋ",
"PUT YOUR BUDGET WHERE IT HELPS":"ਬਜਟ ਠੀਕ ਥਾਂ ਖਰਚੋ",
"A BUDGET YOU CAN FOLLOW":"ਸਮਝਣ ਯੋਗ ਬਜਟ",
"BUILD YOUR REAL MONTHLY BUDGET":"ਅਸਲ ਮਹੀਨਾਵਾਰ ਬਜਟ ਦਾ ਅੰਦਾਜ਼ਾ",
"NEXT STEPS":"ਅਗਲੇ ਕਦਮ",
"BUYING QUESTIONS ANSWERED":"ਖਰੀਦ ਤੋਂ ਪਹਿਲਾਂ ਦੇ ਸਵਾਲ",
"CONFIGURATION REFERENCES":"ਕਨਫਿਗਰੇਸ਼ਨ ਦੇ ਹਵਾਲੇ",
"PROVIDER COMPARISON · REVIEWED 8 OCTOBER 2026":"ਪ੍ਰਦਾਤਾਵਾਂ ਦੀ ਤੁਲਨਾ · 8 ਅਕਤੂਬਰ 2026 ਨੂੰ ਜਾਂਚਿਆ",
"SIX OPTIONS · ONE SET OF BUYING CRITERIA":"6 ਵਿਕਲਪ · ਇੱਕੋ ਚੋਣ ਮਾਪਦੰਡ",
"QUICK SHORTLIST":"ਛੋਟੀ ਸੂਚੀ",
"WHAT TO COMPARE":"ਕੀ ਤੁਲਨਾ ਕਰਨੀ ਹੈ",
"PRICE LENS":"ਕੀਮਤ ਦਾ ਅੰਕਲਨ",
"DECIDE BY SCENARIO":"ਵਰਤੋਂ ਮੁਤਾਬਕ ਫ਼ੈਸਲਾ",
"DO NOT MIX THE TWO DECISIONS":"ਦੋ ਵੱਖਰੇ ਫ਼ੈਸਲੇ ਨਾ ਮਿਲਾਓ",
"EDITORIAL METHOD":"ਮੁਲਾਂਕਣ ਦਾ ਤਰੀਕਾ",
"BACKUP & RECOVERY":"ਬੈਕਅੱਪ ਅਤੇ ਰਿਕਵਰੀ",
"QUICK CHECKLIST":"ਤੁਰੰਤ ਜਾਂਚ ਸੂਚੀ",
"TWO BACKUP LEVELS":"ਬੈਕਅੱਪ ਦੇ ਦੋ ਪੱਧਰ",
"DATABASE":"ਡਾਟਾਬੇਸ",
"CRITICAL SECRET":"ਬਹੁਤ ਜ਼ਰੂਰੀ ਗੁਪਤ ਕੁੰਜੀ",
"FILES & BINARY DATA":"ਫਾਈਲਾਂ ਅਤੇ ਬਾਈਨਰੀ ਡਾਟਾ",
"OFF-SERVER STRATEGY":"ਸਰਵਰ ਤੋਂ ਬਾਹਰ ਬੈਕਅੱਪ ਦੀ ਰਣਨੀਤੀ",
"RESTORE ORDER":"ਰੀਸਟੋਰ ਦਾ ਕ੍ਰਮ",
"RESTORE TEST":"ਰੀਸਟੋਰ ਟੈਸਟ",
"CLI BACKUP LIMITS":"CLI ਬੈਕਅੱਪ ਦੀਆਂ ਹੱਦਾਂ",
"RECOVERY OBJECTIVES":"ਰਿਕਵਰੀ ਦੇ ਟੀਚੇ",
"RECOVERY KEY":"ਰਿਕਵਰੀ ਕੁੰਜੀ",
"DOCKER INSTALLATION":"Docker ਨਾਲ ਇੰਸਟਾਲੇਸ਼ਨ",
"PREREQUISITES":"ਪਹਿਲਾਂ ਦੀਆਂ ਲੋੜਾਂ",
"DEPLOYMENT STACK":"ਡਿਪਲੌਇਮੈਂਟ ਦਾ ਢਾਂਚਾ",
"COPY-AND-ADAPT INSTALLATION":"ਕਾਪੀ ਕਰਕੇ ਆਪਣੀ ਲੋੜ ਅਨੁਸਾਰ ਬਦਲੋ",
"CONFIGURATION":"ਕਨਫਿਗਰੇਸ਼ਨ",
"PERSISTENCE":"ਡਾਟਾ ਸਥਾਈ ਰੱਖਣਾ",
"POSTGRESQL":"PostgreSQL",
"HTTPS & PROXY":"HTTPS ਅਤੇ ਰਿਵਰਸ ਪ੍ਰੌਕਸੀ",
"FIRST START":"ਪਹਿਲੀ ਸ਼ੁਰੂਆਤ",
"UPDATES":"ਅੱਪਡੇਟ",
"COMMON FAILURES":"ਆਮ ਸਮੱਸਿਆਵਾਂ",
"POST-DEPLOY VERIFICATION":"ਇੰਸਟਾਲੇਸ਼ਨ ਤੋਂ ਬਾਅਦ ਜਾਂਚ",
"HOSTING DECISION":"ਹੋਸਟਿੰਗ ਦੀ ਚੋਣ",
"QUICK VERDICT":"ਸਿੱਧਾ ਨਤੀਜਾ",
"SIDE-BY-SIDE":"ਸਿੱਧੀ ਤੁਲਨਾ",
"ONE DECISION · TWO OPERATING MODELS":"ਇੱਕ ਫ਼ੈਸਲਾ · ਦੋ ਸੰਚਾਲਨ ਮਾਡਲ",
"WORKFLOW FREQUENCY CHECK":"ਵਰਕਫਲੋ ਚੱਲਣ ਦੀ ਆਵਿਰਤੀ",
"A THIRD OPERATING MODEL":"ਤੀਜਾ ਸੰਚਾਲਨ ਮਾਡਲ",
"REAL COST MODEL":"ਅਸਲ ਲਾਗਤ ਦਾ ਮਾਡਲ",
"DECISION PATH":"ਫ਼ੈਸਲੇ ਦੀ ਪ੍ਰਕਿਰਿਆ",
"TOTAL COST OF OWNERSHIP":"ਕੁੱਲ ਮਲਕੀਅਤ ਲਾਗਤ",
"CONTROL & DATA":"ਕੰਟਰੋਲ ਅਤੇ ਡਾਟਾ",
"OPERATIONS":"ਸੰਚਾਲਨ",
"SCALING":"ਸਕੇਲਿੰਗ",
"DECISION FRAMEWORK":"ਫ਼ੈਸਲੇ ਦੇ ਮਾਪਦੰਡ",
"EDITION & LICENSE BOUNDARY":"ਐਡੀਸ਼ਨ ਅਤੇ ਲਾਇਸੈਂਸ ਦੀਆਂ ਹੱਦਾਂ",
"LONG-TERM OPERATIONS":"ਲੰਬੇ ਸਮੇਂ ਦਾ ਸੰਚਾਲਨ",
"MIGRATION DECISION":"ਮਾਈਗ੍ਰੇਸ਼ਨ ਦਾ ਫ਼ੈਸਲਾ",
"SERVER REQUIREMENTS":"ਸਰਵਰ ਦੀਆਂ ਲੋੜਾਂ",
"QUICK REQUIREMENTS":"ਜ਼ਰੂਰੀ ਲੋੜਾਂ",
"RESOURCE BUNDLES · VERIFIED PRICING":"ਸਰੋਤਾਂ ਦੇ ਪੈਕ · ਜਾਂਚੀਆਂ ਕੀਮਤਾਂ",
"MINIMUM VS PRACTICAL CAPACITY":"ਘੱਟੋ-ਘੱਟ ਅਤੇ ਵਰਤੋਂਯੋਗ ਸਮਰੱਥਾ",
"RAM & CPU":"RAM ਅਤੇ CPU",
"MEASURE BEFORE YOU UPGRADE":"ਅੱਪਗ੍ਰੇਡ ਤੋਂ ਪਹਿਲਾਂ ਮਾਪੋ",
"DATABASE & STORAGE":"ਡਾਟਾਬੇਸ ਅਤੇ ਸਟੋਰੇਜ",
"DISK CAPACITY":"ਡਿਸਕ ਦੀ ਸਮਰੱਥਾ",
"SYSTEM REQUIREMENTS":"ਸਿਸਟਮ ਦੀਆਂ ਲੋੜਾਂ",
"CONCURRENCY":"ਇੱਕੋ ਸਮੇਂ ਚੱਲਣ ਵਾਲੇ ਕੰਮ",
"SIZING CHECKLIST":"ਸਰੋਤ ਚੋਣ ਦੀ ਜਾਂਚ ਸੂਚੀ",
"ENTRY TIER & STORAGE I/O":"ਮੁੱਢਲਾ ਪਲਾਨ ਅਤੇ ਸਟੋਰੇਜ I/O",
"PRODUCTION SECURITY":"ਪ੍ਰੋਡਕਸ਼ਨ ਸੁਰੱਖਿਆ",
"NETWORK EDGE":"ਨੈੱਟਵਰਕ ਦੀ ਸੀਮਾ",
"VPS HARDENING":"VPS ਦੀ ਸੁਰੱਖਿਆ ਮਜ਼ਬੂਤ ਕਰਨੀ",
"DATABASE & REDIS":"ਡਾਟਾਬੇਸ ਅਤੇ Redis",
"N8N SECRETS":"n8n ਦੀਆਂ ਗੁਪਤ ਕੁੰਜੀਆਂ",
"WORKFLOW RISK":"ਵਰਕਫਲੋ ਦੇ ਖ਼ਤਰੇ",
"AUDIT & UPDATES":"ਆਡਿਟ ਅਤੇ ਅੱਪਡੇਟ",
"DEPLOYMENT ORDER":"ਡਿਪਲੌਇਮੈਂਟ ਦਾ ਕ੍ਰਮ",
"ACCOUNT & PLATFORM CONTROLS":"ਖਾਤੇ ਅਤੇ ਪਲੇਟਫਾਰਮ ਦੀ ਸੁਰੱਖਿਆ",
"QUICK DECISION":"ਸਿੱਧਾ ਫ਼ੈਸਲਾ",
"ARCHITECTURE":"ਸਿਸਟਮ ਦਾ ਢਾਂਚਾ",
"CORE REQUIREMENTS":"ਮੁੱਖ ਲੋੜਾਂ",
"WORKER CONCURRENCY":"ਵਰਕਰਾਂ ਦੀ ਸਮਕਾਲੀ ਸਮਰੱਥਾ",
"WEBHOOKS":"ਵੈੱਬਹੁੱਕ",
"BINARY DATA":"ਬਾਈਨਰੀ ਡਾਟਾ",
"MONITORING":"ਨਿਗਰਾਨੀ",
"SCALING PATH":"ਸਕੇਲਿੰਗ ਦਾ ਰਾਹ",
"HIGH AVAILABILITY BOUNDARY":"ਉੱਚ ਉਪਲਬਧਤਾ ਦੀਆਂ ਹੱਦਾਂ",
"FAQ":"ਅਕਸਰ ਪੁੱਛੇ ਜਾਣ ਵਾਲੇ ਸਵਾਲ",
"ABOUT":"ਸਾਡੇ ਬਾਰੇ",
"CONTACT":"ਸੰਪਰਕ",
"PRIVACY":"ਪਰਦੇਦਾਰੀ",
}

EYEBROW_RE=re.compile(r'(<p\b[^>]*class=["\'][^"\']*\beyebrow\b[^"\']*["\'][^>]*>)([\s\S]*?)(</p>)',re.I)
TAG_SEQ=re.compile(r'</?([A-Za-z][\w-]*)\b[^>]*>')

def shape(s):
    return [("/" if x.group()[1:2]=="/" else "")+x.group(1).lower() for x in TAG_SEQ.finditer(s)]

def polish(index):
    enpath,papath=PAGES[index]
    source=(ROOT/enpath).read_text(encoding="utf-8")
    target=ROOT/papath
    if not target.exists():raise FileNotFoundError(papath)
    text=target.read_text(encoding="utf-8")
    initial=text
    title,h1,desc=SEO[index]
    text=re.sub(r'<title>[\s\S]*?</title>',lambda m:"<title>"+html.escape(title,quote=False)+"</title>",text,count=1,flags=re.I)
    def rewrite_meta(m):
        tag=m.group()
        typ=re.search(r'\b(?:name|property)=["\']([^"\']+)["\']',tag,re.I)
        if not typ:return tag
        field=typ.group(1).lower()
        if field in ("og:title","twitter:title"): value=title
        elif field=="description":value=desc
        else:return tag
        return re.sub(r'\bcontent=(["\'])(.*?)\1',lambda u:'content='+u.group(1)+html.escape(value,quote=True)+u.group(1),tag,flags=re.I|re.S)
    text=re.sub(r'<meta\b[^>]*>',rewrite_meta,text,flags=re.I)
    hmatch=re.search(r'(<h1\b[^>]*>)([\s\S]*?)(</h1>)',text,re.I)
    if not hmatch:raise ValueError("H1 missing on "+papath)
    def seth(m):return m.group(1)+h1+m.group(3)
    text=re.sub(r'(<h1\b[^>]*>)([\s\S]*?)(</h1>)',seth,text,count=1,flags=re.I)
    original_en=EYEBROW_RE.findall(source)
    matches=EYEBROW_RE.findall(text)
    if len(matches)!=len(original_en):
        raise ValueError("Eyebrow count differs on "+papath)
    idx=[0]
    def change_eyebrow(m):
        j=idx[0];idx[0]+=1
        en_label=html.unescape(re.sub(r'<[^>]+>','',original_en[j][1])).strip()
        label=EYEBROWS.get(en_label)
        if label is None:return m.group()
        if re.search(r'<[^>]+>',m.group(2)):return m.group()
        return m.group(1)+html.escape(label,quote=False)+m.group(3)
    text=EYEBROW_RE.sub(change_eyebrow,text)
    # Keep original user-facing page markup, CSS and JavaScript intact.
    if shape(initial)!=shape(text):
        raise AssertionError("Editorial changed HTML tags: "+papath)
    target.write_text(text,encoding="utf-8")
    print("EDITORIAL_PASS",papath,"eyebrows",len(matches),flush=True)
    return papath

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit("python _pa_editorial.py PAGE_INDEX")
    polish(int(sys.argv[1]))
