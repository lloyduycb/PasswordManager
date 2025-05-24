from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
import sqlite3
import bcrypt 

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
        self.login_btn.setDefault(True)
        self.login_btn.setAutoDefault(True)
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
            else:
                self.open_master_window()

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

