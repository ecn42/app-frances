from __future__ import annotations

import os
import subprocess
import sys


def bootstrap_db() -> None:
    script = os.path.join("scripts", "bootstrap_db.py")
    if not os.path.exists(script):
        return
    result = subprocess.run([sys.executable, script], check=False)
    if result.returncode != 0:
        # Keep app startup alive so deploy healthcheck can surface runtime logs.
        print(f"[warn] bootstrap_db failed with code {result.returncode}, continuing startup.")


def main() -> int:
    bootstrap_db()
    port = os.getenv("PORT", "8501")
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.address",
        "0.0.0.0",
        "--server.port",
        port,
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
