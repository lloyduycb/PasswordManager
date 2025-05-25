from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import pyotp
import qrcode
from io import BytesIO

class OTPSetupWindow(QWidget):
    def __init__(self, username, otp_secret, callback=None):
        super().__init__()
        self.username = username
        self.otp_secret = otp_secret
        self.callback = callback  # ✅ New argument for post-Done logic

        self.setWindowTitle("Set Up Two-Factor Authentication")
        self.setGeometry(550, 250, 360, 460)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #EFE9E1;
                font-family: 'Segoe UI', sans-serif;
                color: #222052;
            }
            QLabel {
                font-size: 14px;
                font-weight: normal;
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
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        title = QLabel("Scan this QR code in your Authenticator app:")
        title.setWordWrap(True)
        title.setStyleSheet("font-weight: bold;")
        layout.addWidget(title)

        # Generate TOTP URI and QR Code
        totp_uri = pyotp.totp.TOTP(self.otp_secret).provisioning_uri(
            name=self.username,
            issuer_name="Vault Password Manager"
        )

        qr = qrcode.make(totp_uri)
        buffer = BytesIO()
        qr.save(buffer, format="PNG")
        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        qr_label = QLabel()
        qr_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(qr_label)

        # Manual Key Display
        manual_label = QLabel("Or enter this key manually:")
        manual_label.setStyleSheet("color: #444;")
        manual_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(manual_label)

        key_display = QLabel(f"<b>{self.otp_secret}</b>")
        key_display.setStyleSheet("background-color: #F6EFD9; padding: 8px; border-radius: 6px; font-size: 13px;")
        key_display.setAlignment(Qt.AlignCenter)
        layout.addWidget(key_display)

        # Done button
        done_btn = QPushButton("Done")
        done_btn.clicked.connect(self.finish)  # ✅ Calls method instead of just close
        layout.addWidget(done_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def finish(self):
        self.close()
        if self.callback:
            self.callback()  # ✅ Launch master password setup
