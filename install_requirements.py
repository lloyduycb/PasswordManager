import subprocess
import sys

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[✓] Installed {package}")
    except Exception:
        print(f"[X] Failed to install {package}")

packages = [
    "pyqt5",
    "bcrypt",
    "pyotp",
    "qrcode",
    "pillow"  # Needed by qrcode for image handling
]

for pkg in packages:
    install(pkg)
