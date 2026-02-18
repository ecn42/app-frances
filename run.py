from __future__ import annotations

import os
import subprocess
import sys


def main() -> int:
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
    ]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
