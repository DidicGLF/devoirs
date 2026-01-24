# screens/gestion_classes.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, 
    QFrame, QLabel, QSpacerItem, QSizePolicy, QColorDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIntValidator

import sys
import os

# Ajouter le dossier parent au chemin pour importer utils/gestion.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.gestion import charger_classes, sauvegarder_classes
from models.Classe import Classe

class ClassesWidget(QWidget):
    """Écran de gestion des classes — partie saisie + liste des classes"""
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window  # Référence à AccueilWindow
        self.classes_list = []  # Stockage des instances de Classe
        self.couleur_selectionnee = "#808080"  # Couleur par défaut (gris)
        self.init_ui()

    def init_ui(self):
        # Layout principal (vertical)
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(50, 0, 50, 50)

        # Ligne de saisie (horizontal)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        # 1. Nom de la classe (QLineEdit)
        self.line_nom = QLineEdit()
        self.line_nom.setPlaceholderText("Nom de la classe (ex: 5ème A)")
        self.line_nom.setFixedHeight(30)
        self.line_nom.setFixedWidth(200)
        input_layout.addWidget(self.line_nom)

        # 2. Effectif (QLineEdit avec validation numérique)
        self.line_effectif = QLineEdit()
        self.line_effectif.setPlaceholderText("Effectif")
        self.line_effectif.setFixedHeight(30)
        self.line_effectif.setFixedWidth(150)
        # Accepter uniquement les chiffres
        from PySide6.QtGui import QIntValidator
        validator = QIntValidator(0, 999, self)
        self.line_effectif.setValidator(validator)
        input_layout.addWidget(self.line_effectif)

        # 3. Sélecteur de couleur (bouton)
        self.btn_couleur = QPushButton("Choisir couleur")
        self.btn_couleur.setFixedSize(150, 40)
        self.btn_couleur.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.couleur_selectionnee};
                color: white;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #ddd;
            }}
            QPushButton:hover {{
                border: 2px solid #999;
            }}
        """)
        self.btn_couleur.clicked.connect(self.choisir_couleur)
        input_layout.addWidget(self.btn_couleur)

        # Espaceur flexible
        input_layout.addStretch()

        # 4. Bouton Ajouter
        self.btn_ajouter = QPushButton("Ajouter")
        self.btn_ajouter.setFixedSize(100, 40)
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
        self.btn_ajouter.clicked.connect(self.ajouter_classe)
        input_layout.addWidget(self.btn_ajouter)

        # Ajouter la ligne de saisie au layout principal
        main_layout.addLayout(input_layout)

        # Espacement avant la liste
        main_layout.addSpacing(20)

        # Zone de scroll pour la liste des classes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

        # Conteneur pour la liste des classes
        self.scroll_container = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(10)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setAlignment(Qt.AlignTop)  # Aligner en haut
        self.scroll_container.setLayout(self.scroll_layout)

        # Ajouter le conteneur dans la zone de scroll
        scroll_area.setWidget(self.scroll_container)

        # Ajouter la zone de scroll à la fenêtre
        main_layout.addWidget(scroll_area)

        # Appliquer le layout principal
        self.setLayout(main_layout)

        # Charger les classes depuis utils/gestion.py
        self.charger_classes_from_utils()

    def choisir_couleur(self):
        """Ouvre un sélecteur de couleur"""
        couleur = QColorDialog.getColor(QColor(self.couleur_selectionnee), self, "Choisir une couleur")
        
        if couleur.isValid():
            self.couleur_selectionnee = couleur.name()
            # Mettre à jour le style du bouton
            self.btn_couleur.setStyleSheet(f"""
                QPushButton {{
                    background-color: {self.couleur_selectionnee};
                    color: white;
                    border-radius: 8px;
                    font-size: 12px;
                    font-weight: bold;
                    border: 2px solid #ddd;
                }}
                QPushButton:hover {{
                    border: 2px solid #999;
                }}
            """)

    def charger_classes_from_utils(self):
        """Charge les classes depuis utils/gestion.py et les affiche"""
        classes = charger_classes()
        self.classes_list = classes

        # Vider la liste
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.scroll_layout.removeItem(item)

        # Ajouter chaque classe comme une carte personnalisée
        for classe in classes:
            card = ClasseCard(classe, self)
            self.scroll_layout.addWidget(card)

        # Ajouter un espaceur à la fin
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroll_layout.addItem(spacer)

    def ajouter_classe(self):
        """Ajoute une nouvelle classe à la liste et sauvegarde"""
        nom = self.line_nom.text().strip()
        effectif_text = self.line_effectif.text().strip()
        
        if not nom or not effectif_text:
            return  # Ne rien faire si le nom ou l'effectif est vide
        
        effectif = int(effectif_text)
        
        # Créer une nouvelle instance de Classe
        nouvelle_classe = Classe(nom=nom, effectif=effectif, couleur=self.couleur_selectionnee)
        
        # Ajouter à la liste
        self.classes_list.append(nouvelle_classe)
        
        # Sauvegarder dans le fichier JSON
        sauvegarder_classes(self.classes_list)
        
        # Recharger l'affichage
        self.charger_classes_from_utils()
        
        # Rafraîchir la page des devoirs si elle existe
        self.rafraichir_page_devoirs()
        
        # Réinitialiser les champs
        self.line_nom.clear()
        self.line_effectif.clear()
        self.couleur_selectionnee = "#808080"
        self.btn_couleur.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.couleur_selectionnee};
                color: white;
                border-radius: 8px;
                font-size: 12px;
                font-weight: bold;
                border: 2px solid #ddd;
            }}
            QPushButton:hover {{
                border: 2px solid #999;
            }}
        """)

    def supprimer_classe(self, classe):
        """Supprime une classe de la liste et sauvegarde"""
        if classe in self.classes_list:
            self.classes_list.remove(classe)
            sauvegarder_classes(self.classes_list)
            self.charger_classes_from_utils()
            
            # Rafraîchir la page des devoirs si elle existe
            self.rafraichir_page_devoirs()

    def rafraichir_page_devoirs(self):
        """Rafraîchit la liste des classes dans la page des devoirs"""
        if self.main_window:
            # Recharger la page des devoirs si elle existe
            if hasattr(self.main_window, 'page_devoirs') and self.main_window.page_devoirs:
                # Récupérer le widget DevoirsWidget
                for i in range(self.main_window.page_devoirs.layout().count()):
                    widget = self.main_window.page_devoirs.layout().itemAt(i).widget()
                    if widget and hasattr(widget, 'charger_classes_from_utils'):
                        widget.charger_classes_from_utils()
                        break


