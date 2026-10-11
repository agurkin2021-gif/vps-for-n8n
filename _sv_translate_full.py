#!/usr/bin/env python3
"""Sequential English-sitemap -> Swedish HTML localization, strict technical-data and DOM checks."""
from __future__ import annotations
import collections
import html
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
BASE = "https://agurkin2021-gif.github.io/vps-for-n8n/"
PAGES = [
    ("index.html", "sv/index.html"),
    ("best-vps-for-n8n.html", "sv/best-vps-for-n8n.html"),
    ("about.html", "sv/about.html"),
    ("n8n-backup-and-restore.html", "sv/n8n-backup-and-restore.html"),
    ("contact.html", "sv/contact.html"),
    ("install-n8n-on-a-vps.html", "sv/install-n8n-on-a-vps.html"),
    ("n8n-cloud-vs-self-hosted.html", "sv/n8n-cloud-vs-self-hosted.html"),
    ("n8n-vps-requirements.html", "sv/n8n-vps-requirements.html"),
    ("privacy.html", "sv/privacy.html"),
    ("secure-n8n-on-a-vps.html", "sv/secure-n8n-on-a-vps.html"),
    ("n8n-queue-mode.html", "sv/n8n-queue-mode.html"),
]
LOOKUP = {a: b.removeprefix("sv/") for a,b in PAGES}
SEP = "\n\n§§§\n\n"
CACHE_PATH = ROOT / ".github" / "sv-translation-cache.json"
LANGUAGE_NAMES = {
    "English", "Español", "Русский", "Português", "Deutsch", "हिन्दी", "বাংলা",
    "日本語", "ਪੰਜਾਬੀ", "मराठी", "తెలుగు", "தமிழ்", "Türkçe", "Tiếng Việt",
    "한국어", "Français", "Italiano", "Polski", "Svenska", "n8nVPS", "n8n", "VDSina",
}
LANGUAGE_NAMES.update({"Svenska", "Català", "Română", "Nederlands", "ไทย", "Azərbaycanca", "Ελληνικά", "العربية", "فارسی", "Bahasa Indonesia", "繁體中文", "简体中文"})
LANGUAGE_NAMES.update({"Magyar","Svenska","Svenska"})
EXACT = {
    "FAQ": "Vanliga frågor",
    "Skip to content": "Hoppa till innehållet",
    "Privacy": "Integritet",
    "Contact": "Kontakt",
    "About": "Om oss",
    "Choose your VPS": "Välj VPS",
    "View requirements": "Se systemkraven",
    "Find your configuration": "Hitta rätt konfiguration",
    "Best VPS for n8n: 6 provider options": "Bästa VPS för n8n: 6 leverantörsalternativ",
    "Best VPS for n8n in 2026: 6 Providers Compared": "Bästa VPS för n8n 2026: 6 leverantörer jämförda",
    "n8n VPS Requirements": "Systemkrav för n8n på VPS",
    "n8n Backup and Restore": "Säkerhetskopiering och återställning av n8n",
    "n8n Cloud vs Self-Hosted": "n8n Cloud jämfört med egen drift",
    "Secure n8n on a VPS": "Säkra n8n på en VPS",
    "Install n8n on a VPS": "Installera n8n på en VPS",
    "n8n Queue Mode": "Köläge i n8n",
    "VPS for n8n from $0.07/Day - Plans & Sizing Guide": "VPS för n8n från $0.07/Day – abonnemang och dimensioneringsguide",
    "Docker Compose": "Docker Compose",
    "Reverse proxy": "Omvänd proxy",
    "TLS termination": "TLS-terminering",
    "PostgreSQL credentials": "Inloggningsuppgifter för PostgreSQL",
    "CHOOSE THE RESOURCES YOUR WORKFLOWS NEED": "VÄLJ RESURSER UTIFRÅN DINA ARBETSFLÖDENS BEHOV",
    "YOUR DEPLOYMENT PLAN": "DIN DRIFTSÄTTNINGSPLAN",
    "Which VPS fits your n8n workload?": "Vilken VPS passar din n8n-belastning?",
    "Small automations & always-on workflows": "Små automatiseringar och arbetsflöden som körs dygnet runt",
    "Scheduled syncs & notifications": "Schemalagda synkroniseringar och aviseringar",
    "CRM, leads & online-store workflows": "Arbetsflöden för CRM, leads och e-handel",
    "Imports, documents & heavier jobs": "Importer, dokument och mer krävande uppgifter",
    "Turn your configuration into a VPS order": "Gå från konfiguration till VPS-beställning",
    "Pick the matching server": "Välj en server som passar",
    "Choose your Linux setup": "Välj Linux-konfiguration",
    "Prepare the application": "Förbered applikationen",
    "Connect your automations": "Anslut dina automatiseringar",
    "When a VPS is the right choice for n8n": "När en VPS är rätt val för n8n",
    "Choose your own VPS for control": "Välj en egen VPS för större kontroll",
    "Choose Cloud for managed hosting": "Välj Cloud om du vill ha hanterad drift",
    "What to look for in an n8n VPS": "Vad du bör tänka på när du väljer VPS för n8n",
    "Start with one instance. Add workers when needed.": "Börja med en instans. Lägg till workers vid behov.",
    "Make your n8n setup ready for daily work": "Gör din n8n-miljö redo för daglig drift",
    "Keep your data persistent": "Se till att data lagras beständigt",
    "Connect a secure endpoint": "Använd en säker anslutningspunkt",
    "Keep recovery straightforward": "Gör återställningen enkel",
    "Compare n8n VPS providers at a glance": "Jämför VPS-leverantörer för n8n i korthet",
    "Which provider model fits your n8n setup?": "Vilken leverantörsmodell passar din n8n-miljö?",
    "The criteria that separate a good n8n VPS from a bad fit": "Det som skiljer en lämplig VPS för n8n från ett dåligt val",
    "Setup path": "Installationsväg",
    "Support boundary": "Supportens omfattning",
    "Backups and restore": "Säkerhetskopiering och återställning",
    "Region and latency": "Region och svarstid",
    "Migration and portability": "Migrering och flyttbarhet",
    "Scaling path": "Vägen till skalning",
    "Renewal and extras": "Förnyelse och tillägg",
    "Operational control": "Kontroll över driften",
    "Compare ongoing cost, not only the launch offer": "Jämför löpande kostnader, inte bara introduktionserbjudandet",
    "Short recommendations without pretending one provider wins everything": "Korta rekommendationer utan att utse en leverantör till bäst på allt",
    "Configurations": "Konfigurationer",
    "Requirements": "Systemkrav",
    "Scaling": "Skalning",
    "Sources": "Källor",
    "Editorial scope": "Redaktionell inriktning",
    "Independent infrastructure guide for self-hosted n8n.": "Oberoende guide till infrastruktur för egen drift av n8n.",
    "Independent guide to choosing and running VPS infrastructure for n8n.": "Oberoende guide till att välja och driva VPS-infrastruktur för n8n."
}

