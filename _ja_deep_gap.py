from pathlib import Path
r=Path(r"C:\Users\User\SEO_NICHE_RESEARCH\VPS for N8N\site\ja")
adds={
"best-vps-for-n8n.html":"日本の比較SERPでは2GB/4GBだけでなくSLA、SSD/NVMe容量、転送量、契約期間と更新料金が意思決定要素です。検証用途と顧客向け本番ではSLAの優先度を分けて判断します。",
"n8n-vps-requirements.html":"実測記事では1GBでheap out of memory、2GBで軽量処理が完走する例がありますが、これは全workloadの保証ではありません。AI、binary data、並列実行、PostgreSQLを含む本番では4GB以上の余裕を基準に実測します。",
"n8n-cloud-vs-self-hosted.html":"比較時はCloudのexecution上限と月額だけでなく、Community Editionの機能範囲、セルフホスト側のドメイン・backup・監視・管理時間もTCOに含めます。execution数が増えるほど固定費VPSが有利になる場合があります。",
"install-n8n-vps-docker.html":"本番ではN8N_ENCRYPTION_KEY、WEBHOOK_URL、GENERIC_TIMEZONE/TZを明示し、container imageのversionを固定します。n8nの5678とPostgreSQLの5432は直接Internetへ公開せず、reverse proxy経由で80/443のみ公開する構成を優先します。",
"n8n-vps-security.html":"初回owner作成を放置せず、MFAを有効化し、5678/5432をpublic listenerにしないことを確認します。execution dataの保持期間も制御し、不要な成功executionやbinary dataでdiskを圧迫しないようpruningを設定します。",
"n8n-backup-restore.html":"backupは取得だけでなく別環境への復元を実施して検証します。PostgreSQL、persistent volume、N8N_ENCRYPTION_KEYを同じ復旧手順で戻せることを確認し、upgrade前にもrestore pointを作ります。",
"n8n-queue-mode.html":"公式構成ではworker concurrencyの既定値は10で、5以上が推奨されています。worker数を増やしすぎるとPostgreSQL connection poolを枯渇させるため、RedisだけでなくDB接続数とhealth/readinessも監視します。queue modeではSQLiteではなくPostgreSQLを使います。"
}
for fn,text in adds.items():
 p=r/fn;s=p.read_text(encoding="utf-8")
 if text in s:continue
 marker='<section class="section dark"><p>'
 block=f'<section class="section"><h2>SERPで確認した追加ポイント</h2><p class="intro">{text}</p></section>'
 s=s.replace(marker,block+marker,1);p.write_text(s,encoding="utf-8")
print("UPDATED",len(adds))
