#!/usr/bin/env python3
"""Conservative native-Indonesian editorial polish; preserves HTML structure and technical values."""
from pathlib import Path
import sys,re
from _id_translate_full import PAGES,ROOT,validate

GLOBAL=[
 ("workeran","pekerjaan"),("Workeran","Pekerjaan"),
 ("kesecretan","kerahasiaan"),("Kesecretan","Kerahasiaan"),
 ("tunjangan","kuota"),("Tunjangan","Kuota"),
 ("pemutakhiran","upgrade"),("Pemutakhiran","Upgrade"),
 ("Otomatisasi cahaya","Otomatisasi ringan"),("otomatisasi cahaya","otomatisasi ringan"),
 ("Alur kerja","Workflow"),("alur kerja","workflow"),
 ("Pekerja","Worker"),("pekerja","worker"),
 ("Mode antrian","Queue Mode"),("mode antrian","Queue Mode"),
 ("Mode antrean","Queue Mode"),("mode antrean","Queue Mode"),
 ("Antrean","Queue"),("antrean","queue"),("Antrian","Queue"),("antrian","queue"),
 ("Penerapan","Deployment"),("penerapan","deployment"),
 ("Pencadangan","Backup"),("pencadangan","backup"),
 ("Cadangan","Backup"),("cadangan","backup"),
 ("lalu lintas","traffic"),("Lalu lintas","Traffic"),
 ("Muatan","Payload"),("muatan","payload"),
 ("Proksi terbalik","Reverse proxy"),("proksi terbalik","reverse proxy"),
 ("Titik akhir","Endpoint"),("titik akhir","endpoint"),
 ("Tumpukan","Stack"),("tumpukan","stack"),
 ("pelayan","server"),
 ("Lingkungan Hidup","Environment"),
 ("Rahasia lingkungan","Environment secret"),("rahasia lingkungan","environment secret"),
 ("Rahasia","Secret"),("rahasia","secret"),
 ("Simpul","Node"),("simpul","node"),
 ("kait web","webhook"),("Kait web","Webhook"),
 ("tembok api","firewall"),("Tembok api","Firewall"),
 ("Kegigihan","Persistensi"),("kegigihan","persistensi"),
 ("Docker Tulis","Docker Compose"),("Docker Menulis","Docker Compose"),
 ("file Tulis","file Compose"),("layanan Tulis","layanan Compose"),
 ("stack Tulis","stack Compose"),("tumpukan Tulis","stack Compose"),
 ("wadah","container"),("Wadah","Container"),
 ("kontainer","container"),("Kontainer","Container"),
 ("nama host","hostname"),("Nama host","Hostname"),
 ("dihosting sendiri","self-hosted"),("Dihosting Sendiri","Self-Hosted"),
 ("yang dihosting sendiri","self-hosted"),
 ("Hosting mandiri","Self-hosting"),("hosting mandiri","self-hosting"),
 ("swakelola","self-managed"),("Swakelola","Self-managed"),
 ("gambar sekali klik","image sekali klik"),("Gambar sekali klik","Image sekali klik"),
 ("Modus antrian","Queue Mode"),("modus antrian","Queue Mode"),
 ("Awan","Cloud"),("awan","cloud"),
 ("tunjangan eksekusi","kuota eksekusi"),("Tunjangan eksekusi","Kuota eksekusi"),
 ("pembayaran yang telah dipilih sebelumnya","checkout dengan konfigurasi yang sudah dipilih"),
 ("pembaruan dan tambahan","perpanjangan dan biaya tambahan"),
 ("Pembaruan dan tambahan","Perpanjangan dan biaya tambahan"),
 ("ruang lingkup dukungan","cakupan dukungan"),
]

