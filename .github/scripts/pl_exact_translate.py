#!/usr/bin/env python3
"""Rebuild Polish HTML from exact English DOM, replacing language text only."""
import concurrent.futures, html, json, os, re, sys, time
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from threading import Lock, local
from deep_translator import GoogleTranslator

FILES = {
"index.html":("index.html","VPS pod n8n od 0,07 USD/dzień – dobór serwera","VPS pod n8n"),
"best-vps-for-n8n.html":("najlepszy-vps-pod-n8n.html","Najlepszy VPS pod n8n – porównanie 6 dostawców","Najlepszy VPS pod n8n"),
"n8n-cloud-vs-self-hosted.html":("n8n-cloud-czy-self-hosting.html","n8n Cloud czy self-hosting – koszty i kontrola","n8n Cloud czy self-hosting"),
"n8n-vps-requirements.html":("wymagania-n8n-na-vps.html","Wymagania n8n na VPS – CPU, RAM i dysk","Wymagania n8n na VPS"),
"install-n8n-on-a-vps.html":("jak-zainstalowac-n8n-na-vps.html","Jak zainstalować n8n na VPS – Docker i PostgreSQL","Jak zainstalować n8n na VPS"),
"n8n-backup-and-restore.html":("backup-n8n-przywracanie.html","Backup n8n – kopia zapasowa i przywracanie","Backup n8n i przywracanie"),
"secure-n8n-on-a-vps.html":("jak-zabezpieczyc-n8n-na-vps.html","Jak zabezpieczyć n8n na VPS – HTTPS i dostęp","Jak zabezpieczyć n8n na VPS"),
"n8n-queue-mode.html":("tryb-kolejkowy-n8n.html","Tryb kolejkowy n8n – Redis, workerzy i skalowanie","Tryb kolejkowy n8n")
}
ROOT="https://agurkin2021-gif.github.io/vps-for-n8n/"
AFF="https://www.vdsina.com/?partner=ni8gzrvz75"
OUTDIR=Path("pl")
OUTDIR.mkdir(exist_ok=True)
CACHE_FILE=Path(".github/pl_translate_cache.json")
CACHE={}
if CACHE_FILE.exists(): CACHE=json.loads(CACHE_FILE.read_text(encoding="utf-8"))
LOCK=Lock()
THREAD=local()
def translator():
    if not hasattr(THREAD,"t"): THREAD.t=GoogleTranslator(source="en",target="pl")
    return THREAD.t
def translate_raw(raw):
    if not re.search(r"[A-Za-z]",raw) or raw.strip() in {"VDSina","n8n","Redis","Docker","PostgreSQL","VPS","API","SSH","HTTPS","SSL","FAQ","CPU","RAM","SSD","GB","TB"}: return raw
    leading=raw[:len(raw)-len(raw.lstrip())]; trailing=raw[len(raw.rstrip()):]; core=raw.strip()
    if not core or len(core)>4500: return raw
    if core in CACHE: return leading+CACHE[core]+trailing
    last=None
    for attempt in range(5):
        try:
            result=translator().translate(core)
            if not result or not str(result).strip(): raise ValueError("empty translation")
            result=str(result)
            # Protect product nomenclature from spelling drift.
            result=re.sub(r"(?i)\b(vdsina|wdsina|vdsiną)\b","VDSina",result)
            with LOCK: CACHE[core]=result
            return leading+result+trailing
        except Exception as exc:
            last=exc
            time.sleep(min(12,0.75*(2**attempt)))
    raise RuntimeError("Translation failed: "+core[:100]+"; "+str(last))
class TextPositions(HTMLParser):
    def __init__(self,src):
        super().__init__(convert_charrefs=False)
        self.src=src; self.lines=[0]
        for m in re.finditer("\n",src): self.lines.append(m.end())
        self.stack=[]; self.spans=[]; self.svg=False
    def idx(self): 
        line,col=self.getpos()
        return self.lines[line-1]+col
    def handle_starttag(self,tag,attrs): self.stack.append(tag)
    def handle_startendtag(self,tag,attrs): pass
    def handle_endtag(self,tag):
        for j in range(len(self.stack)-1,-1,-1):
            if self.stack[j]==tag: del self.stack[j:]; break
    def handle_data(self,data):
        if not data.strip() or not re.search("[A-Za-z]",data):return
        if any(t in self.stack for t in ("script","style","code","pre","textarea","noscript","title")):return
        start=self.idx()
        if self.src[start:start+len(data)]!=data:
            raise ValueError("HTML text span mismatch "+repr(data[:65]))
        self.spans.append((start,start+len(data),data))