class ClasseCard(QFrame):
    """Widget personnalisé pour afficher une classe sous forme de carte"""
    def __init__(self, classe, parent_widget=None):
        super().__init__()
        self.classe = classe
        self.parent_widget = parent_widget
        self.init_ui()

    def init_ui(self):
        # Convertir la couleur de la classe en format CSS avec alpha (transparence)
        color_map = {
            "gris": "128, 128, 128",
            "bleu": "0, 0, 255",
            "vert": "0, 128, 0",
            "rouge": "255, 0, 0",
            "jaune": "255, 255, 0",
            "orange": "255, 165, 0",
            "violet": "128, 0, 128",
            "rose": "255, 192, 203",
            "noir": "0, 0, 0",
            "blanc": "255, 255, 255",
        }
        
        # Récupérer les valeurs RGB
        couleur_classe = self.classe.couleur
        if couleur_classe.startswith('#'):
            # Convertir hex en RGB
            hex_color = couleur_classe.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            rgb_values = f"{r}, {g}, {b}"
        else:
            rgb_values = color_map.get(couleur_classe.lower(), "128, 128, 128")
        
        # Stocker pour le eventFilter
        self.rgb_values = rgb_values
        
        # Style de la carte avec fond coloré (alpha = 0.15 pour une couleur douce)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba({rgb_values}, 0.15);
                border-radius: 10px;
                border: 1px solid rgba({rgb_values}, 0.3);
                padding: 10px;
                margin: 5px;
            }}
            QLabel {{
                font-size: 14px;
                color: #333;
                padding: 5px;
                background-color: transparent;
            }}
        """)

        # Layout principal (vertical)
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # Ligne 1 : Nom + Effectif + Bouton supprimer
        top_layout = QHBoxLayout()
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(5, 5, 5, 5)

        # Nom de la classe
        label_nom = QLabel(f"📚 {self.classe.nom}")
        label_nom.setStyleSheet("font-weight: bold; font-size: 16px;")
        top_layout.addWidget(label_nom)

        # Effectif
        label_effectif = QLabel(f"👥 Effectif: {self.classe.effectif}")
        label_effectif.setStyleSheet("font-size: 14px; color: #666;")
        top_layout.addWidget(label_effectif)

        # Espaceur flexible
        top_layout.addStretch()

        # Bouton supprimer
        btn_supprimer = QPushButton("🗑️")
        btn_supprimer.setFixedSize(35, 35)
        btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #dc3545;
                border: 2px solid #dc3545;
                border-radius: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #ffe6e6;
            }
            QPushButton:pressed {
                background-color: #ffcccc;
            }
        """)
        btn_supprimer.clicked.connect(self.supprimer)
        top_layout.addWidget(btn_supprimer)

        layout.addLayout(top_layout)

        # Appliquer le layout
        self.setLayout(layout)

        # Effet hover
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def supprimer(self):
        """Supprime cette classe"""
        if self.parent_widget:
            self.parent_widget.supprimer_classe(self.classe)

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == event.Type.Enter:
                # Style au survol : couleur plus intense
                self.setStyleSheet(f"""
                    QFrame {{
                        background-color: rgba({self.rgb_values}, 0.25);
                        border-radius: 10px;
                        border: 2px solid rgba({self.rgb_values}, 0.5);
                        padding: 10px;
                        margin: 5px;
                    }}
                    QLabel {{
                        font-size: 14px;
                        color: #333;
                        padding: 5px;
                        background-color: transparent;
                    }}
                """)
            elif event.type() == event.Type.Leave:
                # Style normal
                self.setStyleSheet(f"""
                    QFrame {{
                        background-color: rgba({self.rgb_values}, 0.15);
                        border-radius: 10px;
                        border: 1px solid rgba({self.rgb_values}, 0.3);
                        padding: 10px;
                        margin: 5px;
                    }}
                    QLabel {{
                        font-size: 14px;
                        color: #333;
                        padding: 5px;
                        background-color: transparent;
                    }}
                """)
        return super().eventFilter(obj, event)