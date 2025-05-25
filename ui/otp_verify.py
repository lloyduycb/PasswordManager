from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
from core.emailer import send_otp_email
from ui.email_otp_verify import EmailOTPVerifyWindow
import sqlite3, random, datetime
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
        from PyQt5.QtWidgets import QFrame, QHBoxLayout
        from PyQt5.QtGui import QFont
        from PyQt5.QtCore import Qt

        self.setStyleSheet("background-color: #222052;")

        outer_layout = QVBoxLayout(self)
        outer_layout.setAlignment(Qt.AlignCenter)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #EFE9E1;
                border-radius: 20px;
                padding: 30px;
                font-family: 'Segoe UI', sans-serif;           
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Authenticator")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #222052;")
        card_layout.addWidget(title)

        prompt = QLabel("Enter the 6-digit code from your app:")
        prompt.setAlignment(Qt.AlignCenter)
        prompt.setStyleSheet("color: #444; font-size: 13px;")
        card_layout.addWidget(prompt)

        self.otp_input = QLineEdit()
        self.otp_input.setMaxLength(6)
        self.otp_input.setPlaceholderText("●●●●●●")
        self.otp_input.setAlignment(Qt.AlignCenter)
        self.otp_input.setStyleSheet("""
            QLineEdit {
                background-color: #FFF;
                border: 2px solid #C3B4A6;
                border-radius: 12px;
                font-size: 20px;
                padding: 8px;
                letter-spacing: 10px;
            }
        """)
        card_layout.addWidget(self.otp_input)

        verify_btn = QPushButton("Verify")
        verify_btn.setStyleSheet("""
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                font-weight: bold;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)
        verify_btn.clicked.connect(self.verify_otp)
        card_layout.addWidget(verify_btn)

        use_email_btn = QPushButton("Use Email OTP Instead")
        use_email_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #222052;
                font-size: 12px;
                text-decoration: underline;
                padding: 0px;
                border: none;
            }
        """)
        use_email_btn.clicked.connect(self.use_email_otp)
        card_layout.addWidget(use_email_btn)

        outer_layout.addWidget(card)


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

    def use_email_otp(self):
        otp_code = str(random.randint(100000, 999999))
        otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT email FROM users WHERE username = ?", (self.username,))
        row = c.fetchone()

        if not row or not row[0]:
            QMessageBox.critical(self, "Error", "No email found for this user.")
            conn.close()
            return

        email = row[0]

        # Update DB with new email OTP
        c.execute("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE username = ?", 
                (otp_code, otp_expiry, self.username))
        conn.commit()
        conn.close()

        send_otp_email(email, otp_code)
        # Open Email OTP Window
        self.email_otp_window = EmailOTPVerifyWindow(self.username, self.on_success)
        self.email_otp_window.show()
        self.close()
