# main.py

import sys
import os
import platform

# Correction pour Linux : désactiver GTK pour éviter l'erreur du ColorChooser
if platform.system() == 'Linux':
    os.environ['QT_QPA_PLATFORMTHEME'] = ''

from PySide6.QtWidgets import QApplication
from screens.accueil import AccueilWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccueilWindow()
    window.show()
    sys.exit(app.exec())