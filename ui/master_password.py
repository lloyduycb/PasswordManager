# master_password.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QFrame
from PyQt5.QtCore import Qt, QTimer

import sqlite3
import bcrypt


class MasterPasswordWindow(QWidget):
    def __init__(self, username, from_register=False):
        super().__init__()
        self.username = username
        self.from_register = from_register

        self.setWindowTitle("Master Password")
        self.setGeometry(500, 200, 300, 200)  # Slightly taller for better layout
        
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
        
        self.label = QLabel("Enter your Master Password")
        self.label.setAlignment(Qt.AlignCenter)

        self.input = QLineEdit()
        self.input.setPlaceholderText("Master Password")
        self.input.setEchoMode(QLineEdit.Password)
        
        self.submit = QPushButton("Continue")
        self.submit.setDefault(True)
        self.submit.setAutoDefault(True)
        self.submit.clicked.connect(self.verify_master_password)

        card_layout.addWidget(self.label)
        card_layout.addWidget(self.input)
        card_layout.addWidget(self.submit)

        outer_layout.addStretch()
        outer_layout.addWidget(card, alignment=Qt.AlignCenter)
        outer_layout.addStretch()

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
                color: #222052;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
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
                box = QMessageBox(self)
                box.setIcon(QMessageBox.Warning)
                box.setWindowTitle("Weak Password")
                box.setText('<span style="color:#EFE9E1;">Master password must be at least 8 characters.</span>')
                box.setStyleSheet("""
                    QMessageBox {
                        background-color: #222052;
                    }
                    QLabel {
                        color: #EFE9E1;
                    }
                    QPushButton {
                        color: #EFE9E1;
                        background-color: #222052;
                        border: none;
                        padding: 5px 12px;
                    }
                    QPushButton:hover {
                        background-color: #000000;
                    }
                """)
                box.exec_()
                return

                
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            conn = sqlite3.connect("vault.db")
            c = conn.cursor()
            c.execute("INSERT INTO master_password (username, password_hash) VALUES (?, ?)", (self.username, hashed))
            conn.commit()
            conn.close()
            


            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle("Success")
            msg_box.setText("Master password set.")
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #222052;
                    color: #EFE9E1;
                    font-family: 'Segoe UI';
                }
                QLabel {
                    color: #EFE9E1;
                }
                QPushButton {
                    color: #EFE9E1;
                    background-color: #222052;
                    border: none;
                    padding: 5px 12px;
                }
                QPushButton:hover {
                    background-color: #000000;
                }
            """)

            # Show and wait for user to press OK
            msg_box.exec_()

            # Then proceed
            if self.from_register:
                from ui.login import LoginWindow
                self.login_window = LoginWindow()
                self.login_window.show()
            else:
                self.open_home()

            self.close()



    def open_home(self):
        from ui.home import HomeWindow
        self.home = HomeWindow(self.username)
        self.home.show()
        self.close()