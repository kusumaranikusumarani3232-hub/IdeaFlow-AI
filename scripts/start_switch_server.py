import os
import subprocess
import sys
import time
import urllib.request

env_file = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\run\switch-core.env"
pg_ctl = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\toolchain\bundle-057e6b8bca99\postgres\bin\pg_ctl.exe"
pg_data = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\pgdata"
pg_log = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\logs\postgres.log"
switch_exe = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\switch-core\0.31.0\venv\Scripts\switch-core.exe"

# 1. Start postgres if not running
try:
    status = subprocess.run([pg_ctl, "status", "-D", pg_data], capture_output=True, text=True)
    if "is running" not in status.stdout:
        print("Starting PostgreSQL...")
        subprocess.run([pg_ctl, "start", "-D", pg_data, "-l", pg_log], check=True)
    else:
        print("PostgreSQL is already running.")
except Exception as e:
    print("Postgres check/start error:", e)

# 2. Load env vars
env = dict(os.environ)
with open(env_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

print(f"Loaded {len(env)} environment variables. DB_HOST={env.get('DB_HOST')}, SERVER_PORT={env.get('SERVER_PORT')}")

# 3. Start switch-core.exe
print("Starting switch-core.exe...")
proc = subprocess.Popen([switch_exe], env=env)
print(f"switch-core.exe started with PID {proc.pid}")

# Wait for health check
for i in range(15):
    time.sleep(1)
    try:
        with urllib.request.urlopen("http://127.0.0.1:64008/health", timeout=2) as r:
            if r.status == 200:
                print("Switch Server is HEALTHY! Status:", r.status, r.read().decode())
                break
    except Exception as e:
        print(f"Waiting for health check ({i+1}/15)... {e}")


