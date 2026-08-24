import os
import time
import threading
import requests

# Limite máximo do payload
MAX_MB = 300

firebase = "https://ravendev-vtx-default-rtdb.firebaseio.com".rstrip("/")

mb = float(os.environ.get("PAYLOAD_MB", "0.01"))
interval_ms = int(os.environ.get("INTERVAL_MS", "1000"))
connections = int(os.environ.get("CONNECTIONS", "1"))
duration_ms = int(os.environ.get("DURATION_MS", "10000"))

# Único limite: tamanho do payload
if not (0 < mb <= MAX_MB):
    raise SystemExit(
        f"PAYLOAD_MB deve estar entre 0 e {MAX_MB} MB."
    )

payload = "X" * int(mb * 1024 * 1024)

stats = {
    "ok": 0,
    "errors": 0
}

lock = threading.Lock()


def send_once(connection_id):
    end = time.monotonic() + duration_ms / 1000
    endpoint = f"{firebase}/loadtest.json"

    while time.monotonic() < end:
        try:
            started = time.monotonic()

            response = requests.post(
                endpoint,
                json={
                    "timestamp": int(time.time() * 1000),
                    "connection": connection_id,
                    "data": payload
                },
                timeout=10
            )

            latency = int(
                (time.monotonic() - started) * 1000
            )

            with lock:
                if response.ok:
                    stats["ok"] += 1
                    print(
                        f"[C{connection_id}] OK | "
                        f"HTTP {response.status_code} | "
                        f"{latency} ms",
                        flush=True
                    )
                else:
                    stats["errors"] += 1
                    print(
                        f"[C{connection_id}] ERRO | "
                        f"HTTP {response.status_code} | "
                        f"{latency} ms",
                        flush=True
                    )

        except requests.RequestException as exc:
            with lock:
                stats["errors"] += 1
                print(
                    f"[C{connection_id}] ERRO -> {exc}",
                    flush=True
                )

        remaining = end - time.monotonic()

        if remaining <= 0:
            break

        time.sleep(interval_ms / 1000)


print("================================")
print("       FIREBASE TEST")
print("================================")
print(f"Firebase : {firebase}")
print(f"Payload  : {mb} MB")
print(f"Intervalo: {interval_ms} ms")
print(f"Conexoes : {connections}")
print(f"Duracao  : {duration_ms} ms")
print("--------------------------------")
print("Status   : INICIANDO")

threads = []
started = time.monotonic()

for i in range(1, connections + 1):
    t = threading.Thread(
        target=send_once,
        args=(i,)
    )
    t.start()
    threads.append(t)

for t in threads:
    t.join()

elapsed = int(
    (time.monotonic() - started) * 1000
)

print("--------------------------------")
print("Status   : FINALIZADO")
print(f"Envios OK: {stats['ok']}")
print(f"Erros    : {stats['errors']}")
print(f"Tempo    : {elapsed} ms")
print("================================")
