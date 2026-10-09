#!/usr/bin/env python3
"""Finalize Marathi localization on existing HTML pages without altering content or code."""
from __future__ import annotations
from pathlib import Path
import re, html, json, collections
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent
BASE="https://agurkin2021-gif.github.io/vps-for-n8n/"
PAIRS=[
 ("index.html","mr/index.html"),
 ("best-vps-for-n8n.html","mr/best-vps-for-n8n.html"),
 ("about.html","mr/about.html"),
 ("n8n-backup-and-restore.html","mr/n8n-backup-restore.html"),
 ("contact.html","mr/contact.html"),
 ("install-n8n-on-a-vps.html","mr/install-n8n-vps-docker.html"),
 ("n8n-cloud-vs-self-hosted.html","mr/n8n-cloud-vs-self-hosted.html"),
 ("n8n-vps-requirements.html","mr/n8n-vps-requirements.html"),
 ("privacy.html","mr/privacy.html"),
 ("secure-n8n-on-a-vps.html","mr/n8n-vps-security.html"),
 ("n8n-queue-mode.html","mr/n8n-queue-mode.html")
]
LANGS=[
 ("en","English",""),("es","Español","es"),("ru","Русский","ru"),
 ("pt-BR","Português","pt-br"),("de","Deutsch","de"),
 ("hi","हिन्दी","hi"),("bn","বাংলা","bn"),("ja","日本語","ja"),
 ("pa","मराठी","pa"),("mr","मराठी","mr"),("te","తెలుగు","te"),
 ("ta","தமிழ்","ta"),("tr","Türkçe","tr"),("vi","Tiếng Việt","vi"),
 ("ko","한국어","ko"),("fr","Français","fr"),("it","Italiano","it"),
 ("pl","Polski","pl")
]
LABEL_TO_LANG={label:code for code,label,_ in LANGS}
PREFIXES={prefix:code for code,_,prefix in LANGS if prefix}
MENU=re.compile(r'(<div\b[^>]*class=["\'][^"\']*\blang-menu\b[^"\']*["\'][^>]*>)([\s\S]*?)(</div>)',re.I)
ANCHOR=re.compile(r'(<a\b[^>]*>)([^<>]*)(</a>)',re.I)
LINK=re.compile(r'<link\b[^>]*>',re.I)
MR_TITLE="मराठी"

def category(path):
    name=path.rsplit("/",1)[-1].lower()
    if name=="index.html":return "home"
    if re.search(r"^(?:about|acerca-de|ueber-uns|o-projekte?|o-proekte|sobre|o-nas)\.html$",name):return "about"
    if re.search(r"^(?:contact|contacto|contato|kontakty|kontakt)\.html$",name):return "contact"
    if re.search(r"^(?:privacy|privacidad|privacidade|datenschutz|politika-konfidencialnosti|polityka-prywatnosci)\.html$",name):return "privacy"
    if re.search(r"(?:best-vps|bester-vps|mejor-vps|melhor-vps|luchshiy-vps|najlepszy-vps|meilleur-vps|miglior-vps|vps-n8n-tot-nhat)",name):return "best"
    if re.search(r"(?:backup|copias-seguridad|sauvegarde-restauration|rezervnoe|yedekleme|sao-luu|wiederherstellung)",name):return "backup"
    if re.search(r"(?:install|instalar|installer|ustanovka|jak-zainstalowac|cai-n8n|docker-kurulumu)",name):return "install"
    if "n8n-cloud" in name:return "cloud"
    if re.search(r"(?:requirements|anforderungen|requisitos|trebovaniya|gereksinimleri|wymagania|configuration-vps|cau-hinh)",name):return "requirements"
    if re.search(r"(?:security|secure-n8n|sicherheit|seguridad|seguranca|bezopasnost|securite|bao-mat|jak-zabezpieczyc|guvenlik|sicurezza)",name):return "security"
    if re.search(r"(?:queue-mode|modo-cola|modo-fila|rezhim-ocheredi|tryb-kolejkowy)",name):return "queue"
    if "managed-n8n-hosting-india" in name:return "managed-india"
    if "n8n-hosting-india" in name:return "hosting-india"
    return None

def locale(path):
    prefix=path.partition("/")[0]
    return PREFIXES.get(prefix,"en")

def canonical(path):
    if path=="index.html":return BASE
    if path.endswith("/index.html"):return BASE+path[:-10]
    return BASE+path

def set_href(tag,url):
    if re.search(r'\bhref=["\'][^"\']*["\']',tag,re.I):
        return re.sub(r'\bhref=(["\']).*?\1',lambda m:"href="+m.group(1)+url+m.group(1),tag,count=1,flags=re.I)
    return tag.replace("<a",'<a href="'+url+'"',1)