def modify_text(original):
    p=TextPositions(original);p.feed(original)
    unique=list(dict.fromkeys(data.strip() for _,_,data in p.spans if data.strip()))
    print("  visible text nodes",len(p.spans),"distinct",len(unique),flush=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(translate_raw,unique))
    out=original
    for a,b,s in reversed(p.spans):
        replacement=translate_raw(s)
        if "<" in replacement or ">" in replacement:
            replacement=html.escape(replacement,quote=False)
        out=out[:a]+replacement+out[b:]
    return out,len(p.spans)
def translate_attributes(s):
    # English accessibility descriptions, form hints, summaries. Preserve tag names and attributes.
    attrs=("alt","aria-label","placeholder")
    pat=re.compile(r'(?P<name>\b(?:alt|aria-label|placeholder))="(?P<value>[^"]*)"')
    values=list(dict.fromkeys(m.group("value") for m in pat.finditer(s) if re.search("[A-Za-z]",m.group("value"))))
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool: list(pool.map(translate_raw,values))
    def callback(m):
        original=m.group("value")
        if not re.search("[A-Za-z]",original):return m.group(0)
        translated=html.escape(translate_raw(original),quote=True)
        return f'{m.group("name")}="{translated}"'
    return pat.sub(callback,s)
def patch_urls_and_metadata(s,en_path,pl_path,title,h1):
    target=ROOT+"pl/"+("" if pl_path=="index.html" else pl_path)
    # Metadata: Title map is user-approved; other description translated.
    s=re.sub(r"<title>[\s\S]*?</title>","<title>"+html.escape(title)+"</title>",s,count=1)
    s=re.sub(r'(<html\s+lang=")en(")',r'\1pl\2',s,count=1)
    s=re.sub(r'(<link\b[^>]*\brel="canonical"[^>]*\bhref=")[^"]+(")',lambda m:m.group(1)+target+m.group(2),s,count=1)
    s=re.sub(r'(<link\b[^>]*\bhref=")[^"]+("\s+rel="canonical")',lambda m:m.group(1)+target+m.group(2),s,count=1) if target not in s else s
    # Metadata with flexible attribute order.
    s=re.sub(r'<meta\b[^>]*\bproperty="og:url"[^>]*>',lambda m:re.sub(r'content="[^"]*"',f'content="{target}"',m.group(0)),s)
    s=re.sub(r'<meta\b[^>]*\bproperty="og:title"[^>]*>',lambda m:re.sub(r'content="[^"]*"',f'content="{html.escape(title,quote=True)}"',m.group(0)),s)
    s=re.sub(r'<meta\b[^>]*\b(?:name|property)="(?:description|og:description)"[^>]*>',lambda m:re.sub(r'content="([^"]*)"',lambda z:'content="'+html.escape(translate_raw(html.unescape(z.group(1))),quote=True)+'"',m.group(0)),s)
    # Link rewritten only inside actual href/src, preserving all markup blocks.
    def urlfix(m):
        attr,value=m.group(1),m.group(2)
        if value.startswith(("https://","http://","mailto:","tel:","#","data:","javascript:")):return m.group(0)
        if attr=="src" and value.startswith("./"):value=value[2:]
        name,sep,fragment=value.partition("#")
        if name=="./":return f'{attr}="index.html'+('#'+fragment if sep else '')+'"'
        if name in FILES:
            name=FILES[name][0]
        elif name.startswith(("es/","ru/","pt-br/","de/","hi/","bn/","ja/","pa/","mr/","te/","ta/","tr/","vi/","ko/","fr/","it/")) or name in ("styles.css","favicon.svg","about.html","contact.html","privacy.html","n8n-queue-mode-hero.svg"):
            name="../"+name
        else:
            # assets not in Polish: refer to existing parent site assets
            if name and not name.startswith("../") and not name.startswith("pl/") and not name.endswith(".html"):
                name="../"+name
        return f'{attr}="{name}'+('#'+fragment if sep else '')+'"'
    s=re.sub(r'\b(href|src)="([^"]+)"',urlfix,s)
    # Preserve original language switch; add current Polish page to the options.
    match=re.search(r'(<div class="lang-menu">)([\s\S]*?)(</div>)',s)
    if not match:raise RuntimeError("Missing original language switch")
    menu=match.group(2)
    if not re.search(r'>Polski</a>',menu):
        menu+=f'<a href="{pl_path}" aria-current="page">Polski</a>'
    s=s[:match.start(2)]+menu+s[match.end(2):]
    s=re.sub(r'(<div class="lang-switch"><button\b[^>]*>)[\s\S]*?(</button>)',r'\1Polski ▾\2',s,count=1)
    # English root H1 translates automatically; replace with pre-approved wording while keeping original tags.
    h=re.search(r'<h1\b[^>]*>([\s\S]*?)</h1>',s)
    if h:
        # Keep inline <em>/<span> inside English H1; localize its text, not its markup.
        if "<" not in h.group(1):
            s=s[:h.start(1)]+h1+s[h.end(1):]
    # If original English figure had no clickable surface, preserve it unchanged (no invented CTA).
    # JSON-LD remains English source data for now and needs correct language/url fields.
    def jsonld(m):
        text=m.group(2)
        try:obj=json.loads(text)
        except (ValueError,TypeError):return m.group(0)
        def rec(x):
            if isinstance(x,list):return [rec(z) for z in x]
            if isinstance(x,dict):
                r={}
                for k,v in x.items():
                    if isinstance(v,str) and k in ("name","description","text","headline") and re.search("[A-Za-z]",v):
                        r[k]=translate_raw(v)
                    elif isinstance(v,str) and k in ("url","@id"):
                        r[k]=v.replace(ROOT+en_path,target)
                    elif isinstance(v,str) and k=="inLanguage":r[k]="pl"
                    else:r[k]=rec(v)
                return r
            return x
        obj=rec(obj)
        return m.group(1)+json.dumps(obj,ensure_ascii=False,separators=(",",":"))+m.group(3)
    s=re.sub(r'(<script\b[^>]*type="application/ld\+json"[^>]*>)([\s\S]*?)(</script>)',jsonld,s)
    # Polish alternate used only on Polish page; adding language link is necessary for localized page.
    alternate=f'<link rel="alternate" hreflang="pl" href="{target}"/>'
    if 'hreflang="pl"' not in s:s=s.replace("</head>",alternate+"</head>",1)
    return s
