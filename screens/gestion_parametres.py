
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ParametresWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("⚙️ Écran des paramètres en cours de développement"))
        self.setLayout(layout)