def build_registry():
    pages=sorted(f.relative_to(ROOT).as_posix() for f in ROOT.rglob("*.html")
                 if ".git" not in f.parts and f.name!="404.html")
    reg={}
    for path in pages:
        tp=category(path)
        if tp is None:continue
        key=(locale(path),tp)
        if key not in reg:reg[key]=path
    for en,pa in PAIRS:
        tp=category(en)
        reg[("en",tp)]=en
        reg[("mr",tp)]=pa
    return pages,reg

PAGES,REG=build_registry()
def dest(code,tp):
    path=REG.get((code,tp)) or REG.get((code,"home"))
    return canonical(path) if path else BASE

def do_menu(match,path):
    opening,inner,closing=match.groups()
    current=locale(path)
    tp=category(path)
    labels_found=[]
    def rewrite(m):
        tag,label,close=m.groups()
        name=html.unescape(label).strip()
        code=LABEL_TO_LANG.get(name)
        if code is None:return m.group()
        labels_found.append(name)
        tag=set_href(tag,dest(code,tp))
        tag=re.sub(r'\s+aria-current=(["\'])page\1','',tag,flags=re.I)
        if code=="mr" and not re.search(r'\blang=',tag):
            tag=tag[:-1]+' lang="pa">'
        if code==current and dest(code,tp)==canonical(path):
            tag=tag[:-1]+' aria-current="page">'
        return tag+label+close
    inner=ANCHOR.sub(rewrite,inner)
    if MR_TITLE not in labels_found:
        new='<a href="'+dest("mr",tp)+'" hreflang="mr" lang="mr">'+MR_TITLE+'</a>'
        ja=re.search(r'<a\b[^>]*>\s*ਪੰਜਾਬੀ\s*</a>',inner)
        if ja:
            inner=inner[:ja.end()]+new+inner[ja.end():]
        else:
            inner+=new
    if labels_found.count(MR_TITLE)>1:
        seen=[False]
        def once(m):
            if html.unescape(m.group(2)).strip()!=MR_TITLE:return m.group()
            if seen[0]:return ""
            seen[0]=True
            return m.group()
        inner=ANCHOR.sub(once,inner)
    return opening+inner+closing

def do_link(m,path):
    tag=m.group()
    hit=re.search(r'\bhreflang=(["\'])([^"\']+)\1',tag,re.I)
    if not hit:return tag
    code=hit.group(2).lower()
    tp=category(path)
    if code=="ja":
        href=re.search(r'\bhref=(["\'])(.*?)\1',tag,re.I)
        if href and ("/pa/" in href.group(2) or href.group(2).endswith("/pa")):
            # Recover the Japanese URL overwritten by the previous footer synchronizer.
            tag=set_href(tag,dest("ja",tp))
    elif code=="pa":
        if (("pa",tp) in REG):
            tag=set_href(tag,dest("pa",tp))
        elif locale(path)=="pa":
            tag=set_href(tag,canonical(path))
        else:
            return ""
    elif code=="mr":
        if (("mr",tp) in REG):
            tag=set_href(tag,dest("mr",tp))
        elif locale(path)=="mr":
            tag=set_href(tag,canonical(path))
        else:
            return ""
    elif code in ("en","x-default") and path in ("pa/index.html","mr/index.html"):
        tag=set_href(tag,BASE)
    return tag

def transform(path,source):
    if path=="404.html":return source
    if "footer-lang-switch" not in source:
        return source
    out=source
    if path.startswith("mr/") and ("mr/"+path.split("/",1)[1] in [b for _,b in PAIRS]):
        out=re.sub(r'(<html\b[^>]*\blang=["\'])(?:ja|en)(["\'])',r'\1mr\2',out,count=1,flags=re.I)
    out=MENU.sub(lambda m:do_menu(m,path),out)
    out=LINK.sub(lambda m:do_link(m,path),out)
    if ("mr",category(path)) in REG and not re.search(r'<link\b[^>]*hreflang=["\']mr["\']',out,re.I):
        out=out.replace("</head>",'<link rel="alternate" hreflang="mr" href="'+dest("mr",category(path))+'"/></head>',1)
    return out

def sig(source):
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

def ensure_sitemap():
    p=ROOT/"sitemap.xml"
    source=p.read_text(encoding="utf-8")
    existing=set(re.findall(r"<loc>([^<]+)</loc>",source))
    count=0
    for _,translated in PAIRS:
        link=canonical(translated)
        if link not in existing:
            source=source.replace("</urlset>",'  <url><loc>'+link+'</loc></url>\n</urlset>',1)
            existing.add(link)
            count+=1
    p.write_text(source,encoding="utf-8")
    ET.parse(p)
    print("MARATHI_SITEMAP_ADDED",count,flush=True)

