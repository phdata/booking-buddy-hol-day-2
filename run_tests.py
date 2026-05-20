import subprocess
import sys

services = [
    "booking-service",
    "loyalty-service",
    "fleet-service",
    "notifications-service",
]

overall = 0
for service in services:
    print(f"=== {service} ===")
    result = subprocess.run(["uv", "run", "pytest", *sys.argv[1:]], cwd=service)
    if result.returncode != 0:
        overall = 1

sys.exit(overall)
