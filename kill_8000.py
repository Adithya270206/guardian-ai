import psutil

for conn in psutil.net_connections():
    if conn.laddr.port == 8000:
        try:
            p = psutil.Process(conn.pid)
            p.terminate()
            print(f"Killed process {conn.pid} on port 8000")
        except Exception as e:
            print(f"Could not kill process {conn.pid}: {e}")
