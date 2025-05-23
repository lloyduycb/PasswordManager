from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import sqlite3
import datetime
from ui.master_password import MasterPasswordWindow

class EmailVerificationWindow(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Email Verification")
        self.setGeometry(500, 200, 300, 200)

        layout = QVBoxLayout()

        self.label = QLabel("Enter the 6-digit code sent to your email:")
        self.code_input = QLineEdit()
        self.code_input.setMaxLength(6)

        self.verify_btn = QPushButton("Verify")
        self.verify_btn.clicked.connect(self.verify_code)

        layout.addWidget(self.label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.verify_btn)

        self.setLayout(layout)

    def verify_code(self):
        code_entered = self.code_input.text()

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT verification_code, code_expiry FROM users WHERE username = ?", (self.username,))
        row = c.fetchone()

        if not row:
            QMessageBox.warning(self, "Error", "User not found.")
            return

        actual_code, expiry = row
        if datetime.datetime.now() > datetime.datetime.fromisoformat(expiry):
            QMessageBox.warning(self, "Expired", "Verification code expired.")
        elif code_entered == actual_code:
            c.execute("UPDATE users SET is_verified = 1 WHERE username = ?", (self.username,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Verified", "Email verified successfully!")
            self.open_master_password()
        else:
            QMessageBox.warning(self, "Incorrect", "Invalid verification code.")

    def open_master_password(self):
        self.master_window = MasterPasswordWindow(self.username)
        self.master_window.show()
        self.close()