MASK_PATTERN = re.compile(
    r'\$\s*\d+(?:[.,]\d+)*(?:\s*/\s*(?i:day|month|year|mo))?'
    r'|https?://[^\s<>"\']+'
    r'|\b(?:n8nVPS|VDSina|Hostinger|OVHcloud|Bluehost|DreamHost|Contabo|PostgreSQL|SQLite|Docker|GitHub|Cloudflare|Redis|Ubuntu|Linux|Caddy|ConoHa|XServer|n8n|SaaS|Standard)\b'
    r'|\b(?:N8N_[A-Z0-9_]+|EXECUTIONS_[A-Z0-9_]+|QUEUE_[A-Z0-9_]+|DB_[A-Z0-9_]+|POSTGRES_[A-Z0-9_]+|WEBHOOK_[A-Z0-9_]+)\b'
    r'|\b(?:VPS|VDS|RAM|CPU|GPU|API|HTTP|HTTPS|SSH|TLS|MFA|JSON|FAQPage|NVMe|SSD|CLI|DNS|OOM|I/O|SLA|USD|GB|TB|MiB|LLM)\b'
    r'|(?<![A-Za-z0-9])\d+(?:[.,]\d+)*'
)
NUMBER = re.compile(r"(?<![A-Za-z])\d+(?:[.,]\d+)*")
TECH_ONLY = re.compile(r"^[\d\s.,:$%/+–—\-·()vCPURAMGBTMBpsHHzZ]+$", re.I)
USER_ATTR = {"alt", "aria-label", "placeholder", "title", "aria-valuetext"}
JS_TAG = re.compile(r'<script\b(?![^>]*application/ld\+json)[^>]*>([\s\S]*?)</script>', re.I)
CSS_TAG = re.compile(r'<style\b[^>]*>([\s\S]*?)</style>', re.I)
TAG_PATTERN = re.compile(r"<[^>]*>", re.S)
ELIGIBLE_META = {"description", "og:title", "og:description", "twitter:title", "twitter:description", "twitter:image:alt"}
TEXT_FIELDS = {"name", "description", "headline", "alternativeHeadline", "text", "articleBody", "caption", "inLanguage"}

