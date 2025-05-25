from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QApplication, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import bcrypt, sqlite3, pyotp

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Account")
        self.setGeometry(500, 200, 350, 350)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)
        layout.setSpacing(15)

        # Title
        title = QLabel("Sign Up")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #222052;")
        layout.addWidget(title)

        # Username
        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        layout.addWidget(self.username)

        # Email
        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")
        layout.addWidget(self.email)

        # Password with eye toggle
        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(32)


        toggle_btn = QPushButton("👁")
        toggle_btn.setCheckable(True)
        toggle_btn.setFont(QFont("Segoe UI Emoji", 12))
        toggle_btn.setMinimumSize(32, 32)
        toggle_btn.setMaximumSize(32, 32)
        toggle_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                margin: 0px;
            }
            QPushButton:hover {
                background-color: #DDD7CE;
                border-radius: 4px;
            }
        """)
        toggle_btn.toggled.connect(self.toggle_visibility)

        pw_row = QHBoxLayout()
        pw_row.setContentsMargins(0, 0, 0, 0)
        pw_row.setSpacing(4)
        pw_row.addWidget(self.password)
        pw_row.addWidget(toggle_btn)

        pw_widget = QWidget()
        pw_widget.setLayout(pw_row)
        layout.addWidget(pw_widget)

        # Sign Up button
        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.setDefault(True)
        self.signup_btn.setAutoDefault(True)
        self.signup_btn.clicked.connect(self.register)
        layout.addWidget(self.signup_btn)

        # Link to login
        login_link = QLabel('<a href="#">Already have an account?</a>')
        login_link.setAlignment(Qt.AlignCenter)
        login_link.setStyleSheet("color: #666; font-size: 12px;")
        login_link.setOpenExternalLinks(False)
        login_link.linkActivated.connect(self.go_to_login)
        layout.addWidget(login_link)

        self.setStyleSheet("""
            QWidget {
                background-color: #EFE9E1;
                font-family: 'Segoe UI', sans-serif;
            }
            QLineEdit {
                background-color: #EEE5D3;
                border: 1px solid #C3B4A6;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
                color: #222052;
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
                color: #222052;
                font-size: 14px;
            }
        """)

    def toggle_visibility(self, checked):
        self.password.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

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
            self.otp_window = OTPSetupWindow(uname, otp_secret, callback=self.launch_master_setup)
            self.otp_window.show()



        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username or email already exists.")
        except Exception as e:
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Unexpected error:\n{str(e)}")

    def go_to_login(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()
    
    def launch_master_setup(self):
        from ui.master_password import MasterPasswordWindow
        self.master_window = MasterPasswordWindow(self.username, from_register=True)
        self.master_window.show()
        self.close()

