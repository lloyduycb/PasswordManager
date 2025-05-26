import subprocess
import sys

def install(package):
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        capture_output=True,
        text=True
    )

    if "Requirement already satisfied" in result.stdout:
        print(f"[=] Already installed: {package}")
    elif result.returncode == 0:
        print(f"[✓] Installed: {package}")
    else:
        print(f"[X] Failed to install: {package}")
        print(result.stderr.strip())  # Optional: show pip error message

packages = [
    "pyqt5",
    "bcrypt",
    "pyotp",
    "qrcode",
    "pillow"  # Needed by qrcode for image handling
]

for pkg in packages:
    install(pkg)
