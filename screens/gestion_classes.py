
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel

class ClassesWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("🚧 Gestion des classes en cours de développement"))
        self.setLayout(layout)