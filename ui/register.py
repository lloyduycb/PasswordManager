from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from core import db
from ui.verify_email import EmailVerificationWindow
from ui.login import LoginWindow  
import random
import datetime
import sqlite3

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Account")
        self.setGeometry(500, 200, 350, 250)

        layout = QVBoxLayout()

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.signup_btn = QPushButton("Sign Up")
        self.signup_btn.clicked.connect(self.register)

        layout.addWidget(QLabel("Create Account"))
        layout.addWidget(self.username)
        layout.addWidget(self.email)
        layout.addWidget(self.password)
        layout.addWidget(self.signup_btn)

        self.setLayout(layout)

    def register(self):
        uname = self.username.text()
        email = self.email.text()
        pwd = self.password.text()

        if not uname or not email or not pwd:
            QMessageBox.warning(self, "Error", "All fields are required.")
            return

        try:
            # Hash the user's password with bcrypt before storing
            hashed_pwd = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt())
            
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("""
                INSERT INTO users (username, email, password, is_verified) 
                VALUES (?, ?, ?, 1)
            """, (uname, email, hashed_pwd))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Account created successfully!")
            
            # Redirect to login page instead of master password
            self.login_window = LoginWindow()
            self.login_window.show()
            self.close()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username or email already exists.")
