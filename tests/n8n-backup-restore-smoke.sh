#!/usr/bin/env bash
# Ephemeral Docker restore tests using synthetic data only. No production n8n access.
set -Eeuo pipefail
N8N_IMAGE="docker.n8n.io/n8nio/n8n:2.42.5"
PG_IMAGE="postgres:16-alpine"
TOOLS_IMAGE="alpine:3.22"
SUFFIX="$(date +%s)-$$"
BASE="n8n-qa-$SUFFIX"
NETWORK="$BASE-net"
TMP="$(mktemp -d)"
# n8n runs as non-root node and must traverse the bind-mounted host directory.
chmod 755 "$TMP"
PASS="synthetic-test-password"
TEST_KEY="synthetic-test-key-01234567890123456789"
cleanup() {
  docker rm -f "$BASE-sqlite-restore" "$BASE-pg-src" "$BASE-pg-dst" >/dev/null 2>&1 || :
  docker volume rm -f "$BASE-sqlite-src" "$BASE-sqlite-dst" "$BASE-pg-home-src" "$BASE-pg-home-dst" >/dev/null 2>&1 || :
  docker network rm "$NETWORK" >/dev/null 2>&1 || :
  rm -rf "$TMP"
}
trap cleanup EXIT
trap 'echo "Restore test failed at line $LINENO" >&2' ERR
wait_pg() {
  for n in $(seq 1 70); do docker exec "$1" pg_isready -U n8n -d n8n >/dev/null 2>&1 && return 0; sleep 2; done
  docker logs --tail 100 "$1" >&2; return 1
}
wait_n8n() {
  for n in $(seq 1 100); do
    docker exec "$1" node -e 'fetch("http://127.0.0.1:5678/healthz").then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))' >/dev/null 2>&1 && return 0
    sleep 2
  done
  docker logs --tail 130 "$1" >&2; return 1
}
volume_backup() {
  docker run --rm -v "$1:/data:ro" -v "$TMP:/out" "$TOOLS_IMAGE" sh -ec "tar -C /data -czf /out/$2 ."
  test -s "$TMP/$2"
}
volume_restore() {
  docker run --rm -v "$1:/data" -v "$TMP:/out:ro" "$TOOLS_IMAGE" sh -ec "tar -C /data -xzf /out/$2"
}
volume_file() {
  docker run --rm -v "$1:/data:ro" -v "$TMP:/out" "$TOOLS_IMAGE" sh -ec "cp /data/$2 /out/$3"
}
verify_export() {
  python3 - "$TMP/$1" "$2" <<'PY'
import json,sys
items=json.load(open(sys.argv[1],encoding='utf-8'))
if isinstance(items,dict): items=[items]
match=[w for w in items if w.get('name')=='QA backup restore witness']
assert len(match)==1, ('Missing witness',sys.argv[2])
workflow=match[0]
assert len(workflow.get('nodes',[]))==2
assert workflow['connections'].get('Manual Trigger')
assert any(n['type']=='n8n-nodes-base.noOp' for n in workflow['nodes'])
print('PASS',sys.argv[2],': witness workflow, nodes, connections')
PY
}
cat > "$TMP/workflow.json" <<'JSON'
[
  {
    "id": "qa-n8n-restore-witness",
    "name": "QA backup restore witness",
    "active": false,
    "nodes": [
      {"id":"qa-trigger-001","name":"Manual Trigger","type":"n8n-nodes-base.manualTrigger","typeVersion":1,"position":[240,300],"parameters":{}},
      {"id":"qa-noop-002","name":"No Operation","type":"n8n-nodes-base.noOp","typeVersion":1,"position":[460,300],"parameters":{}}
    ],
    "connections":{"Manual Trigger":{"main":[[{"node":"No Operation","type":"main","index":0}]]}},
    "settings":{"executionOrder":"v1"},
    "staticData":null,
    "pinData":{},
    "tags":[]
  }
]
JSON
chmod 644 "$TMP/workflow.json"
docker network create "$NETWORK" >/dev/null
for image in "$N8N_IMAGE" "$PG_IMAGE" "$TOOLS_IMAGE"; do docker pull "$image"; done

echo "SCENARIO 1: SQLite user-folder snapshot / clean restore"
docker volume create "$BASE-sqlite-src" >/dev/null
docker volume create "$BASE-sqlite-dst" >/dev/null
docker run --rm -v "$BASE-sqlite-src:/home/node/.n8n" -v "$TMP:/fixtures:ro" "$N8N_IMAGE" import:workflow --input=/fixtures/workflow.json
docker run --rm -v "$BASE-sqlite-src:/home/node/.n8n" "$N8N_IMAGE" export:workflow --all --output=/home/node/.n8n/source.json
volume_file "$BASE-sqlite-src" source.json sqlite-source.json
verify_export sqlite-source.json sqlite-source
# All writers exited; a cold file backup is SQLite-consistent.
volume_backup "$BASE-sqlite-src" sqlite.tar.gz
python3 - "$TMP/sqlite.tar.gz" <<'PY'
import json,sys,tarfile
with tarfile.open(sys.argv[1],'r:gz') as tf:
    files=tf.getnames()
    assert any(f.endswith('database.sqlite') for f in files), files
    config=next(f for f in files if f.endswith('/config') or f=='./config')
    data=json.load(tf.extractfile(config))
    assert data.get('encryptionKey'), 'n8n-generated encryption key absent'