if CACHE_PATH.exists():
    try:
        cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
else:
    cache = {}
LANGUAGE_NAMES.update({'Čeština', 'Svenska', 'Български', 'Magyar'})
requests_made = 0

def eligible(s: str) -> bool:
    s = html.unescape(s).strip()
    if not s or s in LANGUAGE_NAMES or s in {"&", "•", "→", "●", "×"}:
        return False
    if s in EXACT:
        return True
    if not re.search(r"[A-Za-z]", s):
        return False
    if TECH_ONLY.fullmatch(s) or s.startswith(("https://", "http://", "mailto:")):
        return False
    return True

def mark_numbers(s: str):
    stored=[]
    def replace(m):
        stored.append(m.group())
        return "§" + str(len(stored)-1) + "§"
    return MASK_PATTERN.sub(replace, s), stored

def restore_numbers(s: str, stored):
    # IndicTrans may remove one '§' or separate it from the numeric sentinel.
    # Each technical value is restored exactly once; ambiguity remains a hard error.
    for idx in range(len(stored)-1,-1,-1):
        token=stored[idx]
        nstr=str(idx)
        candidates=[
            r"§\s*"+nstr+r"(?!\d)(?:\s*§)?",
            r"(?<!\d)"+nstr+r"(?!\d)\s*§",
            r"(?<![\dA-Za-z])"+nstr+r"(?!\d)",
        ]
        hits=[]
        for pat in candidates:
            hits=list(re.finditer(pat,s))
            if hits:
                if len(hits)!=1:
                    raise ValueError(f"Ambiguous technical token {idx}: {s[:160]!r}")
                break
        if not hits:
            raise ValueError(f"Technical token {idx} disappeared: {s[:160]!r}")
        m=hits[0]
        # Repair model-collapsed adjacency: 'Linux2 §' -> 'Linux VPS'.
        prefix=" " if m.start()>0 and s[m.start()-1].isalnum() else ""
        suffix=" " if m.end()<len(s) and s[m.end()].isalnum() else ""
        s=s[:m.start()]+prefix+token+suffix+s[m.end():]
    if re.search(r"§\\s*\\d",s):
        raise ValueError(f"Unresolved technical sentinels: {s[:160]!r}")
    return s.replace("§", "")

_OFFLINE_TRANSLATOR = None

def remote_translate(input_text: str) -> str:
    """Translate independent text segments using the installed offline English-to-Swedish model."""
    global _OFFLINE_TRANSLATOR
    if _OFFLINE_TRANSLATOR is None:
        import argostranslate.translate as offline
        languages=offline.get_installed_languages()
        src=next((x for x in languages if x.code=="en"),None)
        dst=next((x for x in languages if x.code=="sv"),None)
        if src is None or dst is None:
            raise RuntimeError("Offline English-to-Swedish language pack not installed")
        _OFFLINE_TRANSLATOR=src.get_translation(dst)
        if _OFFLINE_TRANSLATOR is None:
            raise RuntimeError("Offline English-to-Swedish translator could not load")
    texts=input_text.split(SEP)
    translated=[]
    for item in texts:
        value=_OFFLINE_TRANSLATOR.translate(item)
        if not value.strip():
            raise ValueError("Offline Swedish model returned empty text")
        translated.append(value)
    return SEP.join(translated)

