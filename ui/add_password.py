from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QTextEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QMessageBox, QDateEdit, QFrame, QGridLayout, QApplication
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sqlite3
from core.crypto import encrypt_password
from core.db import insert_password_entry, fetch_folders

class AddPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Password")
        self.setGeometry(580, 250, 420, 520)
        self.init_ui()

    def init_ui(self):
        def emoji_button(char: str) -> QPushButton:
            btn = QPushButton(char)
            font = QFont("Segoe UI Emoji")
            font.setPixelSize(18)
            btn.setFont(font)
            btn.setFixedSize(32, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    min-width: 28px;
                    min-height: 28px;
                }
                QPushButton:hover {
                    color: #000000;
                }
            """)
            return btn




        self.setStyleSheet("""
            QWidget {
                background-color: #EFE9E1;
                font-family: 'Segoe UI', sans-serif;
                color: #222052;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
            }
            QLineEdit, QTextEdit {
                background-color: #DDD7CE;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
            }
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                border-radius: 12px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)

        grid = QGridLayout()
        grid.setVerticalSpacing(12)

        # Fields
        self.name_input = QLineEdit()
        grid.addWidget(QLabel("Name"), 0, 0)
        grid.addWidget(self.name_input, 0, 1)

        self.email_input = QLineEdit()
        email_row = QHBoxLayout()
        email_row.addWidget(self.email_input)
        copy_email_btn = emoji_button("📋")
        copy_email_btn.clicked.connect(lambda: self.copy_to_clipboard(self.email_input.text()))
        email_row.addWidget(copy_email_btn)
        email_frame = QFrame()
        email_frame.setLayout(email_row)
        grid.addWidget(QLabel("Email"), 1, 0)
        grid.addWidget(email_frame, 1, 1)

        self.url_input = QLineEdit()
        grid.addWidget(QLabel("URL"), 2, 0)
        grid.addWidget(self.url_input, 2, 1)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        pw_row = QHBoxLayout()
        pw_row.addWidget(self.password_input)
        copy_pw_btn = emoji_button("📋")
        copy_pw_btn.clicked.connect(lambda: self.copy_to_clipboard(self.password_input.text()))
        toggle_pw_btn = emoji_button("👁")
        toggle_pw_btn.setCheckable(True)
        toggle_pw_btn.toggled.connect(self.toggle_visibility)
        pw_row.addWidget(copy_pw_btn)
        pw_row.addWidget(toggle_pw_btn)
        pw_frame = QFrame()
        pw_frame.setLayout(pw_row)
        grid.addWidget(QLabel("Password"), 3, 0)
        grid.addWidget(pw_frame, 3, 1)

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes")
        grid.addWidget(QLabel("Notes"), 4, 0)
        grid.addWidget(self.notes_input, 4, 1)

        self.expiry_input = QDateEdit()
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setDisplayFormat("yyyy-MM-dd")
        grid.addWidget(QLabel("Expiry Date"), 5, 0)
        grid.addWidget(self.expiry_input, 5, 1)

        layout.addLayout(grid)

        # Save button
        save_btn = QPushButton("Save Password")
        save_btn.clicked.connect(self.save_entry)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def toggle_visibility(self, checked):
        self.password_input.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def save_entry(self):
        name = self.name_input.text().strip()
        email = self.email_input.text().strip()
        url = self.url_input.text().strip()
        password = encrypt_password(self.password_input.text().strip())
        notes = self.notes_input.toPlainText().strip()
        expiry_date = self.expiry_input.date().toString("yyyy-MM-dd")

        if not name:
            QMessageBox.warning(self, "Missing", "Name field is required.")
            return

        conn = sqlite3.connect("vault.db")
        c = conn.cursor()
        c.execute("""
            INSERT INTO passwords (name, email, url, password, notes, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (name, email, url, password, notes, expiry_date))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Saved", f"Password for '{name}' saved.")
        self.close()
