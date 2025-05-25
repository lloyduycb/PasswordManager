from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame
from PyQt5.QtCore import Qt
from core import db
import bcrypt
import random
import datetime
import sqlite3
import pyotp

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Account")
        self.setGeometry(500, 200, 350, 250)

        outer_layout = QVBoxLayout(self)

        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #EFE9E1;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        card_layout = QVBoxLayout(card)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setDefault(True)
        self.signup_btn.setAutoDefault(True)
        # self.signup_btn.clicked.connect(self.register)

        card_layout.addWidget(QLabel("Create Account"))
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.email)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.signup_btn)

        outer_layout.addWidget(card, alignment=Qt.AlignCenter)
        
        self.setLayout(outer_layout)
        self.setStyleSheet("""
            QWidget {
                background-color: #222052;
                font-family: 'Segoe UI', sans-serif;
                color: #000000;
            }

            QLineEdit {
                background-color: #EEE5D3;
                border: 1px solid #C3B4A6;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }

            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #000000;
            }

            QLabel {
                color: #EFE9E1;
                font-size: 16px;
                font-weight: bold;
            }
        """)


        self.setLayout(outer_layout)

    def register(self):
        uname = self.username.text().strip()
        email = self.email.text().strip()
        pwd = self.password.text()

        if not uname or not email or not pwd:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            hashed_pwd = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())

            otp_secret = pyotp.random_base32()

            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (username, email, password, is_verified, otp_secret) 
                VALUES (?, ?, ?, 1, ?)
            """, (uname, email, hashed_pwd, otp_secret))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Account created successfully!")

            from ui.otp_setup import OTPSetupWindow
            self.otp_window = OTPSetupWindow(uname, otp_secret)
            self.otp_window.show()


            # ✅ Go to master password setup
            from ui.master_password import MasterPasswordWindow
            self.master_window = MasterPasswordWindow(uname, from_register=True)
            self.master_window.show()
            self.close()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username or email already exists.")

        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{str(e)}")
