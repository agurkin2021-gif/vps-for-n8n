#!/usr/bin/env python3
"""Sequential EN -> JA HTML localization, strict technical-data and DOM checks."""
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
    ("index.html", "pa/index.html"),
    ("best-vps-for-n8n.html", "pa/best-vps-for-n8n.html"),
    ("about.html", "pa/about.html"),
    ("n8n-backup-and-restore.html", "pa/n8n-backup-restore.html"),
    ("contact.html", "pa/contact.html"),
    ("install-n8n-on-a-vps.html", "pa/install-n8n-vps-docker.html"),
    ("n8n-cloud-vs-self-hosted.html", "pa/n8n-cloud-vs-self-hosted.html"),
    ("n8n-vps-requirements.html", "pa/n8n-vps-requirements.html"),
    ("privacy.html", "pa/privacy.html"),
    ("secure-n8n-on-a-vps.html", "pa/n8n-vps-security.html"),
    ("n8n-queue-mode.html", "pa/n8n-queue-mode.html"),
]
LOOKUP = {a: b.removeprefix("pa/") for a,b in PAGES}
SEP = "\n\n§§§\n\n"
CACHE_PATH = ROOT / ".github" / "pa-translation-cache.json"
LANGUAGE_NAMES = {
    "English", "Español", "Русский", "Português", "Deutsch", "हिन्दी", "বাংলা",
    "ਪੰਜਾਬੀ", "ਪੰਜਾਬੀ", "मराठी", "తెలుగు", "தமிழ்", "Türkçe", "Tiếng Việt",
    "한국어", "Français", "Italiano", "Polski", "n8nVPS", "n8n", "VDSina",
}
EXACT = {
    "FAQ": "ਅਕਸਰ ਪੁੱਛੇ ਜਾਣ ਵਾਲੇ ਸਵਾਲ",
    "FAQPage": "FAQPage",
    "Privacy": "ਪਰਦੇਦਾਰੀ",
    "Contact": "ਸੰਪਰਕ",
    "About": "ਸਾਡੇ ਬਾਰੇ",
    "Choose your VPS": "ਆਪਣਾ VPS ਚੁਣੋ",
    "View requirements": "ਲੋੜਾਂ ਵੇਖੋ",
}
MASK_PATTERN = re.compile(
    r'\$\s*\d+(?:[.,]\d+)*(?:\s*/\s*(?:day|month|year|mo))?'
    r'|https?://[^\s<>"\']+'
    r'|\b(?:n8nVPS|VDSina|Hostinger|OVHcloud|Bluehost|DreamHost|Contabo|PostgreSQL|SQLite|Docker|GitHub|Cloudflare|Redis|Ubuntu|Linux|Caddy|ConoHa|XServer|n8n|SaaS)\b'
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
    for idx, token in enumerate(stored):
        pat = r"§\s*" + str(idx) + r"\s*§"
        s, n = re.subn(pat, lambda _m: token, s)
        if n != 1:
            raise ValueError(f"Technical token {idx} disappeared or duplicated: {s[:150]!r}")
    return s

def remote_translate(s: str) -> str:
    global requests_made
    query = urllib.parse.urlencode({"client":"gtx","sl":"en","tl":"pa","dt":"t","q":s})
    url = "https://translate.googleapis.com/translate_a/single?" + query
    error=None
    for attempt in range(6):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 (compatible; localization-audit/1.0)"})
            with urllib.request.urlopen(req, timeout=35) as response:
                obj=json.load(response)
            requests_made += 1
            text="".join(part[0] or "" for part in obj[0] if part and part[0] is not None)
            if not text.strip():
                raise ValueError("Empty Punjabi translation")
            return text
        except Exception as exc:
            error=exc
            print(f"translate_retry={attempt} detail={type(exc).__name__}: {str(exc)[:180]}", flush=True)
            time.sleep(min(30, 2**attempt + 0.4))
    raise RuntimeError("Translation service failed after retries") from error

def translate_group(items: list[str]) -> list[str]:
    preps=[mark_numbers(x) for x in items]
    joint=SEP.join(p for p,_ in preps)
    try:
        if len(joint)>3800: raise ValueError("batch too long")
        output=remote_translate(joint)
        parts=output.split("§§§")
        if len(parts)!=len(items):
            raise ValueError(f"Segment marker count {len(parts)} vs {len(items)}")
        translated=[restore_numbers(v.strip(), stored) for v,(_,stored) in zip(parts,preps)]
    except Exception as e:
        if len(items)==1:
            raise
        print(f"batch_fallback size={len(items)}: {e}",flush=True)
        translated=[]
        for item in items:
            p,nums=mark_numbers(item)
            translated.append(restore_numbers(remote_translate(p).strip(),nums))
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
                if lang=="pa":return name+BASE+japath+end
                if lang in ("en","x-default"):return name+BASE+enpath+end
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
        if eligible(key):return name+"="+quote+html.escape(EXACT.get(key,cache[key]) if key not in EXACT else EXACT[key],quote=True)+quote
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
            if k=="inLanguage" and x=="en":v[k]="pa"
            elif k in TEXT_FIELDS and isinstance(x,str):
                if eligible(x):v[k]=EXACT.get(x,cache[x]) if x not in EXACT else EXACT[x]
            elif k in ("item","url") and isinstance(x,str) and x==BASE+enpath:
                v[k]=BASE+japath
            elif k=="item" and x==BASE:v[k]=BASE+"pa/"
            else:patch_json(x,enpath,japath)
    elif isinstance(v,list):
        for x in v:patch_json(x,enpath,japath)

def process(enpath,japath):
    source=(ROOT/enpath).read_text(encoding="utf-8")
    # Match only head JSON-LD scripts; other JS is never translated or reformatted.
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
    output=re.sub(r'(<html\b[^>]*\blang=["\'])en(["\'])',r'\1ja\2',output,count=1,flags=re.I)
    output=re.sub(r'(<div\b[^>]*class=["\'][^"\']*\blang-switch\b[^"\']*["\'][^>]*>\s*<button\b[^>]*>)[^<]*(</button>)',lambda m:m.group(1)+"ਪੰਜਾਬੀ ▾"+m.group(2),output,flags=re.I)
    # Keep endonyms in the language menu; make both header and footer link to the same article.
    def fix_language_link(m):
        tag,label=m.group(1),m.group(2)
        if label=="English":
            tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+enpath+'"',tag,count=1)
            tag=re.sub(r'\s+aria-current=["\']page["\']','',tag)
        elif label=="ਪੰਜਾਬੀ":
            tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+japath+'"',tag,count=1)
            if "aria-current=" not in tag:tag=tag[:-1]+' aria-current="page">'
        return tag+label+"</a>"
    output=re.sub(r'(<a\b[^>]*>)(English|日本語)</a>',fix_language_link,output)
    # Punjabi alternate must be present even on English source pages missing the tag.
    if not re.search(r'<link\b[^>]*hreflang=["\']ja["\']',output,re.I):
        output=output.replace("</head>",'<link rel="alternate" hreflang="pa" href="'+BASE+japath+'"/></head>',1)
    # Keep sitemap canonical and language alternates at the directory URL for homepage.
    output=output.replace(BASE+"pa/index.html",BASE+"pa/")
    validate(source,output,enpath,japath)
    dest=ROOT/japath
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(output,encoding="utf-8")
    print(f"PAGE PASS {enpath} -> {japath}; chars={len(output)} punjabi={(len(re.findall(r'[\u0a00-\u0a7f]',output)))} requests={requests_made}",flush=True)