print('PASS SQLite database and original generated encryption key archived')
PY
volume_restore "$BASE-sqlite-dst" sqlite.tar.gz
docker run -d --name "$BASE-sqlite-restore" --network "$NETWORK" -e N8N_DIAGNOSTICS_ENABLED=false -v "$BASE-sqlite-dst:/home/node/.n8n" "$N8N_IMAGE" >/dev/null
wait_n8n "$BASE-sqlite-restore"
docker exec "$BASE-sqlite-restore" n8n export:workflow --all --output=/home/node/.n8n/after.json
volume_file "$BASE-sqlite-dst" after.json sqlite-restored.json
verify_export sqlite-restored.json sqlite-restored
# Do not invoke another CLI n8n process alongside the running server: the Task Broker port is shared.
docker rm -f "$BASE-sqlite-restore" >/dev/null
echo "Executing restored SQLite witness workflow in a standalone n8n process:"
docker run --rm -v "$BASE-sqlite-dst:/home/node/.n8n" "$N8N_IMAGE" execute --id=qa-n8n-restore-witness
echo 'PASS SQLite restored n8n instance boots and executes restored workflow'

echo 'SCENARIO 2: PostgreSQL custom pg_dump + .n8n volume on empty target'
docker volume create "$BASE-pg-home-src" >/dev/null
docker volume create "$BASE-pg-home-dst" >/dev/null
docker run -d --name "$BASE-pg-src" --network "$NETWORK" -e POSTGRES_DB=n8n -e POSTGRES_USER=n8n -e POSTGRES_PASSWORD="$PASS" "$PG_IMAGE" >/dev/null
wait_pg "$BASE-pg-src"
pg_n8n() {
  db_container="$1"; user_volume="$2"; shift 2
  docker run --rm --network "$NETWORK" -e DB_TYPE=postgresdb -e DB_POSTGRESDB_HOST="$db_container" -e DB_POSTGRESDB_DATABASE=n8n -e DB_POSTGRESDB_USER=n8n -e DB_POSTGRESDB_PASSWORD="$PASS" -e N8N_ENCRYPTION_KEY="$TEST_KEY" -v "$user_volume:/home/node/.n8n" -v "$TMP:/fixtures:ro" "$N8N_IMAGE" "$@"
}
pg_n8n "$BASE-pg-src" "$BASE-pg-home-src" import:workflow --input=/fixtures/workflow.json
pg_n8n "$BASE-pg-src" "$BASE-pg-home-src" export:workflow --all --output=/home/node/.n8n/source-pg.json
volume_file "$BASE-pg-home-src" source-pg.json postgres-source.json
verify_export postgres-source.json postgres-source
docker exec "$BASE-pg-src" pg_dump -U n8n -d n8n -Fc > "$TMP/n8n-postgres.dump"
test -s "$TMP/n8n-postgres.dump"
docker exec -i "$BASE-pg-src" pg_restore --list < "$TMP/n8n-postgres.dump" > "$TMP/toc.txt"
test -s "$TMP/toc.txt"
volume_backup "$BASE-pg-home-src" postgres-user-folder.tar.gz
docker run -d --name "$BASE-pg-dst" --network "$NETWORK" -e POSTGRES_DB=n8n -e POSTGRES_USER=n8n -e POSTGRES_PASSWORD="$PASS" "$PG_IMAGE" >/dev/null
wait_pg "$BASE-pg-dst"
docker exec -i "$BASE-pg-dst" pg_restore --exit-on-error --no-owner --no-acl -U n8n -d n8n < "$TMP/n8n-postgres.dump"
volume_restore "$BASE-pg-home-dst" postgres-user-folder.tar.gz
pg_n8n "$BASE-pg-dst" "$BASE-pg-home-dst" export:workflow --all --output=/home/node/.n8n/after-pg.json
volume_file "$BASE-pg-home-dst" after-pg.json postgres-restored.json
verify_export postgres-restored.json postgres-restored
echo "Executing restored PostgreSQL witness workflow:"
pg_n8n "$BASE-pg-dst" "$BASE-pg-home-dst" execute --id=qa-n8n-restore-witness
echo 'PASS PostgreSQL dump, target restore, n8n workflow and execution'
echo 'ALL ISOLATED REAL-N8N RESTORE TESTS PASSED'
