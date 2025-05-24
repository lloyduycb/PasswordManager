from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import pyotp
import sqlite3

class OTPVerifyWindow(QWidget):
    def __init__(self, username, on_success):
        super().__init__()
        self.username = username
        self.on_success = on_success
        self.setWindowTitle("Enter OTP")
        self.setGeometry(550, 250, 300, 150)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter the 6-digit code from your Authenticator app:"))

        self.otp_input = QLineEdit()
        self.otp_input.setMaxLength(6)
        self.otp_input.setPlaceholderText("123456")
        layout.addWidget(self.otp_input)

        verify_btn = QPushButton("Verify")
        verify_btn.clicked.connect(self.verify_otp)
        layout.addWidget(verify_btn)

        self.setLayout(layout)

    def verify_otp(self):
        entered_code = self.otp_input.text().strip()

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT otp_secret FROM users WHERE username = ?", (self.username,))
        result = c.fetchone()
        conn.close()

        if result:
            otp_secret = result[0]
            totp = pyotp.TOTP(otp_secret)
            if totp.verify(entered_code):
                QMessageBox.information(self, "Success", "OTP Verified!")
                self.close()
                self.on_success()
            else:
                QMessageBox.warning(self, "Error", "Invalid OTP. Try again.")
        else:
            QMessageBox.critical(self, "Error", "User not found.")
