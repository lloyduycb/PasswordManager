from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import sqlite3
import bcrypt  # also missing
from ui.master_password import MasterPasswordWindow
from ui.home import HomeWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 200, 350, 200)

        layout = QVBoxLayout()

        self.email_or_user = QLineEdit()
        self.email_or_user.setPlaceholderText("Email or Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)

        layout.addWidget(QLabel("Sign in"))
        layout.addWidget(self.email_or_user)
        layout.addWidget(self.password)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def login(self):
        user_input = self.email_or_user.text()
        password = self.password.text()

        if not user_input or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return

        try:
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

            # Keep a reference to the master window
            self.master_window = MasterPasswordWindow(db_username)
            self.master_window.show()
            
            # Don't close the login window immediately
            # self.close()  # Remove this line initially for testing

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            print(f"Error during login: {e}")  # Check console for this

    def open_home(self):
        self.home = HomeWindow()
        self.home.show()
        self.close()
