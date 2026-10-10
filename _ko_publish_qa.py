#!/usr/bin/env python3
"""Integrate complete Korean localization site-wide and run strict QA."""
from __future__ import annotations
from pathlib import Path
import re, html, json, collections
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
BASE="https://agurkin2021-gif.github.io/vps-for-n8n/"
PAIRS=[
 ("index.html","ko/index.html"),
 ("best-vps-for-n8n.html","ko/best-vps-for-n8n.html"),
 ("about.html","ko/about.html"),
 ("n8n-backup-and-restore.html","ko/n8n-backup-restore.html"),
 ("contact.html","ko/contact.html"),
 ("install-n8n-on-a-vps.html","ko/install-n8n-vps-docker.html"),
 ("n8n-cloud-vs-self-hosted.html","ko/n8n-cloud-vs-self-hosted.html"),
 ("n8n-vps-requirements.html","ko/n8n-vps-requirements.html"),
 ("privacy.html","ko/privacy.html"),
 ("secure-n8n-on-a-vps.html","ko/n8n-vps-security.html"),
 ("n8n-queue-mode.html","ko/n8n-queue-mode.html")
]
KO_EXTRA={}
KO_TITLE="한국어"
MENU=re.compile(r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)([\s\S]*?)(</div>)',re.I)
ANCHOR=re.compile(r'(<a\b[^>]*>)([^<>]*)(</a>)',re.I)
LINK=re.compile(r'<link\b[^>]*>',re.I)

def category(path):
    name=path.rsplit("/",1)[-1].lower()
    if name=="index.html":return "home"
    if re.search(r"^(?:about|acerca-de|ueber-uns|o-projekte?|o-proekte|sobre|o-nas|hakkimizda)\.html$",name):return "about"
    if re.search(r"^(?:contact|contacto|contato|kontakty|kontakt|iletisim)\.html$",name):return "contact"
    if re.search(r"^(?:privacy|privacidad|privacidade|datenschutz|politika-konfidencialnosti|polityka-prywatnosci|gizlilik)\.html$",name):return "privacy"
    if re.search(r"(?:best-vps|bester-vps|mejor-vps|melhor-vps|luchshiy-vps|najlepszy-vps|meilleur-vps|miglior-vps|vps-n8n-tot-nhat)",name):return "best"
    if re.search(r"(?:backup|copias-seguridad|sauvegarde-restauration|rezervnoe|yedekleme|sao-luu|wiederherstellung)",name):return "backup"
    if re.search(r"(?:install|instalar|installer|ustanovka|jak-zainstalowac|cai-n8n|docker-kurulumu)",name):return "install"
    if "n8n-cloud" in name:return "cloud"
    if re.search(r"(?:requirements|anforderungen|requisitos|trebovaniya|gereksinimleri|wymagania|configuration-vps|cau-hinh)",name):return "requirements"
    if re.search(r"(?:security|secure-n8n|sicherheit|seguridad|seguranca|bezopasnost|securite|bao-mat|jak-zabezpieczyc|guvenlik|sicurezza)",name):return "security"
    if re.search(r"(?:queue-mode|modo-cola|modo-fila|rezhim-ocheredi|tryb-kolejkowy)",name):return "queue"
    if re.search(r"(?:managed-n8n-hosting|hebergement-n8n-manage)",name):return "managed-local"
    if re.search(r"(?:n8n-hosting-(?:india|turkiye|bangladesh|japan|deutschland)|n8n-hospedagem-brasil|hosting-n8n-viet-nam|hebergement-n8n-france)",name):return "hosting-local"
    return None

def locale(path):
    return path.partition("/")[0] if "/" in path else "en"

def canonical(path):
    if path=="index.html":return BASE
    if path.endswith("/index.html"):return BASE+path[:-10]
    return BASE+path

KO_BY_CATEGORY={category(en):vi for en,vi in PAIRS}
KO_BY_CATEGORY.update(KO_EXTRA)
EN_BY_CATEGORY={category(en):en for en,_ in PAIRS}

def ko_dest(path):
    tp=category(path)
    if locale(path)=="ko" and tp is None:return canonical(path)
    target=KO_BY_CATEGORY.get(tp,KO_BY_CATEGORY["home"])
    return canonical(target)

def set_href(tag,url):
    if re.search(r'\bhref=["\'][^"\']*["\']',tag,re.I):
        return re.sub(r'\bhref=(["\']).*?\1',lambda m:"href="+m.group(1)+url+m.group(1),tag,count=1,flags=re.I)
    return tag.replace("<a",'<a href="'+url+'"',1)

def normalize_ko_anchor(tag,current,url):
    tag=set_href(tag,url)
    tag=re.sub(r'\s+aria-current=(["\'])page\1','',tag,flags=re.I)
    if not re.search(r'\blang=',tag,re.I):tag=tag[:-1]+' lang="ko">'
    if not re.search(r'\bhreflang=',tag,re.I):tag=tag[:-1]+' hreflang="ko">'
    if current:tag=tag[:-1]+' aria-current="page">'
    return tag