def audit(changed):
    errors=[]
    for index,(en,pa) in enumerate(PAIRS,1):
        source=(ROOT/en).read_text(encoding="utf-8")
        output=(ROOT/pa).read_text(encoding="utf-8")
        if sig(source)!=sig(output):errors.append(pa+": HTML structure differs")
        if styles(source)!=styles(output):errors.append(pa+": inline CSS differs")
        if scripts(source)!=scripts(output):errors.append(pa+": JavaScript differs")
        if prices(source)!=prices(output):errors.append(pa+": prices differ")
        if not re.search(r'<html\b[^>]*\blang=["\']mr["\']',output,re.I):errors.append(pa+": html lang is not mr")
        if len(re.findall(r'<h1(?:\s|>)',output,re.I))!=1:errors.append(pa+": H1 count")
        if canonical(pa) not in output:errors.append(pa+": missing self-canonical")
        if re.search(r'<meta\b[^>]*name=["\']robots["\'][^>]*noindex',output,re.I):errors.append(pa+": noindex")
        if "<!--JSONLD_" in output:errors.append(pa+": JSON-LD placeholder")
        if len(re.findall(r'[\u0900-\u097f]',visible(output)))<5:errors.append(pa+": Marathi missing")
        for attr in ("alt","aria-label","placeholder","aria-valuetext"):
            if len(re.findall(r'\b'+attr+r'=["\']',source,re.I))!=len(re.findall(r'\b'+attr+r'=["\']',output,re.I)):
                errors.append(pa+": missing "+attr)
        for text in re.findall(r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',output,re.S|re.I):
            try:json.loads(text)
            except Exception as exc:errors.append(pa+": invalid JSON-LD "+str(exc))
        print("MARATHI_PAGE_QA "+str(index)+"/11 "+pa+(" PASS" if not errors else " checked"),flush=True)
    valid=0;total=0
    for path in PAGES:
        text=(ROOT/path).read_text(encoding="utf-8")
        if "footer-lang-switch" not in text:continue
        total+=1
        ft=text[text.find("<footer"):]
        ft_menu=MENU.search(ft)
        if not ft_menu or MR_TITLE not in ft_menu.group(2):
            errors.append(path+": Marathi absent in footer")
        for block in MENU.finditer(text):
            if MR_TITLE not in block.group(2):errors.append(path+": Marathi absent in selector")
            for m in ANCHOR.finditer(block.group(2)):
                label=html.unescape(m.group(2)).strip()
                code=LABEL_TO_LANG.get(label)
                if not code:continue
                href=re.search(r'\bhref=(["\'])(.*?)\1',m.group(1),re.I)
                expected=dest(code,category(path))
                if not href or href.group(2)!=expected:
                    errors.append(path+": incorrect "+label+" menu link")
            valid+=1
        if re.search(r'<link\b[^>]*hreflang=["\']ja["\'][^>]*href=["\'][^"\']*/pa/',text,re.I):
            errors.append(path+": ja points to Marathi")
        if re.search(r'<link\b[^>]*href=["\'][^"\']*/pa/[^"\']*["\'][^>]*hreflang=["\']ja["\']',text,re.I):
            errors.append(path+": ja points to Marathi")
    sm=ET.parse(ROOT/"sitemap.xml")
    urls=[x.text for x in sm.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
    en_expected={canonical(en) for en,_ in PAIRS}
    mr_expected={canonical(pa) for _,pa in PAIRS}
    if not en_expected.issubset(set(urls)):errors.append("Sitemap missing an English original")
    if not mr_expected.issubset(set(urls)):errors.append("Sitemap missing a Marathi equivalent")
    if len(en_expected)!=len(mr_expected):errors.append("Sitemap page counts differ")
    if len(set(urls))!=len(urls):errors.append("Sitemap duplicate URL")
    expected_en={"index.html","best-vps-for-n8n.html","about.html","n8n-backup-and-restore.html",
        "contact.html","install-n8n-on-a-vps.html","n8n-cloud-vs-self-hosted.html",
        "n8n-vps-requirements.html","privacy.html","secure-n8n-on-a-vps.html","n8n-queue-mode.html"}
    actual_en={"" if p==BASE else p.removeprefix(BASE) for p in urls if p==BASE or (
        p.startswith(BASE) and "/" not in p.removeprefix(BASE) and p.endswith(".html"))}
    if actual_en!={("" if p=="index.html" else p) for p in expected_en}:errors.append("English sitemap no longer has exactly the 11 translation originals")
    print("MARATHI_QA english="+str(len(en_expected))+" translated="+str(len(pa_expected))
          +" footer_pages="+str(total)+" menus="+str(valid)+" changed="+str(changed)
          +" issues="+str(len(errors)),flush=True)
    if errors:raise AssertionError("\n".join(errors[:75]))

def main():
    changed=0
    for path in PAGES:
        f=ROOT/path
        s=f.read_text(encoding="utf-8")
        out=transform(path,s)
        if out!=s:
            f.write_text(out,encoding="utf-8")
            changed+=1
    ensure_sitemap()
    audit(changed)

if __name__=="__main__":main()
