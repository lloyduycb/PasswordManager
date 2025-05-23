from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from ui.login import LoginWindow
from ui.register import RegisterWindow

class StartPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.setGeometry(500, 200, 300, 150)

        layout = QVBoxLayout()

        self.login_btn = QPushButton("Log In")
        self.login_btn.clicked.connect(self.open_login)

        self.signup_btn = QPushButton("Create Account")
        self.signup_btn.clicked.connect(self.open_register)

        layout.addWidget(self.login_btn)
        layout.addWidget(self.signup_btn)

        self.setLayout(layout)

    def open_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def open_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()