def do_menu(match,path):
    opening,inner,closing=match.groups()
    current=(locale(path)=="ko")
    target=ko_dest(path)
    found=0
    def rewrite(m):
        nonlocal found
        tag,label,close=m.groups()
        if html.unescape(label).strip()!=KO_TITLE:return m.group()
        found+=1
        if found>1:return ""
        return normalize_ko_anchor(tag,current,target)+label+close
    inner=ANCHOR.sub(rewrite,inner)
    if found==0:
        new='<a href="'+target+'" hreflang="ko" lang="ko"'+(' aria-current="page"' if current else '')+'>'+KO_TITLE+'</a>'
        tr=list(re.finditer(r'<a\b[^>]*>\s*Tiếng Việt\s*</a>',inner,re.I))
        if tr:
            m=tr[-1];inner=inner[:m.end()]+new+inner[m.end():]
        else:inner+=new
    return opening+inner+closing

def do_link(match,path):
    tag=match.group()
    hit=re.search(r'\bhreflang=(["\'])([^"\']+)\1',tag,re.I)
    if not hit:return tag
    code=hit.group(2).lower()
    if code=="ko":tag=set_href(tag,ko_dest(path))
    elif code in ("en","x-default") and locale(path)=="ko" and category(path) in EN_BY_CATEGORY:
        tag=set_href(tag,canonical(EN_BY_CATEGORY[category(path)]))
    return tag

def set_korean_button(text,path):
    if locale(path)!="ko":return text
    return re.sub(
      r'(<div\b[^>]*class=["\'][^"\']*\blang-switch\b[^"\']*["\'][^>]*>\s*<button\b[^>]*>)[^<]*(</button>)',
      lambda m:m.group(1)+"한국어 ▾"+m.group(2),text,flags=re.I)

def transform(path,source):
    if path=="404.html":return source
    out=source
    if "footer-lang-switch" in out:
        out=set_korean_button(out,path)
        out=MENU.sub(lambda m:do_menu(m,path),out)
    out=LINK.sub(lambda m:do_link(m,path),out)
    if category(path) in KO_BY_CATEGORY and not re.search(r'<link\b[^>]*hreflang=["\']ko["\']',out,re.I):
        out=out.replace("</head>",'<link rel="alternate" hreflang="ko" href="'+ko_dest(path)+'"/></head>',1)
    return out

def signature(source):
    return [("/" if m.group()[1:2]=="/" else "")+m.group(1).lower()
            for m in re.finditer(r'</?([a-z][\w-]*)\b[^>]*>',source,re.I)
            if m.group(1).lower() not in ("link","meta")]
def scripts(source):
    return [m.group(1) for m in re.finditer(r'<script\b(?![^>]*application/ld\+json)[^>]*>([\s\S]*?)</script>',source,re.I)]
def styles(source):
    return [m.group(1) for m in re.finditer(r'<style\b[^>]*>([\s\S]*?)</style>',source,re.I)]
def visible(source):
    source=re.sub(r'<(?:script|style)\b[^>]*>[\s\S]*?</(?:script|style)>',"",source,flags=re.I)
    return html.unescape(re.sub(r'<[^>]*>'," ",source))
def prices(source):
    return collections.Counter(re.findall(r'\$\s*\d+(?:[.,]\d+)*(?:/(?:day|month|year|mo))?',visible(source),re.I))
def korean_chars(source):
    return len(re.findall(r'[가-힣]',source))

def alternate(text,lang):
    for tag in LINK.findall(text):
        code=re.search(r'\bhreflang=(["\'])([^"\']+)\1',tag,re.I)
        if code and code.group(2).lower()==lang.lower():
            href=re.search(r'\bhref=(["\'])([^"\']+)\1',tag,re.I)
            if href:return href.group(2)
    return None

def ensure_sitemap():
    p=ROOT/"sitemap.xml"
    source=p.read_text(encoding="utf-8")
    existing=set(re.findall(r"<loc>([^<]+)</loc>",source));count=0
    for _,translated in PAIRS:
        url=canonical(translated)
        if url not in existing:
            source=source.replace("</urlset>",'  <url><loc>'+url+'</loc></url>\n</urlset>',1)
            existing.add(url);count+=1
    p.write_text(source,encoding="utf-8");ET.parse(p)
    print("KOREAN_SITEMAP_ADDED",count,flush=True)