def validate(src,out,enpath,japath):
    def signature(x):
        return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower() for m in re.finditer(r'</?([a-z][\w-]*)\b[^>]*>',x,re.I) if m.group(1).lower() not in ("link","meta")]
    if signature(src)!=signature(out):raise AssertionError(f"HTML structure changed: {enpath}")
    if [m.group(1) for m in CSS_TAG.finditer(src)] != [m.group(1) for m in CSS_TAG.finditer(out)]:
        raise AssertionError(f"CSS changed: {enpath}")
    if [m.group(1) for m in JS_TAG.finditer(src)] != [m.group(1) for m in JS_TAG.finditer(out)]:
        raise AssertionError(f"JavaScript changed: {enpath}")
    if not re.search(r'<html\b[^>]*lang=["\']ja',out,re.I):
        raise AssertionError("lang ja missing")
    canonical = BASE + ("pa/" if japath == "pa/index.html" else japath)
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
    if len(re.findall(r'[\u3040-\u30ff\u4e00-\u9fff]',out))<20:
        raise AssertionError("Punjabi content absent")
    if "<!--JSONLD_" in out:raise AssertionError("JSON-LD placeholder unresolved")
    if "</html>" not in out.lower():raise AssertionError("HTML not complete")

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _pa_translate_full.py PAGE_INDEX (0..10)")
    i=int(sys.argv[1])
    if not 0 <= i < len(PAGES):raise SystemExit("Page out of range")
    a,b=PAGES[i]
    print(f"PAGE {i+1}/{len(PAGES)} START: {a}",flush=True)
    process(a,b)
