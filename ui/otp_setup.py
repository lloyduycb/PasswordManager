from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtGui import QPixmap
import pyotp
import qrcode
from io import BytesIO

class OTPSetupWindow(QWidget):
    def __init__(self, username, otp_secret):
        super().__init__()
        self.username = username
        self.otp_secret = otp_secret
        self.setWindowTitle("Set Up Two-Factor Authentication")
        self.setGeometry(550, 250, 300, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Scan this QR code in your Authenticator app:"))

        # Generate URI
        totp_uri = pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.username,
            issuer_name="Vault Password Manager"
        )

        # Generate QR Code
        qr = qrcode.make(totp_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        qr_label = QLabel()
        qr_label.setPixmap(pixmap)
        qr_label.setScaledContents(True)
        qr_label.setFixedSize(200, 200)
        layout.addWidget(qr_label)

        # Manual code
        layout.addWidget(QLabel("Or enter this key manually:"))
        layout.addWidget(QLabel(f"<b>{self.otp_secret}</b>"))

        ok_btn = QPushButton("Done")
        ok_btn.clicked.connect(self.close)
        layout.addWidget(ok_btn)

        self.setLayout(layout)
