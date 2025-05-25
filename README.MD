# 🔐 Vault Password Manager

Vault is a secure, minimalist password manager built with Python and PyQt5. It offers a clean UI for managing login credentials, folders, 2FA setup, and password generation — all stored locally using SQLite.

---

## 📦 Features

- Master password protection
- Secure local storage using SQLite and `bcrypt` hashing
- Password vault with folder organisation
- Recently used and favourite entries
- Two-factor authentication (OTP) setup via QR code
- Password generator with strength indicator
- Expiry tracking and notifications
- Auto-lock on inactivity

---

## 🛠️ Built With

- **Python 3.12+**
- **PyQt5** – GUI framework
- **SQLite** – local database
- **bcrypt** – for hashing passwords securely
- **pyotp** – for generating OTP secrets
- **qrcode / Pillow** – for generating scannable QR codes

---

## ⚙️ Setup Instructions

1. **Clone this repo**:
   ```bash
   git clone https://github.com/yourname/vault-password-manager.git
   cd vault-password-manager

2. Install requirements:
   ```bash
   python install_requirements.py

3. Run the app:
   ```bash
   python main.py