def preserve_exact_when_model_drops_token(raw: str) -> str:
    """Last-resort token-preserving translation, only when sentence masking fails."""
    pieces=[]; last=0
    for m in MASK_PATTERN.finditer(raw):
        pieces.append((False,raw[last:m.start()]))
        pieces.append((True,m.group()))
        last=m.end()
    pieces.append((False,raw[last:]))
    translated=[]
    for protected,part in pieces:
        if protected or not eligible(part.strip()):
            translated.append(part)
        else:
            lead=part[:len(part)-len(part.lstrip())]
            trail=part[len(part.rstrip()):]
            translated.append(lead+remote_translate(part.strip())+trail)
    output="".join(translated)
    for word in {m.group() for m in MASK_PATTERN.finditer(raw)}:
        if raw.count(word)!=output.count(word):
            raise AssertionError("Exact technical token was lost: "+word)
    print("SV_SAFE_TRANSLATION_FALLBACK",raw[:110],flush=True)
    return output

def translate_group(items: list[str]) -> list[str]:
    global requests_made
    if not items:return []
    masked=[mark_numbers(item) for item in items]
    joined=SEP.join(x for x,_ in masked)
    try:
        if len(joined)>2900:raise ValueError("Batch exceeds conservative translation limit")
        output=remote_translate(joined)
        pieces=output.split("§§§")
        if len(pieces)!=len(items):
            raise ValueError(f"Translation changed segment separators: {len(pieces)} vs {len(items)}")
        translated=[restore_numbers(part.strip(),stored) for part,(_,stored) in zip(pieces,masked)]
    except Exception as exc:
        print("SV_BATCH_RETRY_SEPARATELY",len(items),str(exc)[:170],flush=True)
        translated=[]
        for item,(part,stored) in zip(items,masked):
            one=remote_translate(part)
            try:
                translated.append(restore_numbers(one.strip(),stored))
            except ValueError:
                translated.append(preserve_exact_when_model_drops_token(item))
    if len(translated)!=len(items) or any(not x.strip() for x in translated):
        raise AssertionError("Swedish translation omitted a supplied text segment")
    requests_made+=len(items)
    return translated

def translate_candidates(strings: set[str]):
    todo=[]
    for x in sorted(strings):
        if not eligible(x) or x in EXACT or x in cache: continue
        todo.append(x)
    print(f"translation_candidates={len(strings)} uncached={len(todo)}",flush=True)
    batch=[]; count=0
    for idx,item in enumerate(todo):
        if len(item)>3200:
            if batch:
                _finish(batch); batch=[];count=0
            # Break only exceptionally long standalone paragraph at sentence boundaries.
            chunks=re.split(r"(?<=[.!?])\s+(?=[A-Z(])",item)
            if len(chunks)==1:
                chunks=[item[k:k+2400] for k in range(0,len(item),2400)]
            result=[]
            for c in chunks:
                if len(c)>3200: raise ValueError("Oversized unsplittable paragraph")
                result.extend(translate_group([c]))
            cache[item]=" ".join(result)
            continue
        if batch and (count+len(item)+len(SEP)>2400 or len(batch)>=10):
            _finish(batch);batch=[];count=0
        batch.append(item);count+=len(item)+len(SEP)
    if batch:_finish(batch)
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache,ensure_ascii=False,separators=(',',':')),encoding="utf-8")

def _finish(items):
    translations=translate_group(items)
    for en,ja in zip(items,translations):
        if not ja.strip():raise ValueError("Empty translated sentence")
        cache[en]=ja
    CACHE_PATH.parent.mkdir(parents=True,exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache,ensure_ascii=False,separators=(',',':')),encoding="utf-8")
    print("SV_SLOTS_VERIFIED",len(cache),flush=True)

def localize(s: str) -> str:
    key=html.unescape(s).strip()
    if not eligible(key): return s
    translated=EXACT.get(key,cache.get(key))
    if translated is None: raise KeyError("Untranslated text: "+key[:100])
    leading=s[:len(s)-len(s.lstrip())]
    trailing=s[len(s.rstrip()):]
    return leading+html.escape(translated,quote=False)+trailing

