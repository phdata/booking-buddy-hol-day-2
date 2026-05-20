import subprocess
import sys
from pathlib import Path

services = [
    "booking-service",
    "loyalty-service",
    "fleet-service",
    "notifications-service",
]

for service in services:
    print(f"=== {service} ===")
    for db in Path(service).glob("*.db"):
        if not db.name.startswith("test_"):
            db.unlink()
    subprocess.run(["uv", "sync"], cwd=service, check=True)
    subprocess.run(["uv", "run", "python", "seed.py"], cwd=service, check=True)
