from pathlib import Path
import re,xml.etree.ElementTree as ET
root=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site"); out=root/"ja"; out.mkdir(exist_ok=True); base="https://agurkin2021-gif.github.io/vps-for-n8n/"
P=[
("index.html","n8n向けVPS：セルフホスト用サーバーの選び方","n8nをVPSでセルフホストする際のCPU、メモリ、NVMe、Docker、PostgreSQL、HTTPS、運用責任を整理します。","n8n向けVPS：本番運用に合うサーバーの選び方","検証や軽い自動化は1〜2 vCPU / 2GB、本番の出発点は2 vCPU / 4GBが実用的です。AIや大きなデータ処理では4+ vCPU / 8GB+を検討します。","日本での選定ポイント","月額・更新料金、国内リージョンの遅延、NVMe、SLA、スナップショット、root権限、Docker対応、増強しやすさを比較します。"),
("best-vps-for-n8n.html","n8nにおすすめのVPS比較：2GB・4GBと料金","n8n向けVPSをメモリ、CPU、料金、SLA、国内リージョン、Docker対応で比較するための基準。","n8nにおすすめのVPS：2GBか4GBか","個人・低頻度なら2GBでも動作可能ですが、本番・AI・複数Webhookでは4GB以上の余裕が安全です。","比較で見る項目","初期価格だけでなく更新料金、SLA、国内データセンター、バックアップ、転送量、スケールアップ費用を確認します。"),
("n8n-hosting-japan.html","n8nホスティング日本：ManagedとVPSを比較","n8nホスティングのワンクリック導入、Managed運用、VPSセルフホスト、料金、バックアップ、サポート範囲を比較。","n8nホスティング：ManagedかセルフホストVPSか","ホスティング商品にはワンクリック導入、自動更新、バックアップなどを含むものがあります。一方、通常のVPSは自由度が高い代わりに運用責任が増えます。","料金とサポート範囲","月額・更新料金、実行回数制限、root権限、バックアップ、アプリ更新、サポートがVPSまでかn8n内部までかを分けて確認します。"),
("n8n-vps-requirements.html","n8n VPS要件：メモリ・CPU・ストレージ","n8nのVPS要件をメモリ、CPU、NVMe、PostgreSQL、実行数、binary dataから判断します。","n8n VPS要件：メモリとCPU","最小構成を本番保証と考えず、Docker + PostgreSQL + reverse proxyの余裕を確保します。","増強のサイン","OOM/restart、swap、CPU/RAM高止まり、実行遅延、backlogを監視し、実負荷に合わせて増強します。"),
("n8n-cloud-vs-self-hosted.html","n8n Cloud vs セルフホスト：料金と運用比較","n8n CloudとVPSセルフホストを実行数、料金、データ配置、保守、バックアップ、セキュリティで比較。","n8n Cloud vs セルフホストVPS","Cloudはインフラ運用を減らせます。セルフホストはデータ配置や環境を制御できますが、OS・ネットワーク・更新・復旧は自分側の責任です。","TCOで比較","VPS料金だけでなくドメイン、バックアップ、監視、管理時間を含めます。実行数が増えるほど固定費VPSが有利になる場合があります。"),
("n8n-queue-mode.html","n8n Queue Mode：Redis・Workerでスケール","n8n queue modeをRedis、PostgreSQL、workers、concurrency、encryption keyの観点から解説。","n8n Queue Modeとスケーリング","mainがtrigger/webhookを受け、Redisがqueueを保持し、workersが実行します。全instanceからPostgreSQLとRedisへ到達できる構成が必要です。","本番の注意点","workersは同じN8N_ENCRYPTION_KEYを共有し、worker concurrencyとDB connection poolを同時に設計します。"),
("n8n-vps-security.html","n8n VPSセキュリティ：本番ハードニング","n8nセルフホストのHTTPS、firewall、SSH、更新、API制限、credential保護を整理。","n8n VPSセキュリティ","HTTPS/reverse proxy、firewall、SSH key、定期更新を基本にし、不要な公開ポートを閉じます。","データ保護","credentials、execution data、APIアクセスを保護し、Cloudと違ってself-hostedのサーバーセキュリティは運用者側が担います。"),
("n8n-backup-restore.html","n8nバックアップと復元：PostgreSQLと暗号化キー","n8nのdatabase、persistent data、N8N_ENCRYPTION_KEYをバックアップし復元テストする方法。","n8nバックアップと復元","workflow exportだけでは不十分です。DB、persistent volumes/config、encryption keyをサーバー外へ保存します。","復元テスト","同じencryption keyがないと暗号化済みcredentialsを読めません。定期的に別環境へtest restoreします。"),
("install-n8n-vps-docker.html","VPSにn8nをDockerで構築：PostgreSQL・HTTPS","VPSへDocker/Compose、PostgreSQL、domain、HTTPS、reverse proxyでn8nを本番構築する流れ。","VPSにn8nをDockerで構築","Ubuntu/Debian → Docker/Compose → PostgreSQL → persistent volume → domain/DNS → HTTPS/reverse proxy → webhook確認 → backupの順で構築します。","日本VPSのテンプレート","n8n導入テンプレートを提供する国内VPSもあります。簡単な導入と、本番の更新・バックアップ・セキュリティ責任は分けて考えます。")]
links=" · ".join(f'<a href="{x[0]}">{x[2].split("：")[0]}</a>' for x in P)
for fn,title,desc,h1,p1,h2,p2 in P:
 url=base+"ja/"+("" if fn=="index.html" else fn)
 s=f'''<!doctype html><html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><meta name="description" content="{desc}"><meta name="robots" content="index,follow"><link rel="canonical" href="{url}"><link rel="alternate" hreflang="ja" href="{url}"><link rel="alternate" hreflang="en" href="{base}"><link rel="alternate" hreflang="x-default" href="{base}"><link rel="icon" href="../favicon.svg"><link rel="stylesheet" href="../styles.css"></head><body><header><a class="brand" href="index.html">n8n<span>VPS</span></a><div class="lang-switch"><button type="button">日本語 &#9662;</button><div class="lang-menu"><a href="../">English</a><a href="../hi/">हिन्दी</a><a href="../bn/">বাংলা</a><a href="./">日本語</a></div></div></header><main><section class="section"><h1>{h1}</h1><p class="lead">{desc}</p><div class="actions"><a class="primary" href="https://www.vdsina.com/?partner=ni8gzrvz75" rel="sponsored nofollow">VPSを見る</a></div></section><section class="section dark"><h2>{h2}</h2><p>{p1}</p></section><section class="section"><h2>本番運用のポイント</h2><p class="intro">{p2}</p></section><section class="section dark"><p>{links}</p></section></main></body></html>'''
 (out/fn).write_text(s,encoding="utf-8")
urls=[]
for f in root.rglob("*.html"):
 if ".git" in f.parts or f.name=="404.html": continue
 rel=f.relative_to(root).as_posix()
 if rel.endswith("/index.html"): rel=rel[:-10]
 elif rel=="index.html": rel=""
 urls.append(base+rel)
(root/"sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"\n".join(f'  <url><loc>{u}</loc></url>' for u in sorted(set(urls)))+'\n</urlset>\n',encoding="utf-8")
print("JA",len(list(out.glob("*.html"))),"URLS",len(set(urls)))