def is_eligible_meta(tag: str) -> bool:
    a=re.search(r'\b(?:name|property)=["\']([^"\']+)["\']',tag,re.I)
    return bool(a and a.group(1).lower() in ELIGIBLE_META)

def tag_text_candidates(tag: str) -> list[str]:
    result=[]
    for m in re.finditer(r'(?<![\w:-])(alt|aria-label|placeholder|title|aria-valuetext)=["\']([^"\']+)["\']',tag,re.I):
        if eligible(m.group(2)):result.append(html.unescape(m.group(2)).strip())
    if re.match(r'<meta\b',tag,re.I) and is_eligible_meta(tag):
        m=re.search(r'\bcontent=["\']([^"\']+)["\']',tag,re.I)
        if m and eligible(m.group(1)):result.append(html.unescape(m.group(1)).strip())
    return result

def patch_tag(tag: str,enpath: str,japath: str):
    is_link=bool(re.match(r'<link\b',tag,re.I))
    is_a=bool(re.match(r'<a\b',tag,re.I))
    def rewrite_url(m):
        name,value,end=m.group(1),m.group(2),m.group(3)
        field=name.split("=")[0].lower()
        if field=="href" and is_link:
            if re.search(r'\brel=["\']canonical["\']',tag,re.I):
                return name+BASE+japath+end
            mlang=re.search(r'\bhreflang=["\']([^"\']+)',tag,re.I)
            if mlang:
                lang=mlang.group(1).lower()
                if lang=="sv":return name+BASE+japath+end
                if lang in ("en","x-default"):return name+BASE+enpath+end
        if is_a and value.startswith(BASE):
            local=value[len(BASE):]
            bare,hashsep,fragment=local.partition("#")
            if bare in LOOKUP:
                return name+BASE+"sv/"+LOOKUP[bare]+(hashsep+fragment if hashsep else "")+end
            if bare=="":
                return name+BASE+"sv/"+(hashsep+fragment if hashsep else "")+end
        if re.match(r"^(?:https?://|//|/|#|data:|mailto:|tel:)",value,re.I):
            return m.group(0)
        if value.startswith("../"):return m.group(0)
        path,sep,fragment=value.partition("#")
        if (field=="href" and is_a) and path in LOOKUP:
            return name+LOOKUP[path]+(sep+fragment if sep else "")+end
        if path=="styles.css" and is_link:
            return name+"../styles.css"+end
        if path=="favicon.svg" and is_link:
            return name+"../favicon.svg"+end
        if field=="src" and path and not path.startswith(("./","../")):
            return name+"../"+value+end
        if field=="href" and not is_a and not is_link and path.endswith((".svg",".png",".jpg",".webp")):
            return name+"../"+value+end
        return m.group(0)
    tag=re.sub(r'\b((?:href|src|poster)=["\'])([^"\']*)(["\'])',rewrite_url,tag,flags=re.I)
    if re.match(r'<meta\b',tag,re.I) and re.search(r'\bproperty=["\']og:url',tag,re.I):
        tag=re.sub(r'\bcontent=(["\'])[^"\']*\1',lambda m:'content='+m.group(1)+BASE+japath+m.group(1),tag)
    def trans_attr(m):
        name,quote,value=m.group(1),m.group(2),m.group(3)
        key=html.unescape(value).strip()
        if eligible(key):return name+"="+quote+html.escape(EXACT.get(key,cache.get(key, key)) if key not in EXACT else EXACT[key],quote=True)+quote
        return m.group(0)
    tag=re.sub(r'\b(alt|aria-label|placeholder|title|aria-valuetext)=(["\'])(.*?)\2',trans_attr,tag,flags=re.I|re.S)
    if re.match(r'<meta\b',tag,re.I) and is_eligible_meta(tag):
        tag=re.sub(r'\bcontent=(["\'])(.*?)\1',lambda m:'content='+m.group(1)+html.escape(EXACT.get(html.unescape(m.group(2)).strip(),cache.get(html.unescape(m.group(2)).strip(),html.unescape(m.group(2)))),quote=True)+m.group(1),tag,flags=re.I|re.S)
    return tag

