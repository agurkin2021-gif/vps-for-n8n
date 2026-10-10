#!/usr/bin/env python3
"""Conservative Thai editorial polish; preserves HTML structure and technical values."""
from pathlib import Path
import sys,re
from _th_translate_full import PAGES,ROOT,validate

GLOBAL=[
 ("คนงาน","worker"),
 ("ผู้ปฏิบัติงาน","worker"),
 ("พร็อกซีย้อนกลับ","reverse proxy"),
 ("พร็อกซีแบบย้อนกลับ","reverse proxy"),
 ("เว็บฮุค","webhook"),
 ("จุดสิ้นสุด","endpoint"),
 ("สแตก","stack"),
 ("คิวโหมด","Queue Mode"),
 ("โหมดคิว","Queue Mode"),
 ("โฮสต์ด้วยตนเอง","self-hosted"),
 ("โฮสต์เอง","self-hosted"),
 ("จัดการด้วยตนเอง","self-managed"),
 ("ความลับของสภาพแวดล้อม","environment secret"),
 ("ความลับ","secret"),
 ("การปรับใช้","deployment"),
 ("การสำรองข้อมูล","backup"),
 ("ข้อมูลสำรอง","backup"),
 ("ไฟล์เขียน Docker","ไฟล์ Docker Compose"),
 ("Docker เขียน","Docker Compose"),
 ("คอมโพส Docker","Docker Compose"),
]

PER_PAGE={
"th/index.html":[
 ("VPS สำหรับ n8n","VPS สำหรับ n8n"),
],
"th/best-vps-for-n8n.html":[
 ("VPS ที่ดีที่สุดสำหรับ n8n","VPS ที่ดีที่สุดสำหรับ n8n"),
],
"th/n8n-backup-restore.html":[
 ("การสำรองและกู้คืน n8n","การ backup และกู้คืน n8n"),
],
"th/install-n8n-vps-docker.html":[
 ("ติดตั้ง n8n บน VPS","ติดตั้ง n8n บน VPS"),
],
"th/n8n-cloud-vs-self-hosted.html":[
 ("n8n Cloud กับโฮสต์ด้วยตนเอง","n8n Cloud เทียบกับ Self-Hosted"),
],
"th/n8n-vps-requirements.html":[
 ("ข้อกำหนด VPS ของ n8n","ข้อกำหนด VPS สำหรับ n8n"),
],
"th/n8n-vps-security.html":[
 ("รักษาความปลอดภัย n8n บน VPS","ความปลอดภัยของ n8n บน VPS"),
],
"th/n8n-queue-mode.html":[
 ("โหมดคิว n8n","n8n Queue Mode"),
],
}

def polish(i):
    en,target=PAGES[i]
    p=ROOT/target
    text=p.read_text(encoding="utf-8")
    before=text;hits=0
    for old,new in PER_PAGE.get(target,[]):
        n=text.count(old)
        if n:
            text=text.replace(old,new);hits+=n
    for old,new in GLOBAL:
        n=text.count(old)
        if n:
            text=text.replace(old,new);hits+=n
    validate((ROOT/en).read_text(encoding="utf-8"),text,en,target)
    if text!=before:
        p.write_text(text,encoding="utf-8")
    print("THAI_NATIVE_POLISH",i+1,"/11",target,"replacements",hits,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _th_native_polish.py PAGE_INDEX")
    i=int(sys.argv[1])
    if not 0<=i<len(PAGES):
        raise SystemExit("Page out of range")
    polish(i)
