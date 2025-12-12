# screens/gestion_devoirs.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QDateEdit, QComboBox,
    QLineEdit, QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, QDate, QTimer, QEvent
from PySide6.QtGui import QColor, QFont, QPalette

import sys
import os

# Ajouter le dossier parent au chemin pour importer utils/gestion.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.gestion import charger_classes, charger_devoirs  # Import des fonctions

class DevoirsWidget(QWidget):
    """Écran de gestion des devoirs — partie saisie + liste des devoirs (design personnalisé)"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.classes_list = []  # Stockage des instances de Classe
        self.devoirs_list = []  # Stockage des instances de Devoir
        self.init_ui()

    def init_ui(self):
        # Layout principal (vertical)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 0, 50, 50)  # pas de marge en haut (pas de titre)

        # Ligne de saisie (horizontal)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        # 1. Classe (QComboBox) — au début de la ligne, comme demandé
        self.combo_classe = QComboBox()
        self.combo_classe.setFixedWidth(120)
        input_layout.addWidget(self.combo_classe)

        # 2. Sélecteur de date
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)  # affiche un calendrier au clic
        self.date_edit.setDate(QDate.currentDate())  # date par défaut = aujourd'hui
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setFixedWidth(120)
        input_layout.addWidget(self.date_edit)

        # 3. Statut (ComboBox)
        self.combo_statut = QComboBox()
        self.combo_statut.addItems(["À faire", "En cours", "Terminé"])
        self.combo_statut.setFixedWidth(120)
        input_layout.addWidget(self.combo_statut)

        # 4. Contenu (QLineEdit)
        self.line_content = QLineEdit()
        self.line_content.setPlaceholderText("Description du devoir...")
        self.line_content.setFixedHeight(30)
        input_layout.addWidget(self.line_content, 1)  # 1 = stretch

        # 5. Bouton Ajouter — style identique aux boutons de la page d'accueil
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.setFixedSize(100, 40)  # ajustement de taille uniquement
        self.btn_ajouter.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QPushButton:pressed {
                background-color: #2868A8;
            }
        """)
        input_layout.addWidget(self.btn_ajouter)

        # Ajouter la ligne de saisie au layout principal
        main_layout.addLayout(input_layout)

        # Espacement avant la liste
        main_layout.addSpacing(20)

        # Conteneur pour la liste des devoirs (avec scroll si besoin)
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_container.setLayout(self.scroll_layout)

        # Ajouter le conteneur à la fenêtre
        main_layout.addWidget(self.scroll_container)

        # Appliquer le layout principal
        self.setLayout(main_layout)

        # Charger les classes depuis utils/gestion.py
        self.charger_classes_from_utils()

        # Charger les devoirs depuis utils/gestion.py
        self.charger_devoirs_from_utils()

        # Connexion du bouton (à implémenter plus tard)
        # self.btn_ajouter.clicked.connect(self.ajouter_devoir)

    def charger_classes_from_utils(self):
        """Charge les classes depuis utils/gestion.py et les ajoute au QComboBox"""
        classes = charger_classes()
        self.classes_list = classes

        # Vider le combo box
        self.combo_classe.clear()

        # Ajouter les noms des classes
        for classe in classes:
            self.combo_classe.addItem(classe.nom)

    def charger_devoirs_from_utils(self):
        """Charge les devoirs depuis utils/gestion.py et les affiche dans la liste personnalisée"""
        devoirs = charger_devoirs()
        self.devoirs_list = devoirs

        # Vider la liste
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Ajouter chaque devoir comme une carte personnalisée
        for devoir in devoirs:
            card = DevoirCard(devoir, self)
            self.scroll_layout.addWidget(card)

        # Ajouter un espaceur à la fin pour éviter que le dernier élément touche le bas
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroll_layout.addItem(spacer)

    def ajouter_devoir(self):
        """À implémenter — ajoute un devoir à la liste et au tableau"""
        pass

