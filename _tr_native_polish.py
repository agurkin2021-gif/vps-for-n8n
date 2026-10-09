#!/usr/bin/env python3
"""Conservative native-Turkish editorial polish; never changes HTML structure or technical values."""
from pathlib import Path
import sys
from _tr_translate_full import PAGES,ROOT,validate

GLOBAL=[
 ("n8n'ı","n8n'i"),("n8n'ın","n8n'in"),("n8n'a","n8n'e"),
 ("n8n Bulut","n8n Cloud"),
 ("Kendi Kendine Barındırılan","Self-Hosted"),
 ("Kendi kendine barındırılan","Self-hosted"),
 ("kendi kendine barındırılan","self-hosted"),
 ("Şirket içinde barındırılan","Self-hosted"),
 ("şirket içinde barındırılan","self-hosted"),
 ("Kuyruk Modu","Queue Mode"),("Kuyruk modu","Queue Mode"),("kuyruk modu","Queue Mode"),
 ("Sıra modu","Queue Mode"),("sıra modu","Queue Mode"),
 ("Web kancası","Webhook"),("web kancası","webhook"),
 ("Ters proxy","Reverse proxy"),("ters proxy","reverse proxy"),
 ("Docker Oluştur","Docker Compose"),
 ("Genel ana makine adı","Genel hostname"),
]

