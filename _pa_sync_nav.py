#!/usr/bin/env python3
"""Synchronize Punjabi site-wide footer/header language options and sitemap."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
BASE="https://agurkin2021-gif.github.io/vps-for-n8n/"
TOPICS=[
("best-vps-for-n8n.html",r"best-vps|bester-vps|mejor-vps|melhor-vps|luchshiy-vps|najlepszy-vps|meilleur-vps|miglior-vps|vps-n8n-tot-nhat"),
("n8n-backup-restore.html",r"backup|copias-seguridad|sauvegarde-restauration|rezervnoe|yedekleme|sao-luu|rezervnoe-kopirovanie"),
("install-n8n-vps-docker.html",r"install|instalar|installer|ustanovka|jak-zainstalowac|cai-n8n|docker-kurulumu"),
("n8n-cloud-vs-self-hosted.html",r"n8n-cloud"),
("n8n-vps-requirements.html",r"requirements|anforderungen|requisitos|trebovaniya|gereksinimleri|wymagania|configuration-vps|cau-hinh"),
("n8n-vps-security.html",r"security|secure-n8n|sicherheit|seguridad|seguranca|bezopasnost|securite|bao-mat|jak-zabezpieczyc|guvenlik|sicurezza"),
("n8n-queue-mode.html",r"queue-mode|modo-cola|modo-fila|rezhim-ocheredi|tryb-kolejkowy"),
("about.html",r"^(?:about|acerca-de|ueber-uns|o-proekte|sobre|o-nas)\.html$"),
("contact.html",r"^(?:contact|contacto|contato|kontakty|kontakt)\.html$"),
("privacy.html",r"^(?:privacy|privacidad|privacidade|datenschutz|politika-konfidencialnosti|polityka-prywatnosci)\.html$"),
("n8n-hosting-india.html",r"(?:n8n-hosting-india|managed-n8n-hosting-india|hosting-india)"),
]
PUNJABI=[
"index.html", "best-vps-for-n8n.html", "about.html", "n8n-backup-restore.html",
"contact.html", "install-n8n-vps-docker.html", "n8n-cloud-vs-self-hosted.html",
"n8n-vps-requirements.html","privacy.html","n8n-vps-security.html","n8n-queue-mode.html",
]
LANG_MENU=re.compile(r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)([\s\S]*?)(</div>)',re.I)
PA_ANCHOR=re.compile(r'<a\b[^>]*>\s*ਪੰਜਾਬੀ\s*</a>',re.I)
JA_ANCHOR=re.compile(r'<a\b[^>]*>\s*日本語\s*</a>',re.I)

def match_pa_page(path:str):
    if path in ("", "index.html") or path.endswith("/index.html"):
        return "index.html",True
    name=path.rsplit("/",1)[-1]
    for fn,pattern in TOPICS:
        if re.search(pattern,name,re.I) or (fn=="n8n-hosting-india.html" and re.search(pattern,path,re.I)):
            return fn,True
    return "index.html",False

def rewrite_anchor(tag:str,want:str):
    if re.search(r'\bhref=["\'][^"\']*["\']',tag,re.I):
        tag=re.sub(r'\bhref=["\'][^"\']*["\']','href="'+want+'"',tag,count=1)
    else:
        tag=tag.replace("<a","<a href=\""+want+"\"",1)
    tag=re.sub(r'\s+aria-current=["\']page["\']','',tag)
    return tag

def rewrite_menu(m,want):
    opening,inner,closing=m.groups()
    if PA_ANCHOR.search(inner):
        inner=PA_ANCHOR.sub(lambda z:rewrite_anchor(z.group(),want),inner)
    else:
        a='<a href="'+want+'" hreflang="pa" lang="pa">ਪੰਜਾਬੀ</a>'
        if JA_ANCHOR.search(inner):
            inner=JA_ANCHOR.sub(lambda z:z.group()+a,inner,count=1)
        else:
            inner=inner+a
    return opening+inner+closing

def process_file(f:Path):
    original=f.read_text(encoding="utf-8")
    # Obsolete noindex redirect stubs have no footer or user-facing language menu.
    if "noindex" in original.lower() and "refresh" in original.lower() and "http-equiv" in original.lower():return False,True
    if f.relative_to(ROOT).as_posix().startswith("pa/"):return False,True
    relative=f.relative_to(ROOT).as_posix()
    target,has_equivalent=match_pa_page(relative)
    want="/vps-for-n8n/pa/"+("" if target=="index.html" else target)
    processed=LANG_MENU.sub(lambda m:rewrite_menu(m,want),original)
    if not re.search(r'<footer\b[\s\S]*?<div\b[^>]*class=["\'][^"\']*footer-lang-switch',processed,re.I):
        # Existing pages are expected to have native footer dropdowns.
        return False,False
    # Make any pre-existing hreflang="pa" link match the footer's selection.
    if has_equivalent:
        processed=re.sub(r'<link\b[^>]*hreflang=["\']pa["\'][^>]*>',
            lambda m:re.sub(r'\bhref=["\'][^"\']*["\']','href="'+BASE+"pa/"+("" if target=="index.html" else target)+'"',m.group()),processed,flags=re.I)
        if not re.search(r'<link\b[^>]*hreflang=["\']pa["\']',processed,re.I):
            processed=processed.replace("</head>",'<link rel="alternate" hreflang="pa" href="'+BASE+"pa/"+("" if target=="index.html" else target)+'"/></head>',1)
    footer=processed[processed.find("<footer"):]
    if not PA_ANCHOR.search(footer):return False,False
    if processed!=original:
        f.write_text(processed,encoding="utf-8")
        return True,True
    return False,True

changed=0; checked=0;errors=[]
for f in sorted(ROOT.rglob("*.html")):
    if ".git" in f.parts:continue
    edited,valid=process_file(f)
    checked+=1;changed+=int(edited)
    if not valid:errors.append(str(f.relative_to(ROOT)))
print(f"LANGUAGE_SWITCH_QA checked={checked} changed={changed} missing_footer={len(errors)}",flush=True)
if errors:raise RuntimeError("Footer language missing in "+", ".join(errors[:20]))

sitemap=ROOT/"sitemap.xml"
text=sitemap.read_text(encoding="utf-8")
for p in ("pa/about.html","pa/contact.html","pa/privacy.html"):
    url=BASE+p
    if url not in text:text=text.replace("</urlset>","  <url><loc>"+url+"</loc></url>\n</urlset>",1)
sitemap.write_text(text,encoding="utf-8")
ET.parse(sitemap)
urls=re.findall(r"<loc>([^<]+)</loc>",text)
en=[p for p in urls if p.startswith(BASE) and not p.removeprefix(BASE).startswith(tuple(x+"/" for x in ["bn","pa","de","es","hi","ko","pa","pt-br","ru","mr","te","tr","ta","vi","fr","it","pl"])) and p.removeprefix(BASE) in ("","best-vps-for-n8n.html","about.html","n8n-backup-and-restore.html","contact.html","install-n8n-on-a-vps.html","n8n-cloud-vs-self-hosted.html","n8n-vps-requirements.html","privacy.html","secure-n8n-on-a-vps.html","n8n-queue-mode.html")]
ja=[p for p in urls if p.startswith(BASE+"pa/")]
expected=[BASE+"pa/"+("" if x=="index.html" else x) for x in PUNJABI]
if len(en)!=11 or any(x not in ja for x in expected):
    raise RuntimeError(f"Sitemap mismatch: en={len(en)}, ja={len(ja)}, missing={[x for x in expected if x not in ja]}")
if len(set(urls))!=len(urls):raise RuntimeError("Sitemap duplicate URLs")
print(f"SITEMAP_QA english={len(en)} matching_pa={len(expected)} pa_total={len(ja)} extra_region={len(ja)-len(expected)} duplicates=0",flush=True)