PER_PAGE={
"id/index.html":[
 ("VPS untuk n8n dari $0.07/Day - Panduan Rencana &amp; Ukuran","VPS untuk n8n mulai $0.07/Day — Panduan Paket &amp; Kapasitas"),
 ("PILIH SUMBER DAYA YANG DIBUTUHKAN ALUR KERJA ANDA","PILIH SUMBER DAYA YANG DIBUTUHKAN WORKFLOW ANDA"),
 ("RENCANA PENERAPAN ANDA","RENCANA DEPLOYMENT ANDA"),
 ("80 GB penyimpanan · 32 TB lalu lintas · Standard jangkauan","80 GB penyimpanan · 32 TB traffic · Seri Standard"),
 ("01 · OTOMATISASI CAHAYA","01 · OTOMATISASI RINGAN"),
 ("Otomatisasi cahaya — 1 vCPU / 2 GB / 40 GB — $0.50/day","Otomatisasi ringan — 1 vCPU / 2 GB / 40 GB — $0.50/day"),
 ("Ubah konfigurasi Anda menjadi urutan VPS","Ubah konfigurasi Anda menjadi pesanan VPS"),
 ("Ketika VPS adalah pilihan yang tepat untuk n8n","Kapan VPS menjadi pilihan yang tepat untuk n8n?"),
 ("Mulailah dengan satu contoh. Tambahkan pekerja bila diperlukan.","Mulai dengan satu instance. Tambahkan worker bila diperlukan."),
 ("Apa yang Anda bayar saat Anda menghosting sendiri n8n","Apa yang sebenarnya Anda bayar saat self-host n8n"),
 ("Perkirakan berapa biaya sebenarnya n8n VPS bulan Anda","Perkirakan biaya nyata VPS n8n per bulan"),
 ("Standard VPS harga dan termasuk lalu lintas","Harga VPS Standard dan traffic yang disertakan"),
 ("Resmi Docker Instruksi penulisan ·","Petunjuk resmi Docker Compose ·"),
 ("TAHU APA YANG HARUS DIPILIH","KETAHUI APA YANG HARUS DIPILIH"),
],
"id/best-vps-for-n8n.html":[
 ("VPS terbaik untuk n8n di 2026: 6 Penyedia Dibandingkan","VPS Terbaik untuk n8n pada 2026: Perbandingan 6 Penyedia"),
 ("Kriteria yang memisahkan n8n VPS yang baik dari yang buruk","Kriteria yang membedakan VPS n8n yang baik dari pilihan yang tidak cocok"),
 ("Saya ingin start dengan gesekan terendah","Saya ingin memulai semudah mungkin"),
 ("Saya mengharapkan mode antrian nanti","Saya berencana menggunakan Queue Mode nanti"),
 ("Rekomendasi singkat tanpa berpura-pura bahwa satu penyedia memenangkan segalanya","Rekomendasi singkat tanpa menganggap satu penyedia unggul dalam semua skenario"),
 ("Pembaruan dan tambahan","Perpanjangan dan biaya tambahan"),
 ("Pilihan penyedia bukan ukuran server","Memilih penyedia dan menentukan ukuran server adalah dua keputusan berbeda"),
 ("Tumpukan 4 contoh:","Contoh Stack 4:"),
 ("Docker Tulis file","file Docker Compose"),
],
"id/about.html":[
 ("Ruang lingkup editorial","Cakupan editorial"),
],
"id/n8n-backup-restore.html":[
 ("n8n Pencadangan dan Pemulihan","Backup dan Pemulihan n8n"),
 ("Apa yang harus dilindungi oleh cadangan n8n","Apa yang harus dilindungi oleh backup n8n"),
 ("Alur kerja &amp; ekspor kredensial","Ekspor workflow &amp; kredensial"),
 ("Cuplikan penyedia","Snapshot penyedia"),
 ("Sejarah eksekusi","Riwayat eksekusi"),
 ("Cadangan pada VPS yang sama hanyalah salinan lokal","Backup pada VPS yang sama hanyalah salinan lokal"),
 ("Cadangan tidak akan terbukti sampai pemulihan berhasil","Backup belum terbukti sampai proses pemulihan berhasil"),
 ("CLI ekspor bukan merupakan cadangan instance lengkap","Ekspor CLI bukan backup instance lengkap"),
 ("n8n pencadangan dan pemulihan: pertanyaan umum","Backup dan pemulihan n8n: pertanyaan umum"),
],
"id/contact.html":[
 ("Hubungi | n8nVPS","Kontak | n8nVPS"),
 ("Status kontak","Informasi kontak"),
],
"id/install-n8n-vps-docker.html":[
 ("Instal n8n pada VPS","Instal n8n di VPS"),
 ("Siapkan VPS sebelum memulai n8n","Siapkan VPS sebelum menginstal n8n"),
 ("Docker Menulis","Docker Compose"),
 ("tembok api","Firewall"),
 ("Instal n8n pada VPS Anda dengan Docker Tulis","Instal n8n di VPS Anda dengan Docker Compose"),
 ("2. Ciptakan nilai lingkungan dan pertahankan kuncinya","2. Buat nilai environment dan simpan kuncinya"),
 ("3. Tulis composer.yaml untuk instalasi baru","3. Buat compose.yaml untuk instalasi baru"),
 ("4. Buat file Caddy HTTPS","4. Buat Caddyfile HTTPS"),
 ("5. Mulai wadah dan uji dari luar","5. Jalankan container dan uji dari luar"),
 ("6. Cadangkan sebelum mengubah versi yang dipasangi pin","6. Backup sebelum mengubah versi yang dipin"),
 ("Tetapkan rahasia dan URL publik dengan sengaja","Atur secret dan URL publik secara eksplisit"),
 ("PostgreSQL kredensial","Kredensial PostgreSQL"),
 ("URL kait web","URL webhook"),
 ("Kegigihan yang hilang","Persistensi hilang"),
 ("Periksa titik akhir kesehatan n8n","Periksa health endpoint n8n"),
 ("Sematkan versi aplikasi","Pin versi aplikasi"),
 ("Jangan menempatkan PostgreSQL versi mayor pada tempatnya","Jangan menaikkan versi mayor PostgreSQL langsung di tempat"),
],
"id/n8n-cloud-vs-self-hosted.html":[
 ("n8n Cloud vs Dihosting Sendiri","n8n Cloud vs Self-Hosted"),
 ("Pilih n8n Cloud kapan","Pilih n8n Cloud ketika"),
 ("Pilih yang dihosting sendiri VPS kapan","Pilih VPS self-hosted ketika"),
 ("n8n Cloud vs yang dihosting sendiri VPS: tabel perbandingan","n8n Cloud vs VPS self-hosted: tabel perbandingan"),
 ("Bagaimana jadwal sederhana dapat menggunakan tunjangan eksekusi Cloud","Bagaimana jadwal sederhana menggunakan kuota eksekusi Cloud"),
 ("Hosting mandiri bukan hanya faktur VPS","Self-hosting bukan sekadar tagihan VPS"),
 ("Dimana self hosting mengubah arsitekturnya","Di mana self-hosting mengubah arsitektur"),
 ("Apa yang Anda ambil saat Anda menjadi tuan rumah mandiri","Tanggung jawab yang Anda ambil saat self-hosting"),
 ("Lajang VPS","Satu VPS"),
 ("Modus antrian","Queue Mode"),
 ("Mulailah dengan Awan","Mulai dengan Cloud"),
 ("n8n Awan","n8n Cloud"),
 ("Komunitas yang Dihosting Sendiri","Community Self-Hosted"),
 ("Bisnis/Perusahaan yang dihosting sendiri","Business/Enterprise Self-Hosted"),
],
"id/n8n-vps-requirements.html":[
 ("n8n VPS Persyaratan","Persyaratan VPS n8n"),
 ("Produksi minimal, praktis, dan beban kerja lebih berat","Minimum, produksi praktis, dan beban kerja lebih berat"),
 ("CPU-simpul berat","Node yang intensif CPU"),
 ("Perkirakan n8n penyimpanan riwayat eksekusi sebelum memesan","Perkirakan penyimpanan riwayat eksekusi n8n sebelum memesan"),
 ("Docker &amp; Menulis","Docker &amp; Compose"),
 ("HTTPS &amp; membalikkan proksi","HTTPS &amp; reverse proxy"),
 ("Cara menggunakan entri 1 GB VPS","Cara menggunakan opsi VPS 1 GB"),
],
"id/privacy.html":[
 ("Kebijakan Privasi | n8nVPS","Kebijakan Privasi | n8nVPS"),
 ("Analisis dan tautan afiliasi","Analytics dan tautan afiliasi"),
],
"id/n8n-vps-security.html":[
 ("Amankan n8n pada VPS","Keamanan n8n di VPS"),
 ("Garis dasar keamanan minimum sebelum paparan publik","Baseline keamanan minimum sebelum akses publik"),
 ("Mengeras SSH","Hardening SSH"),
 ("TLS penghentian","TLS termination"),
 ("Proksi terbalik, HTTPS dan header tepercaya","Reverse proxy, HTTPS, dan header tepercaya"),
 ("Jaga kerahasiaan layanan backend","Jaga layanan backend tetap privat"),
 ("Rahasia lingkungan","Environment secret"),
 ("Keamanan adalah proses operasi","Keamanan adalah proses operasional berkelanjutan"),
 ("Amankan tumpukan sebelum mengaktifkan alur kerja produksi","Amankan seluruh stack sebelum mengaktifkan workflow produksi"),
 ("Gunakan SSRF dan kontrol rahasia dengan sengaja","Gunakan kontrol SSRF dan secret secara eksplisit"),
],
"id/n8n-queue-mode.html":[
 ("n8n Mode Antrian","n8n Queue Mode"),
 ("Apakah Anda benar-benar memerlukan mode antrian?","Apakah Anda benar-benar memerlukan Queue Mode?"),
 ("Tetap dalam mode reguler kapan","Tetap gunakan mode reguler ketika"),
 ("Pertimbangkan mode antrian kapan","Pertimbangkan Queue Mode ketika"),
 ("Cara kerja mode antrian n8n","Cara kerja Queue Mode n8n"),
 ("Apa yang dibutuhkan oleh setiap penerapan mode antrean","Komponen yang dibutuhkan setiap deployment Queue Mode"),
 ("Kapasitas pekerja","Kapasitas worker"),
 ("Skala pekerja berdasarkan jumlah dan pekerjaan per pekerja","Skalakan worker berdasarkan jumlah dan concurrency per worker"),
 ("Tambahkan pekerja kapan","Tambahkan worker ketika"),
 ("Tonton PostgreSQL","Pantau PostgreSQL"),
 ("Mode antrian dapat menambahkan latensi handoff eksekusi","Queue Mode dapat menambah latensi handoff eksekusi"),
 ("Ketahui apakah antrean membantu","Ukur apakah Queue Mode benar-benar membantu"),
 ("Kedalaman antrian","Queue depth"),
 ("Pekerja CPU &amp; RAM","CPU &amp; RAM worker"),
 ("JALUR PENskalaan","JALUR SCALING"),
 ("Contoh tunggal n8n dengan PostgreSQL; mengukur puncak CPU, RAM dan konkurensi.","Satu instance n8n dengan PostgreSQL; ukur puncak CPU, RAM, dan concurrency."),
]
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
        if old.isalpha():
            text,n=re.subn(r'\b'+re.escape(old)+r'\b',new,text)
        else:
            n=text.count(old)
            if n:text=text.replace(old,new)
        hits+=n
    validate((ROOT/en).read_text(encoding="utf-8"),text,en,target)
    if text!=before:
        p.write_text(text,encoding="utf-8")
    print("INDONESIAN_NATIVE_POLISH",i+1,"/11",target,"replacements",hits,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():
        raise SystemExit("Usage: python _id_native_polish.py PAGE_INDEX")
    i=int(sys.argv[1])
    if not 0<=i<len(PAGES):
        raise SystemExit("Page out of range")
    polish(i)
