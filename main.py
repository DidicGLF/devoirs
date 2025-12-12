# main.py

import sys
from PySide6.QtWidgets import QApplication
from screens.accueil import AccueilWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccueilWindow()
    window.show()
    sys.exit(app.exec())