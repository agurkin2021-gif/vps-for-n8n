#!/usr/bin/env python3
"""Greek editorial pass using the reviewed SEO heading dictionary and technical glossary.
Every translated page is regenerated from its authoritative English source, then
checked for HTML/CSS/JS/price/number parity before publication.
"""
from __future__ import annotations
import json
import pathlib
import re
import subprocess
import sys
import time
import _el_translate_full as T

ROOT = pathlib.Path(__file__).resolve().parent
HEADINGS = json.loads((ROOT / ".github" / "el-editorial-headings.json").read_text(encoding="utf-8"))
T.EXACT.update(HEADINGS)
T.LANGUAGE_NAMES.update({"Azərbaycanca","Ελληνικά"})

def polish_sentence(english: str, greek: str) -> str:
    """Use the English source to disambiguate n8n technical terms in Greek."""
    out=greek
    # Greek usage treats VPS and n8n as neuter technical nouns.
    if re.search(r'\bVPS\b', english, re.I):
        for a,b in (
            ("Μια VPS","Ένα VPS"),("Μία VPS","Ένα VPS"),
            ("μια VPS","ένα VPS"),("μία VPS","ένα VPS"),
            ("η VPS","το VPS"),("Η VPS","Το VPS"),
            ("της VPS","του VPS"),("Της VPS","Του VPS"),
            ("την VPS","το VPS"),("Την VPS","Το VPS"),
            ("στην VPS","στο VPS"),("Στην VPS","Στο VPS"),
            ("στη VPS","στο VPS"),("οι VPS","τα VPS"),
            ("Οι VPS","Τα VPS"),("στη δική σας VPS","στο δικό σας VPS"),
            ("η δική σας VPS","το δικό σας VPS"),
            ("την δική σας VPS","το δικό σας VPS"),
            ("μια n8n VPS","ένα VPS για n8n"),
        ):
            out=out.replace(a,b)
    if "n8n" in english:
        for a,b in (
            ("την n8n","το n8n"),("της n8n","του n8n"),
            ("η n8n","το n8n"),("Η n8n","Το n8n"),
            ("στην n8n","στο n8n"),("με την n8n","με το n8n"),
            ("για την n8n","για το n8n"),("της εφαρμογής n8n","της εφαρμογής n8n"),
            ("n8n Το Cloud","Το n8n Cloud"),("n8n Σύννεφο","n8n Cloud"),
        ):
            out=out.replace(a,b)
    if re.search(r'\bworkers?\b',english,re.I):
        for form in ("εργαζόμενους","εργαζόμενοι","εργαζομένους","εργαζομένων","εργαζόμενος",
                     "εργαζόμενο","εργαζόμενα","εργαζόμενη","εργαζόμενες",
                     "Εργαζόμενους","Εργαζόμενοι","Εργαζομένων",
                     "εργάτες","εργάτης","εργάτη","εργατών","εργαζόμενων"):
            out=out.replace(form,"workers")
        out=out.replace("Εργάτες","Workers").replace("Εργάτης","Worker")
    if re.search(r'\binstances?\b',english,re.I) and not re.search(r'\bexamples?\b',english,re.I):
        for a,b in (
            ("Ένα μόνο παράδειγμα n8n","Μία μόνο εγκατάσταση n8n"),
            ("ένα μόνο παράδειγμα n8n","μία μόνο εγκατάσταση n8n"),
            ("ένα λιτό παράδειγμα n8n","μια λιτή εγκατάσταση n8n"),
            ("ένα παράδειγμα n8n","μια εγκατάσταση n8n"),
            ("το παράδειγμα n8n","την εγκατάσταση n8n"),
            ("παραδείγματος n8n","εγκατάστασης n8n"),
            ("παραδείγματα n8n","εγκαταστάσεις n8n"),
            ("παράδειγμα n8n","εγκατάσταση n8n"),
            ("παράδειγμα της n8n","εγκατάσταση του n8n"),
            ("παραδείγματα","εγκαταστάσεις"),
        ):
            out=out.replace(a,b)
    if re.search(r'\b(?:traffic|bandwidth)\b',english,re.I):
        out=out.replace("κυκλοφορία δεδομένων","κίνηση δεδομένων").replace("κυκλοφορία","κίνηση δεδομένων")
        out=out.replace("Κυκλοφορία","Κίνηση δεδομένων")
    if re.search(r'\b(?:plan|tier|plans)\b',english,re.I):
        out=out.replace("σχέδιο Standard","πακέτο Standard").replace("σχεδίου Standard","πακέτου Standard")
        out=out.replace("ένα σχέδιο VPS","ένα πακέτο VPS")
    out=out.replace("Περισσότερα RAM","Περισσότερη RAM").replace("περισσότερα RAM","περισσότερη RAM")
    out=out.replace("το λίστα ελέγχου","τη λίστα ελέγχου")
    out=out.replace("σε μια Linux VPS","σε ένα Linux VPS")
    out=out.replace("για 30 ημέρα","για 30 ημέρες").replace("30-ημέρα","30 ημερών")
    out=out.replace("6 Οκτώβριος 2026","6 Οκτωβρίου 2026")
    out=out.replace("μία VPS","ένα VPS").replace("ένα n8n VPS","ένα VPS για n8n")
    return out

def main():
    old_items=len(T.cache)
    updated=0
    for english,greek in list(T.cache.items()):
        refined=polish_sentence(english,greek)
        if refined!=greek:
            T.cache[english]=refined
            updated+=1
    # Manual headings win over any cached translation and are the exact source meaning.
    T.CACHE_PATH.write_text(json.dumps(T.cache,ensure_ascii=False,indent=1)+"\n",encoding="utf-8")
    print(f"GREEK_EDITORIAL_GLOSSARY cached={old_items} improved={updated} headings={len(HEADINGS)}",flush=True)
    assert T.verify_source_sitemap()==len(T.PAGES)==11
    for i,(en,target) in enumerate(T.PAGES,1):
        print(f"GREEK_EDITORIAL_PAGE {i}/11 OPEN {en}",flush=True)
        T.process(en,target)
        source=(ROOT/en).read_text(encoding="utf-8")
        result=(ROOT/target).read_text(encoding="utf-8")
        T.validate(source,result,en,target)
        print(f"GREEK_EDITORIAL_PAGE {i}/11 VERIFIED {target}",flush=True)
    from _el_publish_qa import main as sitewide_qa
    sitewide_qa()
    # Stable second pass catches missing footer entries and duplicate sitemap records.
    sitewide_qa()
    print("GREEK_EDITORIAL_FINAL_QA_PASS",flush=True)

if __name__=="__main__":
    main()
