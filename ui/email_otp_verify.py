from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer
import sqlite3
import datetime

class EmailOTPVerifyWindow(QWidget):
    def __init__(self, username, on_success_callback):
        super().__init__()
        self.username = username
        self.on_success = on_success_callback

        self.setWindowTitle("Email OTP Verification")
        self.setGeometry(550, 250, 300, 150)

        layout = QVBoxLayout()
        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter OTP from email")

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.clicked.connect(self.verify_otp)

        layout.addWidget(QLabel("We've sent a 6-digit OTP to your email."))
        layout.addWidget(self.otp_input)
        layout.addWidget(self.verify_btn)

        self.setLayout(layout)

        self.resend_btn = QPushButton("Resend OTP")
        self.resend_btn.clicked.connect(self.resend_otp)
        layout.addWidget(self.resend_btn)

        self.resend_btn.setEnabled(False)
        self.cooldown_timer = QTimer()
        self.cooldown_timer.timeout.connect(self.update_resend_cooldown)
        self.cooldown_seconds = 30  # 30-second cooldown
        self.cooldown_timer.start(1000)


    def verify_otp(self):
        entered_code = self.otp_input.text().strip()

        if not entered_code:
            QMessageBox.warning(self, "Missing OTP", "Please enter the OTP.")
            return

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT otp_code, otp_expiry FROM users WHERE username = ?", (self.username,))
        row = c.fetchone()
        conn.close()

        if not row or not row[0]:
            QMessageBox.critical(self, "Error", "No OTP was found for your account.")
            return

        stored_code, expiry_str = row
        expiry = datetime.datetime.fromisoformat(expiry_str) if expiry_str else None

        now = datetime.datetime.now()
        if entered_code != stored_code:
            QMessageBox.warning(self, "Invalid OTP", "The OTP code is incorrect.")
        elif expiry and now > expiry:
            QMessageBox.warning(self, "Expired", "Your OTP has expired.")
        else:
            self.clear_otp()
            self.close()
            self.on_success()

    def clear_otp(self):
        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("UPDATE users SET otp_code = NULL, otp_expiry = NULL WHERE username = ?", (self.username,))
        conn.commit()
        conn.close()

    def update_resend_cooldown(self):
        self.cooldown_seconds -= 1
        if self.cooldown_seconds <= 0:
            self.resend_btn.setText("Resend OTP")
            self.resend_btn.setEnabled(True)
            self.cooldown_timer.stop()
        else:
            self.resend_btn.setText(f"Resend OTP ({self.cooldown_seconds})")

    def resend_otp(self):
        from core.emailer import send_otp_email
        import random, datetime

        otp_code = str(random.randint(100000, 999999))
        otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE username = ?", 
                (otp_code, otp_expiry, self.username))
        c.execute("SELECT email FROM users WHERE username = ?", (self.username,))
        email = c.fetchone()[0]
        conn.commit()
        conn.close()

        send_otp_email(email, otp_code)
        QMessageBox.information(self, "Resent", f"A new OTP was sent to {email}.")

        self.resend_btn.setEnabled(False)
        self.cooldown_seconds = 30
        self.cooldown_timer.start(1000)