def tags(s):
    return [m.group(1).lower() for m in re.finditer(r'<(/?[a-zA-Z][a-zA-Z0-9:-]*)\b',s)]
def validate(en,pol,en_path,pl_path):
    a=tags(en);b=tags(pol)
    if a!=b[:len(a)]:
        # one new alternate link + one Polish language menu anchor causes exactly 2 extra links
        aa=Counter(a);bb=Counter(b)
        for tag in set(aa)|set(bb):
            expected=aa[tag]+(1 if tag=="link" else 1 if tag in ("a","/a") else 0)
            if bb[tag]!=expected:raise ValueError("DOM tag mismatch "+pl_path+" "+tag+f" {bb[tag]}!={expected}")
    if pol.count("<h1")!=1 or not re.search('lang="pl"',pol):raise ValueError("bad H1/lang")
    if len(pol)<len(en)*0.55:raise ValueError("localized HTML suspiciously short")
    if pol.count("<section")!=en.count("<section"):raise ValueError("missing section")
    if pol.count("<svg")!=en.count("<svg"):raise ValueError("missing SVG")
    if pol.count("<table")!=en.count("<table"):raise ValueError("missing table")
    if pol.count("<article")!=en.count("<article"):raise ValueError("missing card")
    if pol.count("<details")!=en.count("<details"):raise ValueError("missing FAQ")
    if pol.count("<script")!=en.count("<script"):raise ValueError("JS script count changed")
    if pol.count("<style")!=en.count("<style"):raise ValueError("CSS tag count changed")
    if 'https://www.vdsina.com/?partner=ni8gzrvz75' not in pol:raise ValueError("partner link missing")
    # No broken links to english root from within Polish directory.
    if 'href="styles.css"' in pol or 'src="n8n-queue-mode-hero.svg"' in pol:raise ValueError("relative asset broken")
    if pol.count('class="lang-switch"')!=en.count('class="lang-switch"'):raise ValueError("language switch missing")
    # No Polish visual template: entire English markup used.
    if 'class="pl-vis"' in pol:raise ValueError("wrong hero")
    return {"english":en_path,"polish":"pl/"+pl_path,"html_bytes":len(pol),"sections":pol.count("<section"),"svg":pol.count("<svg"),"cards":pol.count("<article"),"faq":pol.count("<details"),"tables":pol.count("<table")}
def main():
    checks=[]
    for en_path,(pl_path,title,h1) in FILES.items():
        source=Path(en_path).read_text(encoding="utf-8")
        print("Working on",en_path,flush=True)
        translated,count=modify_text(source)
        translated=translate_attributes(translated)
        translated=patch_urls_and_metadata(translated,en_path,pl_path,title,h1)
        checks.append(validate(source,translated,en_path,pl_path))
        (OUTDIR/pl_path).write_text(translated,encoding="utf-8")
        CACHE_FILE.parent.mkdir(exist_ok=True,parents=True)
        CACHE_FILE.write_text(json.dumps(CACHE,ensure_ascii=False),encoding="utf-8")
        print("  PASS",checks[-1],flush=True)
    Path(".github/pl_exact_translation_qa.json").write_text(json.dumps({"checks":checks,"translated_strings":len(CACHE)},ensure_ascii=False,indent=2),encoding="utf-8")
    print("ALL_8_PAGES_PASS",len(CACHE),flush=True)
if __name__=="__main__": main()