def audit(changed):
    errors=[]
    for index,(en,vi) in enumerate(PAIRS,1):
        source=(ROOT/en).read_text(encoding="utf-8")
        output=(ROOT/vi).read_text(encoding="utf-8")
        if signature(source)!=signature(output):errors.append(vi+": HTML structure differs")
        if styles(source)!=styles(output):errors.append(vi+": inline CSS differs")
        if scripts(source)!=scripts(output):errors.append(vi+": JavaScript differs")
        if prices(source)!=prices(output):errors.append(vi+": prices differ")
        if len(re.findall(r'<details\b',source,re.I))!=len(re.findall(r'<details\b',output,re.I)):errors.append(vi+": FAQ count differs")
        if len(re.findall(r'<img\b',source,re.I))!=len(re.findall(r'<img\b',output,re.I)):errors.append(vi+": image count differs")
        if not re.search(r'<html\b[^>]*\blang=["\']ko["\']',output,re.I):errors.append(vi+": html lang is not ko")
        if len(re.findall(r'<h1(?:\s|>)',source,re.I))!=len(re.findall(r'<h1(?:\s|>)',output,re.I)):errors.append(vi+": H1 count differs")
        if canonical(vi) not in output:errors.append(vi+": self canonical missing")
        if re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*noindex',output,re.I):errors.append(vi+": noindex")
        if "<!--JSONLD_" in output:errors.append(vi+": unresolved JSON-LD placeholder")
        if korean_chars(visible(output))<5:errors.append(vi+": Korean text missing")
        for attr in ("alt","aria-label","placeholder","aria-valuetext"):
            if len(re.findall(r'\b'+attr+r'=["\']',source,re.I))!=len(re.findall(r'\b'+attr+r'=["\']',output,re.I)):
                errors.append(vi+": missing "+attr)
        for block in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',output,re.S|re.I):
            try:json.loads(block)
            except Exception as exc:errors.append(vi+": invalid JSON-LD "+str(exc))
        if alternate(source,"ko")!=canonical(vi):errors.append(en+": reciprocal Korean hreflang wrong")
        if alternate(output,"en")!=canonical(en):errors.append(vi+": English hreflang wrong")
        print("KOREAN_PAGE_QA "+str(index)+"/11 "+vi+(" PASS" if not errors else " checked"),flush=True)

    pages=sorted(f.relative_to(ROOT).as_posix() for f in ROOT.rglob("*.html") if ".git" not in f.parts and f.name!="404.html")
    total=menus=0
    for path in pages:
        text=(ROOT/path).read_text(encoding="utf-8")
        if "footer-lang-switch" not in text:continue
        total+=1
        footer=text[text.find("<footer"):]
        fm=MENU.search(footer)
        if not fm or KO_TITLE not in fm.group(2):errors.append(path+": Korean absent in footer")
        expected=ko_dest(path)
        for block in MENU.finditer(text):
            menus+=1
            anchors=[m for m in ANCHOR.finditer(block.group(2)) if html.unescape(m.group(2)).strip()==KO_TITLE]
            if len(anchors)!=1:
                errors.append(path+": Korean selector count "+str(len(anchors)));continue
            href=re.search(r'\bhref=(["\'])(.*?)\1',anchors[0].group(1),re.I)
            if not href or href.group(2)!=expected:errors.append(path+": incorrect Korean menu link")
        if locale(path)=="ko" and "한국어 ▾" not in text:errors.append(path+": Korean button label missing")

    sm=ET.parse(ROOT/"sitemap.xml")
    urls=[x.text for x in sm.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    en_expected={canonical(en) for en,_ in PAIRS}
    ko_expected={canonical(vi) for _,vi in PAIRS}
    if not en_expected.issubset(set(urls)):errors.append("Sitemap missing English original")
    if not ko_expected.issubset(set(urls)):errors.append("Sitemap missing Korean equivalent")
    if len(en_expected)!=len(ko_expected) or len(ko_expected)!=11:errors.append("English/Korean page-count mismatch")
    ko_urls=[u for u in urls if u.startswith(BASE+"ko/")]
    if len(ko_urls)!=11:errors.append("Korean sitemap expected 11 URLs, got "+str(len(ko_urls)))
    if len(set(urls))!=len(urls):errors.append("Sitemap duplicate URL")

    expected_en={"index.html","best-vps-for-n8n.html","about.html","n8n-backup-and-restore.html","contact.html",
      "install-n8n-on-a-vps.html","n8n-cloud-vs-self-hosted.html","n8n-vps-requirements.html","privacy.html",
      "secure-n8n-on-a-vps.html","n8n-queue-mode.html"}
    actual_en={"" if u==BASE else u.removeprefix(BASE) for u in urls if u==BASE or
      (u.startswith(BASE) and "/" not in u.removeprefix(BASE) and u.endswith(".html"))}
    if actual_en!={("" if p=="index.html" else p) for p in expected_en}:errors.append("English sitemap no longer has exactly 11 originals")

    print("KOREAN_QA english=11 translated=11 ko_sitemap="+str(len(ko_urls))+
          " footer_pages="+str(total)+" menus="+str(menus)+" changed="+str(changed)+
          " issues="+str(len(errors)),flush=True)
    if errors:raise AssertionError("\n".join(errors[:100]))

def main():
    changed=0
    pages=sorted(f.relative_to(ROOT).as_posix() for f in ROOT.rglob("*.html") if ".git" not in f.parts and f.name!="404.html")
    for path in pages:
        p=ROOT/path;src=p.read_text(encoding="utf-8");out=transform(path,src)
        if out!=src:p.write_text(out,encoding="utf-8");changed+=1
    ensure_sitemap();audit(changed)

if __name__=="__main__":main()
