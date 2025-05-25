from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame
from PyQt5.QtCore import Qt
import sqlite3
import bcrypt 

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 200, 350, 200)

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


        self.email_or_user = QLineEdit()
        self.email_or_user.setPlaceholderText("Email or Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.setDefault(True)
        self.login_btn.setAutoDefault(True)
        self.login_btn.clicked.connect(self.login)

        card_layout.addWidget(QLabel("Sign in"))
        card_layout.addWidget(self.email_or_user)
        card_layout.addWidget(self.password)
        card_layout.addWidget(self.login_btn)

        outer_layout.addWidget(card, alignment=Qt.AlignCenter)
        card.setFixedSize(280, 220)  # or whatever size fits your form content

        
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

    def login(self):
        user_input = self.email_or_user.text()
        password = self.password.text()

        if not user_input or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        try:
            # Get user by username or email
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("""
                SELECT username, password FROM users
                WHERE username = ? OR email = ?
            """, (user_input, user_input))
            user = c.fetchone()
            conn.close()

            if not user:
                QMessageBox.warning(self, "Error", "User not found.")
                return

            db_username, db_password = user

            if not bcrypt.checkpw(password.encode(), db_password):
                QMessageBox.warning(self, "Error", "Incorrect password.")
                return

            # ✅ Store username for later
            self.logged_in_username = db_username

            # ✅ Check for OTP
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("SELECT otp_secret FROM users WHERE username = ?", (db_username,))
            row = c.fetchone()
            conn.close()

            if row and row[0]:  # otp_secret exists
                from ui.otp_verify import OTPVerifyWindow
                self.otp_window = OTPVerifyWindow(db_username, self.open_master_window)
                self.otp_window.show()
                self.close()
            else:
                import random, datetime
                from core.emailer import send_otp_email

                # Generate OTP code and expiry
                otp_code = str(random.randint(100000, 999999))
                otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=5)

                # Store OTP in DB
                conn = sqlite3.connect("vault.db")
                c = conn.cursor()
                c.execute("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE username = ?", 
                        (otp_code, otp_expiry, db_username))
                conn.commit()
                c.execute("SELECT email FROM users WHERE username = ?", (db_username,))
                email_row = c.fetchone()
                conn.close()

                if email_row and email_row[0]:
                    user_email = email_row[0]
                    send_otp_email(user_email, otp_code)

                    # Open Email OTP verification window
                    from ui.email_otp_verify import EmailOTPVerifyWindow
                    self.email_otp_window = EmailOTPVerifyWindow(db_username, self.open_master_window)
                    self.email_otp_window.show()
                    self.close()
                else:
                    QMessageBox.critical(self, "Error", "No email found for user.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            print(f"Error during login: {e}")


    def open_home(self):
        from ui.home import HomeWindow
        self.home = HomeWindow()
        self.home.show()
        self.close()

    def open_master_window(self):
        from ui.master_password import MasterPasswordWindow
        self.master_window = MasterPasswordWindow(self.logged_in_username)
        self.master_window.show()
        self.close()

