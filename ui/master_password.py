# master_password.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
import sqlite3
import bcrypt


class MasterPasswordWindow(QWidget):
    def __init__(self, username, from_register=False):
        super().__init__()
        self.username = username
        self.from_register = from_register

        self.setWindowTitle("Master Password")
        self.setGeometry(500, 200, 300, 200)  # Slightly taller for better layout
        
        layout = QVBoxLayout()
        
        self.label = QLabel("Enter your Master Password")
        self.input = QLineEdit()
        self.input.setPlaceholderText("Master Password")
        self.input.setEchoMode(QLineEdit.Password)
        
        self.submit = QPushButton("Continue")
        self.submit.setDefault(True)
        self.submit.setAutoDefault(True)
        self.submit.clicked.connect(self.verify_master_password)
        
        layout.addWidget(self.label)
        layout.addWidget(self.input)
        layout.addWidget(self.submit)
        self.setLayout(layout)
        
        # Check if master password exists for this user
        self.master_exists = self.check_master_exists()
        
        if not self.master_exists:
            self.label.setText("Create a Master Password")
            self.input.setPlaceholderText("Create Master Password")

    def check_master_exists(self):
        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("SELECT password_hash FROM master_password WHERE username = ?", (self.username,))
        row = c.fetchone()
        conn.close()
        return bool(row)

    def verify_master_password(self):
        password = self.input.text()
        
        if not password:
            QMessageBox.warning(self, "Error", "Master password cannot be empty.")
            return
            
        if self.master_exists:
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("SELECT password_hash FROM master_password WHERE username = ?", (self.username,))
            row = c.fetchone()
            conn.close()

            if row:
                hashed_pw = row[0]

                # Ensure hashed_pw is bytes
                if isinstance(hashed_pw, str):
                    hashed_pw = hashed_pw.encode('utf-8')

                if bcrypt.checkpw(password.encode(), hashed_pw):
                    self.open_home()
                    return

            QMessageBox.warning(self, "Error", "Incorrect master password.")

        else:
            # Create new master password
            if len(password) < 6:
                QMessageBox.warning(self, "Weak Password", "Master password must be at least 8 characters.")
                return
                
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("INSERT INTO master_password (username, password_hash) VALUES (?, ?)", (self.username, hashed))
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Success", "Master password set.")
            
            if self.from_register:
                from ui.login import LoginWindow
                self.login_window = LoginWindow()
                self.login_window.show()
                self.close()
            else:
                self.open_home()

            self.close()

    def open_home(self):
        from ui.home import HomeWindow
        self.home = HomeWindow(self.username)
        self.home.show()
        self.close()