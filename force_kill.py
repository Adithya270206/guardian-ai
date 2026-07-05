import subprocess
import re

out = subprocess.check_output("netstat -ano | findstr :8000", shell=True, text=True)
pids = set()
for line in out.strip().split("\n"):
    if not line: continue
    parts = line.strip().split()
    if len(parts) >= 5:
        pid = parts[-1]
        if pid != "0":
            pids.add(pid)

for pid in pids:
    print(f"Killing PID {pid}")
    subprocess.run(f"taskkill /F /PID {pid}", shell=True)
