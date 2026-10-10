#!/usr/bin/env python3
"""Sequential English-sitemap -> Korean HTML localization, strict technical-data and DOM checks."""
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
    ("index.html", "ko/index.html"),
    ("best-vps-for-n8n.html", "ko/best-vps-for-n8n.html"),
    ("about.html", "ko/about.html"),
    ("n8n-backup-and-restore.html", "ko/n8n-backup-restore.html"),
    ("contact.html", "ko/contact.html"),
    ("install-n8n-on-a-vps.html", "ko/install-n8n-vps-docker.html"),
    ("n8n-cloud-vs-self-hosted.html", "ko/n8n-cloud-vs-self-hosted.html"),
    ("n8n-vps-requirements.html", "ko/n8n-vps-requirements.html"),
    ("privacy.html", "ko/privacy.html"),
    ("secure-n8n-on-a-vps.html", "ko/n8n-vps-security.html"),
    ("n8n-queue-mode.html", "ko/n8n-queue-mode.html"),
]
LOOKUP = {a: b.removeprefix("ko/") for a,b in PAGES}
SEP = "\n\n§§§\n\n"
CACHE_PATH = ROOT / ".github" / "ko-translation-cache.json"
LANGUAGE_NAMES = {
    "English", "Español", "Русский", "Português", "Deutsch", "हिन्दी", "বাংলা",
    "日本語", "ਪੰਜਾਬੀ", "मराठी", "తెలుగు", "தமிழ்", "Türkçe", "Tiếng Việt",
    "한국어", "Français", "Italiano", "Polski", "n8nVPS", "n8n", "VDSina",
}
EXACT = {
    "FAQ": "자주 묻는 질문",
    "Skip to content": "콘텐츠로 건너뛰기",
    "FAQPage": "FAQPage",
    "Privacy": "개인정보 처리방침",
    "Contact": "문의",
    "About": "소개",
    "Choose your VPS": "VPS 선택",
    "View requirements": "요구사항 보기",
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
    if re.search(r"§\s*\d",s):
        raise ValueError(f"Unresolved technical sentinels: {s[:160]!r}")
    return s

def remote_translate(input_text: str) -> str:
    """Translate a batch of independent English segments to idiomatic Korean."""
    query=urllib.parse.urlencode({"client":"gtx","sl":"en","tl":"ko","dt":"t","q":input_text})
    url="https://translate.googleapis.com/translate_a/single?"+query
    error=None
    for attempt in range(7):
        try:
            request=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; article-localizer/1.0)"})
            with urllib.request.urlopen(request,timeout=35) as response:
                obj=json.load(response)
            output="".join(part[0] or "" for part in obj[0] if part and part[0] is not None)
            if not output.strip():raise ValueError("Translation service returned empty text")
            return output
        except Exception as exc:
            error=exc
            print("KOREAN_TRANSLATE_RETRY",attempt,type(exc).__name__,str(exc)[:120],flush=True)
            time.sleep(min(40,2**attempt+.4))
    raise RuntimeError("Korean translation endpoint unavailable") from error

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
    print("KOREAN_SAFE_TRANSLATION_FALLBACK",raw[:110],flush=True)
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
        print("KOREAN_BATCH_RETRY_SEPARATELY",len(items),str(exc)[:170],flush=True)
        translated=[]
        for item,(part,stored) in zip(items,masked):
            one=remote_translate(part)
            try:
                translated.append(restore_numbers(one.strip(),stored))
            except ValueError:
                translated.append(preserve_exact_when_model_drops_token(item))
    if len(translated)!=len(items) or any(not x.strip() for x in translated):
        raise AssertionError("Korean translation omitted a supplied text segment")
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
    print("KOREAN_SLOTS_VERIFIED",len(cache),flush=True)

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
                if lang=="vi":return name+BASE+japath+end
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
            if k=="inLanguage" and x=="en":v[k]="ko"
            elif k in TEXT_FIELDS and isinstance(x,str):
                if eligible(x):v[k]=EXACT.get(x,cache[x]) if x not in EXACT else EXACT[x]
            elif k in ("item","url") and isinstance(x,str) and x==BASE+enpath:
                v[k]=BASE+japath
            elif k=="item" and x==BASE:v[k]=BASE+"ko/"
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
    output=re.sub(r'(<html\b[^>]*\blang=["\'])en(["\'])',r'\1vi\2',output,count=1,flags=re.I)
    output=re.sub(r'(<div\b[^>]*class=["\'][^"\']*\blang-switch\b[^"\']*["\'][^>]*>\s*<button\b[^>]*>)[^<]*(</button>)',lambda m:m.group(1)+"한국어 ▾"+m.group(2),output,flags=re.I)
    # Keep endonyms in the language menu; make both header and footer link to the same article.
    def fix_language_link(m):
        tag,label=m.group(1),m.group(2)
        if label=="English":
            tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+enpath+'"',tag,count=1)
            tag=re.sub(r'\s+aria-current=["\']page["\']','',tag)
        elif label=="한국어":
            tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+japath+'"',tag,count=1)
            if "aria-current=" not in tag:tag=tag[:-1]+' aria-current="page">'
        return tag+label+"</a>"
    output=re.sub(r'(<a\b[^>]*>)(English|Tiếng Việt)</a>',fix_language_link,output)
    # Korean alternate must be present even on English source pages missing the tag.
    if not re.search(r'<link\b[^>]*hreflang=["\']ko["\']',output,re.I):
        output=output.replace("</head>",'<link rel="alternate" hreflang="ko" href="'+BASE+japath+'"/></head>',1)
    # Keep sitemap canonical and language alternates at the directory URL for homepage.
    output=output.replace(BASE+"ko/index.html",BASE+"ko/")
    validate(source,output,enpath,japath)
    dest=ROOT/japath
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(output,encoding="utf-8")
    print(f"PAGE PASS {enpath} -> {japath}; chars={len(output)} korean_chars={(len(re.findall(r'[가-힣]',output)))} requests={requests_made}",flush=True)

def validate(src,out,enpath,japath):
    def signature(x):
        return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower() for m in re.finditer(r'</?([a-z][\w-]*)\b[^>]*>',x,re.I) if m.group(1).lower() not in ("link","meta")]
    if signature(src)!=signature(out):raise AssertionError(f"HTML structure changed: {enpath}")
    if [m.group(1) for m in CSS_TAG.finditer(src)] != [m.group(1) for m in CSS_TAG.finditer(out)]:
        raise AssertionError(f"CSS changed: {enpath}")
    if [m.group(1) for m in JS_TAG.finditer(src)] != [m.group(1) for m in JS_TAG.finditer(out)]:
        raise AssertionError(f"JavaScript changed: {enpath}")
    if not re.search(r'<html\b[^>]*lang=["\']ko',out,re.I):
        raise AssertionError("lang vi missing")
    canonical = BASE + ("vi/" if japath == "ko/index.html" else japath)
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
    if len(re.findall(r'[가-힣]',out))<5:
        raise AssertionError("Korean content absent")
    if "<!--JSONLD_" in out:raise AssertionError("JSON-LD placeholder unresolved")
    if "</html>" not in out.lower():raise AssertionError("HTML not complete")

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _vi_translate_full.py PAGE_INDEX (0..10)")
    i=int(sys.argv[1])
    if not 0 <= i < len(PAGES):raise SystemExit("Page out of range")
    a,b=PAGES[i]
    print(f"PAGE {i+1}/{len(PAGES)} START: {a}",flush=True)
    verify_source_sitemap()
    process(a,b)
