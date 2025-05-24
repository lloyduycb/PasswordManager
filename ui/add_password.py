from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QTextEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QComboBox
from core.db import insert_password_entry
from core.crypto import encrypt_password, decrypt_password


class AddPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Password")
        self.setGeometry(550, 250, 400, 400)

        layout = QVBoxLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Name")

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")

        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Notes...")

        self.folder_dropdown = QComboBox()
        self.folder_dropdown.addItem("None")
        self.folders = fetch_folders()
        for _, name in self.folders:
            self.folder_dropdown.addItem(name)

        layout.addWidget(QLabel("Folder"))
        layout.addWidget(self.folder_dropdown)


        self.submit_btn = QPushButton("Save")
        self.submit_btn.clicked.connect(self.save_entry)

        layout.addWidget(QLabel("Create Password"))
        layout.addWidget(self.name_input)
        layout.addWidget(self.email_input)
        layout.addWidget(self.url_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.notes_input)
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def save_entry(self):
        from core.db import insert_password_entry
        from core.crypto import encrypt_password  # if using encryption

        name = self.name_input.text()
        email = self.email_input.text()
        url = self.url_input.text()
        password = encrypt_password(self.password_input.text())
        notes = self.notes_input.toPlainText()

        # Get folder ID
        folder_name = self.folder_dropdown.currentText()
        folder_id = None
        if folder_name != "None":
            folder_id = next((fid for fid, name in self.folders if name == folder_name), None)

        if not name or not password:
            QMessageBox.warning(self, "Error", "Name and Password are required.")
            return

        insert_password_entry(name, email, url, password, notes, folder_id)
        QMessageBox.information(self, "Saved", "Password entry added.")
        self.close()

