from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QFrame
from PyQt5.QtCore import Qt

class StartPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.setGeometry(600, 300, 400, 300)
        self.setStyleSheet("""
            QWidget {
                background-color: #222052;
                font-family: 'Segoe UI', sans-serif;
            }
        """)


        outer_layout = QVBoxLayout()
        outer_layout.setAlignment(Qt.AlignCenter)

        # Card frame
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #EFE9E1;
                border-radius: 20px;
                padding: 40px;
            }
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)

        # Title
        title = QLabel("Welcome")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #222052;")
        card_layout.addWidget(title)

        # Log In button
        login_btn = QPushButton("Log In")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)
        login_btn.clicked.connect(self.open_login)
        card_layout.addWidget(login_btn)

        # Create Account button
        register_btn = QPushButton("Create Account")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #222052;
                color: #EFE9E1;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #000000;
            }
        """)
        register_btn.clicked.connect(self.open_register)
        card_layout.addWidget(register_btn)

        outer_layout.addWidget(card)
        self.setLayout(outer_layout)

    def open_login(self):
        from ui.login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def open_register(self):
        from ui.register import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()
