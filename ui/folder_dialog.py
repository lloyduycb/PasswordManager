from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QDialog
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class FolderDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New Folder")
        self.setFixedSize(300, 160)
        self.folder_name = None

        self.setStyleSheet("""
            QDialog {
                background-color: #EFE9E1;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #222052;
            }
            QLineEdit {
                background-color: #DDD7CE;
                border-radius: 8px;
                padding: 6px;
                font-size: 13px;
                color: #222052;
            }
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                border-radius: 10px;
                padding: 6px 12px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel("Folder name:")
        self.name_input = QLineEdit()

        layout.addWidget(label)
        layout.addWidget(self.name_input)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancel")

        ok_btn.clicked.connect(self.accept_dialog)
        cancel_btn.clicked.connect(self.reject)

        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)

        layout.addLayout(btn_row)
        self.setLayout(layout)

    def accept_dialog(self):
        text = self.name_input.text().strip()
        if text:
            self.folder_name = text
            self.accept()
