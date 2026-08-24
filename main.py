import os
import time
import threading
import requests

MAX_MB = 5
MAX_CONNECTIONS = 5
MAX_DURATION_MS = 60_000
MIN_INTERVAL_MS = 1_000

firebase = os.environ["https://ravendev-vtx-default-rtdb.firebaseio.com"].rstrip("/")
mb = float(os.environ.get("PAYLOAD_MB", "0.01"))
interval_ms = int(os.environ.get("INTERVAL_MS", "1000"))
connections = int(os.environ.get("CONNECTIONS", "1"))
duration_ms = int(os.environ.get("DURATION_MS", "10000"))

if not (0 < mb <= MAX_MB):
    raise SystemExit(f"PAYLOAD_MB deve estar entre 0 e {MAX_MB} MB.")
if interval_ms < MIN_INTERVAL_MS:
    raise SystemExit(f"INTERVAL_MS minimo: {MIN_INTERVAL_MS} ms.")
if not (1 <= connections <= MAX_CONNECTIONS):
    raise SystemExit(f"CONNECTIONS deve estar entre 1 e {MAX_CONNECTIONS}.")
if not (1000 <= duration_ms <= MAX_DURATION_MS):
    raise SystemExit(f"DURATION_MS deve estar entre 1000 e {MAX_DURATION_MS} ms.")

payload = "X" * int(mb * 1024 * 1024)
stats = {"ok": 0, "errors": 0}
lock = threading.Lock()

def send_once(connection_id):
    end = time.monotonic() + duration_ms / 1000
    endpoint = firebase + "/loadtest.json"

    while time.monotonic() < end:
        try:
            started = time.monotonic()
            r = requests.post(
                endpoint,
                json={
                    "timestamp": int(time.time() * 1000),
                    "connection": connection_id,
                    "data": payload,
                },
                timeout=10,
            )
            latency = int((time.monotonic() - started) * 1000)

            with lock:
                if r.ok:
                    stats["ok"] += 1
                    print(
                        f"[C{connection_id}] ENVIANDO -> OK "
                        f"HTTP {r.status_code} | {latency} ms",
                        flush=True,
                    )
                else:
                    stats["errors"] += 1
                    print(
                        f"[C{connection_id}] ENVIANDO -> ERRO "
                        f"HTTP {r.status_code} | {latency} ms",
                        flush=True,
                    )
        except requests.RequestException as exc:
            with lock:
                stats["errors"] += 1
                print(f"[C{connection_id}] ERRO -> {exc}", flush=True)

        remaining = end - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(interval_ms / 1000, remaining))

print("================================")
print("     FIREBASE TEST - GITHUB")
print("================================")
print(f"Firebase : {firebase}")
print(f"Peso     : {mb} MB")
print(f"Intervalo: {interval_ms} ms")
print(f"Conexoes : {connections}")
print(f"Duracao  : {duration_ms} ms")
print("--------------------------------")
print("Status   : INICIANDO", flush=True)

threads = []
started = time.monotonic()

for i in range(1, connections + 1):
    t = threading.Thread(target=send_once, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

elapsed = int((time.monotonic() - started) * 1000)

print("--------------------------------")
print("Status   : FINALIZADO")
print(f"Envios OK: {stats['ok']}")
print(f"Erros    : {stats['errors']}")
print(f"Tempo    : {elapsed} ms")
print("================================")