class DevoirCard(QFrame):
    """Widget personnalisé pour afficher un devoir sous forme de carte"""
    def __init__(self, devoir, parent=None):
        super().__init__(parent)
        self.devoir = devoir
        self.init_ui()

    def init_ui(self):
        # Style de la carte
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
                padding: 5px;
            }
            QLabel.statut {
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 5px;
                color: white;
            }
            QLabel.statut.fait {
                background-color: #28a745;
            }
            QLabel.statut.en_cours {
                background-color: #ffc107;
                color: #333;
            }
            QLabel.statut.a_faire {
                background-color: #dc3545;
            }
        """)

        # Layout principal (vertical) : ligne + ligne colorée en dessous
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Ligne 1 : Classe + Date + Contenu + Statut (sur une seule ligne)
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(5, 5, 5, 5)

        # Classe
        label_classe = QLabel(f"📚 {self.devoir.classe_objet.nom}")
        label_classe.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_layout.addWidget(label_classe)

        # Date
        label_date = QLabel(f"📅 {self.devoir.date}")
        label_date.setStyleSheet("font-size: 13px; color: #666;")
        top_layout.addWidget(label_date)

        # Contenu (flexible)
        label_contenu = QLabel(self.devoir.contenu)
        label_contenu.setWordWrap(True)
        label_contenu.setStyleSheet("font-size: 14px; color: #333;")
        top_layout.addWidget(label_contenu, 1)  # 1 = stretch

        # Statut (avec couleur)
        label_statut = QLabel(self.devoir.statut)
        label_statut.setObjectName("statut")
        if self.devoir.statut == "Fait":
            label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #28a745; color: white;")
        elif self.devoir.statut == "En cours":
            label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #ffc107; color: #333;")
        else:  # À faire
            label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #dc3545; color: white;")

        top_layout.addWidget(label_statut)

        layout.addLayout(top_layout)

        # Ligne 2 : Ligne colorée en dessous (ex: pour indiquer l'état)
        self.line_color = QFrame()
        self.line_color.setFixedHeight(5)  # hauteur de la ligne

        # Récupérer la couleur de la classe
        couleur_classe = self.devoir.classe_objet.couleur

        # Convertir la couleur en format CSS
        # Si la couleur est un nom (ex: "bleu", "rouge"), on peut utiliser un dictionnaire
        # Si c'est un code hexa (ex: "#0000FF"), on l'utilise directement
        color_map = {
            "gris": "#808080",
            "bleu": "#0000FF",
            "vert": "#008000",
            "rouge": "#FF0000",
            "jaune": "#FFFF00",
            "orange": "#FFA500",
            "violet": "#800080",
            "rose": "#FFC0CB",
            "noir": "#000000",
            "blanc": "#FFFFFF",
        }

        color_css = color_map.get(couleur_classe.lower(), "#808080")  # gris par défaut

        # Appliquer la couleur
        self.line_color.setStyleSheet(f"background-color: {color_css};")

        layout.addWidget(self.line_color)

        # Appliquer le layout
        self.setLayout(layout)

        # Effet hover (optionnel)
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.Enter:
                self.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 10px;
                        border: 1px solid #ddd;
                        padding: 10px;
                        margin: 5px;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    }
                    QLabel {
                        font-size: 14px;
                        color: #333;
                        padding: 5px;
                    }
                    QLabel.statut {
                        font-weight: bold;
                        padding: 5px 10px;
                        border-radius: 5px;
                        color: white;
                    }
                    QLabel.statut.fait {
                        background-color: #28a745;
                    }
                    QLabel.statut.en_cours {
                        background-color: #ffc107;
                        color: #333;
                    }
                    QLabel.statut.a_faire {
                        background-color: #dc3545;
                    }
                """)
                self.line_color.setStyleSheet("background-color: #ddd;")  # réinitialiser la couleur de la ligne au hover
                if self.devoir.est_en_retard():
                    self.line_color.setStyleSheet("background-color: #dc3545;")
                elif self.devoir.statut == "Fait":
                    self.line_color.setStyleSheet("background-color: #28a745;")
                elif self.devoir.statut == "En cours":
                    self.line_color.setStyleSheet("background-color: #ffc107;")
            elif event.type() == QEvent.Leave:
                self.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border-radius: 10px;
                        border: 1px solid #ddd;
                        padding: 10px;
                        margin: 5px;
                    }
                    QLabel {
                        font-size: 14px;
                        color: #333;
                        padding: 5px;
                    }
                    QLabel.statut {
                        font-weight: bold;
                        padding: 5px 10px;
                        border-radius: 5px;
                        color: white;
                    }
                    QLabel.statut.fait {
                        background-color: #28a745;
                    }
                    QLabel.statut.en_cours {
                        background-color: #ffc107;
                        color: #333;
                    }
                    QLabel.statut.a_faire {
                        background-color: #dc3545;
                    }
                """)
                self.line_color.setStyleSheet("background-color: #ddd;")
                if self.devoir.est_en_retard():
                    self.line_color.setStyleSheet("background-color: #dc3545;")
                elif self.devoir.statut == "Fait":
                    self.line_color.setStyleSheet("background-color: #28a745;")
                elif self.devoir.statut == "En cours":
                    self.line_color.setStyleSheet("background-color: #ffc107;")
        return super().eventFilter(obj, event)