def json_values(v) -> list[str]:
    out=[]
    if isinstance(v,dict):
        for k,x in v.items():
            if k in TEXT_FIELDS and isinstance(x,str) and k!="inLanguage" and eligible(x):out.append(x)
            else:out.extend(json_values(x))
    elif isinstance(v,list):
        for x in v:out.extend(json_values(x))
    return out

def patch_json(v,enpath,japath):
    if isinstance(v,dict):
        for k,x in v.items():
            if k=="inLanguage" and x=="en":v[k]="sv"
            elif k in TEXT_FIELDS and isinstance(x,str):
                if eligible(x):v[k]=EXACT.get(x,cache.get(x,x)) if x not in EXACT else EXACT[x]
            elif k in ("item","url") and isinstance(x,str) and x==BASE+enpath:
                v[k]=BASE+japath
            elif k=="item" and x==BASE:v[k]=BASE+"sv/"
            else:patch_json(x,enpath,japath)
    elif isinstance(v,list):
        for x in v:patch_json(x,enpath,japath)

def verify_source_sitemap():
    import xml.etree.ElementTree as ET
    urls=[x.text for x in ET.parse(ROOT / "sitemap.xml").findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    root_urls={u.removeprefix(BASE) for u in urls if u and u.startswith(BASE) and (
        u==BASE or ("/" not in u.removeprefix(BASE) and u.endswith(".html"))
    )}
    expected={"" if en=="index.html" else en for en,_ in PAGES}
    if root_urls!=expected:
        raise AssertionError(f"Authoritative English sitemap changed: missing={expected-root_urls}, extra={root_urls-expected}")
    return len(root_urls)

def process(enpath,japath):
    source=(ROOT/enpath).read_text(encoding="utf-8")
    # JSON-LD text is translated, while executable JavaScript and CSS are unchanged.
    scripts=[]
    def hide_schema(m):
        scripts.append((m.group(1),m.group(2),m.group(3)))
        return "<!--JSONLD_"+str(len(scripts)-1)+"-->"
    protected=re.sub(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)([\s\S]*?)(</script>)',hide_schema,source,flags=re.I)
    tokens=re.split(r'(<[^>]*>)',protected)
    candidates=set()
    skip=None
    for part in tokens:
        if part.startswith("<"):
            open_tag=re.match(r'<(script|style|pre|code)\b',part,re.I)
            close_tag=re.match(r'</(script|style|pre|code)\s*>',part,re.I)
            if open_tag:skip=open_tag.group(1).lower()
            elif close_tag and skip==close_tag.group(1).lower():skip=None
            if skip is None:candidates.update(tag_text_candidates(part))
        elif skip is None and eligible(part):
            candidates.add(html.unescape(part).strip())
    objs=[]
    for start,payload,end in scripts:
        obj=json.loads(payload)
        objs.append((start,obj,end))
        candidates.update(json_values(obj))
    translate_candidates(candidates)
    transformed=[]
    skip=None
    for part in tokens:
        if part.startswith("<"):
            op=re.match(r'<(script|style|pre|code)\b',part,re.I)
            cl=re.match(r'</(script|style|pre|code)\s*>',part,re.I)
            if op:skip=op.group(1).lower()
            elif cl and skip==cl.group(1).lower():skip=None
            transformed.append(part if skip else patch_tag(part,enpath,japath))
        else:
            transformed.append(part if skip else localize(part))
    output="".join(transformed)
    for idx,(start,obj,end) in enumerate(objs):
        patch_json(obj,enpath,japath)
        output=output.replace("<!--JSONLD_"+str(idx)+"-->",start+json.dumps(obj,ensure_ascii=False,separators=(',',':'))+end,1)
    output=re.sub(r'(<html\b[^>]*\blang=["\'])en(["\'])',r'\1cs\2',output,count=1,flags=re.I)
    output=re.sub(r'(<div\b[^>]*class=["\'][^"\']*\blang-switch\b[^"\']*["\'][^>]*>\s*<button\b[^>]*>)[^<]*(</button>)',lambda m:m.group(1)+"Svenska ▾"+m.group(2),output,flags=re.I)
    # Keep endonyms in the language menu; make both header and footer link to the same article.
    def fix_language_link(m):
        tag,label=m.group(1),m.group(2)
        if label=="English":
            tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+enpath+'"',tag,count=1)
            tag=re.sub(r'\s+aria-current=["\']page["\']','',tag)
        elif label=="Svenska":
            tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+japath+'"',tag,count=1)
            if "aria-current=" not in tag:tag=tag[:-1]+' aria-current="page">'
        return tag+label+"</a>"
    output=re.sub(r'(<a\b[^>]*>)(English|Svenska)</a>',fix_language_link,output)
    # Swedish alternate must be present even on English source pages missing the tag.
    if not re.search(r'<link\b[^>]*hreflang=["\']sv["\']',output,re.I):
        output=output.replace("</head>",'<link rel="alternate" hreflang="sv" href="'+BASE+japath+'"/></head>',1)
    # Keep sitemap canonical and language alternates at the directory URL for homepage.
    output=output.replace(BASE+"sv/index.html",BASE+"sv/")
    validate(source,output,enpath,japath)
    dest=ROOT/japath
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(output,encoding="utf-8")
    print(f"PAGE PASS {enpath} -> {japath}; chars={len(output)} untranslated_markers={len(re.findall(r'\\b(?:dan|yang|untuk|dengan|dari|pada|Anda|ini)\\b',html.unescape(re.sub(r'<[^>]*>',' ',output)),re.I))} requests={requests_made}",flush=True)

