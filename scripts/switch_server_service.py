import os
import subprocess
import sys
import time

env_file = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\run\switch-core.env"
pg_ctl = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\toolchain\bundle-057e6b8bca99\postgres\bin\pg_ctl.exe"
pg_data = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\pgdata"
pg_log = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\logs\postgres.log"
switch_exe = r"C:\Users\kusuma\AppData\Roaming\switchdash\local-switch-server\native\switch-core\0.31.0\venv\Scripts\switch-core.exe"

print("[Switch Service] Starting PostgreSQL server...")
try:
    subprocess.run([pg_ctl, "start", "-D", pg_data, "-l", pg_log, "-w"], check=True)
    print("[Switch Service] PostgreSQL started successfully.")
except Exception as e:
    print(f"[Switch Service] Note on pg_ctl start: {e}")

# Load environment
env = dict(os.environ)
with open(env_file, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip()

print(f"[Switch Service] Environment loaded ({len(env)} vars). Launching switch-core...")
sys.stdout.flush()

# Run switch-core directly in the foreground of this daemon process
try:
    p = subprocess.Popen([switch_exe], env=env)
    p.wait()
except Exception as e:
    print(f"[Switch Service] switch-core terminated: {e}")
finally:
    print("[Switch Service] Stopping PostgreSQL on service exit...")
    subprocess.run([pg_ctl, "stop", "-D", pg_data, "-m", "fast"])