PER_PAGE={
"tr/index.html":[
 ("$0.07/Day'den n8n için VPS - Planlar ve Boyutlandırma Kılavuzu","n8n için VPS — $0.07/Day'den Başlayan Planlar ve Boyutlandırma Rehberi"),
 ("VPS için n8n","n8n için VPS"),
 ("İthalat, belgeler ve daha ağır işler","Veri içe aktarma, belgeler ve daha ağır işler"),
 ("Yapılandırmanızı VPS sırasına dönüştürün","Yapılandırmanızı bir VPS siparişine dönüştürün"),
 ("Başvuruyu hazırlayın","Uygulamayı hazırlayın"),
 ("VPS n8n için doğru seçim olduğunda","n8n için VPS ne zaman doğru seçimdir?"),
 ("Yönetilen barındırma için Bulut'u seçin","Yönetilen barındırma için n8n Cloud'u seçin"),
 ("Bir örnekle başlayın. Gerektiğinde işçi ekleyin.","Tek bir n8n instance ile başlayın. Gerektiğinde worker ekleyin."),
 ("Yürütme geçmişinin büyümesi için","Çalıştırma geçmişi büyüdüğünde"),
],
"tr/best-vps-for-n8n.html":[
 ("2026'deki n8n için En İyi VPS: 6 Sağlayıcıları Karşılaştırıldı","2026'da n8n için En İyi VPS: 6 Sağlayıcı Karşılaştırması"),
 ("n8n için en iyi VPS: 6 sağlayıcı seçenekleri","n8n için En İyi VPS: 6 Sağlayıcı Seçeneği"),
 ("İyi bir n8n VPS'i kötü uyumdan ayıran kriterler","İyi bir n8n VPS'i uygun olmayan bir seçenekten ayıran kriterler"),
 ("Yenileme ve ekstralar","Yenileme ve ek maliyetler"),
 ("Tek bir sağlayıcının her şeyi kazandığını iddia etmeden kısa öneriler","Her ihtiyaca tek bir kazanan atamadan kısa öneriler"),
 ("En düşük sürtünmeli başlangıcı istiyorum","En kolay başlangıcı istiyorum"),
 ("Daha sonra sıra modunu bekliyorum","Daha sonra Queue Mode'a geçmeyi planlıyorum"),
 ("En çok göçü önemsiyorum","Migration ve taşınabilirlik benim için en önemli konu"),
 ("Sağlayıcı seçimi sunucu boyutlandırması değildir","Sağlayıcı seçimi ile sunucu boyutlandırması aynı karar değildir"),
],
"tr/n8n-vps-docker-kurulumu.html":[
 ("n8n'ı bir VPS'e yükleyin","VPS'e n8n Kurulumu"),
 ("n8n'e başlamadan önce VPS'ı hazırlayın","n8n kurulumundan önce VPS'i hazırlayın"),
 ("1. Docker, DNS maddelerini hazırlayın ve erişin","1. Docker, DNS ve erişimi hazırlayın"),
 ("5. Kapları başlatın ve dışarıdan test edin","5. Container'ları başlatın ve dışarıdan test edin"),
 ("6. Sabitlenmiş sürümleri değiştirmeden önce yedekleyin","6. Pinlenmiş sürümleri değiştirmeden önce yedek alın"),
 ("n8n ve PostgreSQL ayrı ayrı devam etsin","n8n ve PostgreSQL verilerini ayrı ayrı kalıcı tutun"),
 ("n8n veri","n8n verisi"),
 ("PostgreSQL veri","PostgreSQL verisi"),
],
"tr/n8n-cloud-vs-self-hosted.html":[
 ("n8n Bulut ve Kendi Kendine Barındırılan Karşılaştırması: Maliyet ve Kontrol","n8n Cloud vs Self-Hosted: Maliyet ve Kontrol"),
 ("n8n Bulut ve Kendi Kendine Barındırılan Karşılaştırması","n8n Cloud vs Self-Hosted"),
 ("Şu durumlarda şirket içinde barındırılan VPS seçeneğini seçin:","Şu durumlarda self-hosted VPS seçin:"),
 ("Basit bir program Bulut yürütme iznini nasıl kullanabilir?","Basit bir schedule n8n Cloud execution kotasını nasıl tüketebilir?"),
 ("Tek tıklama n8n VPS her zaman yönetilen bir hizmet değildir","Tek tıkla kurulan n8n VPS her zaman managed hosting değildir"),
 ("Kendi kendine ev sahipliği yaptığınızda neleri üstlenirsiniz?","Self-hosting yaptığınızda hangi sorumlulukları üstlenirsiniz?"),
 ("Bulut kolaylığı ve şirket içinde barındırılan ölçeklendirme kontrolü","Cloud kolaylığı ile self-hosted ölçeklendirme kontrolü"),
],
"tr/n8n-vps-gereksinimleri.html":[
 ("n8n VPS Gereksinimler","n8n VPS Gereksinimleri"),
 ("Minimum, pratik üretim ve daha ağır iş yükleri","Minimum, pratik production ve daha ağır iş yükleri"),
 ("Pratik küçük üretim","Pratik küçük production"),
 ("Eşzamanlı yürütmeler","Eşzamanlı çalıştırmalar"),
 ("CPU-ağır düğümler","CPU yoğun node'lar"),
 ("Sipariş vermeden önce n8n yürütme geçmişi depolama alanını tahmin edin","Sipariş vermeden önce n8n çalıştırma geçmişi için gereken depolamayı tahmin edin"),
],
"tr/n8n-vps-guvenlik.html":[
 ("n8n'ı VPS'e sabitleyin","n8n VPS Güvenliği"),
 ("Sertleşme SSH","SSH hardening"),
 ("TLS fesih","TLS termination"),
 ("Çevre sırları","Environment secret'ları"),
 ("Konteyner teşhiri","Container erişimi"),
 ("n8n güvenlik denetimini çalıştır","n8n security audit'i çalıştırın"),
],
"tr/n8n-queue-mode.html":[
 ("İşçi kapasitesi","Worker kapasitesi"),
 ("İşçiler hem sayıma hem de işçi başına işe göre ölçeklendirilir","Worker kapasitesi, worker sayısı ve worker başına concurrency ile ölçeklenir"),
 ("Şu durumlarda işçi ekleyin:","Şu durumlarda worker ekleyin:"),
 ("PostgreSQL'ı izle","PostgreSQL'i izleyin"),
 ("Kuyruğun yardımcı olup olmadığını öğrenin","Queue Mode'un fayda sağlayıp sağlamadığını ölçün"),
 ("Kuyruk derinliği","Queue depth"),
 ("Kuyruk modu yürütme aktarma gecikmesini artırabilir","Queue Mode, execution handoff gecikmesini artırabilir"),
 ("İlk önce dikey olarak ölçeklendirin","Önce dikey ölçeklendirmeyi deneyin"),
]
}

def polish(i):
    en,tr=PAGES[i]
    p=ROOT/tr
    text=p.read_text(encoding="utf-8")
    before=text
    hits=0
    for old,new in PER_PAGE.get(tr,[]):
        n=text.count(old)
        if n:
            text=text.replace(old,new);hits+=n
    for old,new in GLOBAL:
        n=text.count(old)
        if n:
            text=text.replace(old,new);hits+=n
    validate((ROOT/en).read_text(encoding="utf-8"),text,en,tr)
    if text!=before:p.write_text(text,encoding="utf-8")
    print("TURKISH_NATIVE_POLISH",i+1,"/11",tr,"replacements",hits,flush=True)

if __name__=="__main__":
    if len(sys.argv)!=2 or not sys.argv[1].isdigit():raise SystemExit("Usage: python _tr_native_polish.py PAGE_INDEX")
    i=int(sys.argv[1])
    if not 0<=i<len(PAGES):raise SystemExit("Page out of range")
    polish(i)