def validate(src,out,enpath,japath):
    def signature(x):
        return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower() for m in re.finditer(r'</?([a-z][\w-]*)\b[^>]*>',x,re.I) if m.group(1).lower() not in ("link","meta")]
    if signature(src)!=signature(out):raise AssertionError(f"HTML structure changed: {enpath}")
    if [m.group(1) for m in CSS_TAG.finditer(src)] != [m.group(1) for m in CSS_TAG.finditer(out)]:
        raise AssertionError(f"CSS changed: {enpath}")
    if [m.group(1) for m in JS_TAG.finditer(src)] != [m.group(1) for m in JS_TAG.finditer(out)]:
        raise AssertionError(f"JavaScript changed: {enpath}")
    if not re.search(r'<html\b[^>]*lang=["\']sv',out,re.I):
        raise AssertionError("lang sv missing")
    canonical = BASE + ("sv/" if japath == "sv/index.html" else japath)
    if canonical not in out:raise AssertionError("self canonical missing")
    if len(re.findall(r'<h1(?:\s|>)',src,re.I))!=len(re.findall(r'<h1(?:\s|>)',out,re.I)):
        raise AssertionError("H1 count differs")
    def visible(x):
        return html.unescape(re.sub(r'<[^>]*>',' ',re.sub(r'<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>','',x,flags=re.I)))
    n1=collections.Counter(NUMBER.findall(visible(src)))
    n2=collections.Counter(NUMBER.findall(visible(out)))
    if n1-n2:
        raise AssertionError("Original numeric values lost: "+str(n1-n2))
    if n2-n1:
        print("Numerical expressions added by translation (check that they express spelled-out amounts): "+str(n2-n1),flush=True)
    prices=lambda x:collections.Counter(re.findall(r'\$\s*\d+(?:[.,]\d+)*(?:/(?:day|month|year|mo))?',visible(x)))
    if prices(src)!=prices(out):raise AssertionError("Price identifiers changed")
    if len(re.findall(r'\b(?:och|för|med|som|att|inte|utan|från|eller|till|dina|din|ditt|den|det|denna|när|kan|behöver|är|har|ska|om|också|via|på|av|medan|server|säkerhet|lagring|drift|sidan|information|guiden|används|välja)\b',visible(out),re.I))<5:
        raise AssertionError("Swedish content absent")
    if "§" in out:raise AssertionError("Protected-token separator leaked")
    if "<!--JSONLD_" in out:raise AssertionError("JSON-LD placeholder unresolved")
    if "</html>" not in out.lower():raise AssertionError("HTML not complete")

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _sv_translate_full.py PAGE_INDEX (0..10)")
    i=int(sys.argv[1])
    if not 0 <= i < len(PAGES):raise SystemExit("Page out of range")
    a,b=PAGES[i]
    print(f"PAGE {i+1}/{len(PAGES)} START: {a}",flush=True)
    verify_source_sitemap()
    process(a,b)
