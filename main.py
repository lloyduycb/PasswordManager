import sys
from PyQt5.QtWidgets import QApplication
from core.db import init_db
from ui.start import StartPage

if __name__ == "__main__":
    try:
        init_db()
        app = QApplication(sys.argv)
        window = StartPage()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)
