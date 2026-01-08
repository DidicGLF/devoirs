# screens/gestion_devoirs.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QDateEdit, QComboBox,
    QLineEdit, QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy, QScrollArea, QCheckBox, QApplication
)
from PySide6.QtCore import Qt, QDate, QTimer, QEvent, QMimeData, QPoint
from PySide6.QtGui import QColor, QFont, QPalette, QDrag

import sys
import os

# Ajouter le dossier parent au chemin pour importer utils/gestion.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.gestion import charger_classes, charger_devoirs, sauvegarder_devoirs
from models.Devoir import Devoir

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

        # 3. Contenu (QLineEdit)
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

        # Zone de scroll pour la liste des devoirs
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

        # Conteneur pour la liste des devoirs
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

        # Charger les devoirs depuis utils/gestion.py
        self.charger_devoirs_from_utils()

        # Connexion du bouton
        self.btn_ajouter.clicked.connect(self.ajouter_devoir)

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
            item = self.scroll_layout.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            elif item.spacerItem():
                self.scroll_layout.removeItem(item)

        # Ajouter chaque devoir comme une carte personnalisée
        for devoir in devoirs:
            card = DevoirCard(devoir, self)
            self.scroll_layout.addWidget(card)

        # Ajouter un espaceur à la fin pour éviter que le dernier élément touche le bas
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroll_layout.addItem(spacer)

    def ajouter_devoir(self):
        """Ajoute un devoir à la liste et sauvegarde"""
        contenu = self.line_content.text().strip()
        
        if not contenu or self.combo_classe.currentIndex() == -1:
            return  # Ne rien faire si le contenu est vide ou aucune classe sélectionnée
        
        # Récupérer la classe sélectionnée
        classe_index = self.combo_classe.currentIndex()
        classe_objet = self.classes_list[classe_index]
        
        # Récupérer la date (format YYYY-MM-DD pour correspondre au model)
        date = self.date_edit.date().toString("yyyy-MM-dd")
        
        # Statut par défaut : "À faire"
        statut = "À faire"
        
        # Créer une nouvelle instance de Devoir
        nouveau_devoir = Devoir(
            contenu=contenu,
            classe_objet=classe_objet,
            date=date,
            statut=statut
        )
        
        # Ajouter à la liste
        self.devoirs_list.append(nouveau_devoir)
        
        # Sauvegarder dans le fichier JSON
        sauvegarder_devoirs(self.devoirs_list)
        
        # Recharger l'affichage
        self.charger_devoirs_from_utils()
        
        # Réinitialiser les champs
        self.line_content.clear()
        self.date_edit.setDate(QDate.currentDate())

    def supprimer_devoir(self, devoir):
        """Supprime un devoir de la liste et sauvegarde"""
        if devoir in self.devoirs_list:
            self.devoirs_list.remove(devoir)
            sauvegarder_devoirs(self.devoirs_list)
            self.charger_devoirs_from_utils()


class DevoirCard(QFrame):
    """Widget personnalisé pour afficher un devoir sous forme de carte"""
    def __init__(self, devoir, parent_widget=None):
        super().__init__()
        self.devoir = devoir
        self.parent_widget = parent_widget
        self.setAcceptDrops(True)
        self.drag_start_position = None
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

        # Case à cocher
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(30, 30)
        self.checkbox.setStyleSheet("""
            QCheckBox::indicator {
                width: 25px;
                height: 25px;
                border-radius: 5px;
                border: 2px solid #4A90E2;
            }
            QCheckBox::indicator:unchecked {
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #28a745;
                border-color: #28a745;
            }
        """)
        # Cocher la case si le statut est "Fait" ou "Terminé"
        if self.devoir.statut in ["Fait", "Terminé"]:
            self.checkbox.setChecked(True)
        self.checkbox.stateChanged.connect(self.changer_statut)
        top_layout.addWidget(self.checkbox)

        # Classe
        label_classe = QLabel(f"📚 {self.devoir.classe_objet.nom}")
        label_classe.setStyleSheet("font-weight: bold; font-size: 14px;")
        top_layout.addWidget(label_classe)

        # Date
        # Convertir la date de YYYY-MM-DD en DD-MM-YYYY pour l'affichage
        date_affichage = self.devoir.date
        try:
            from datetime import datetime
            date_obj = datetime.strptime(self.devoir.date, "%Y-%m-%d")
            date_affichage = date_obj.strftime("%d-%m-%Y")
        except:
            pass  # Si la conversion échoue, on garde le format original
        
        label_date = QLabel(f"📅 {date_affichage}")
        label_date.setStyleSheet("font-size: 13px; color: #666;")
        top_layout.addWidget(label_date)

        # Contenu (flexible)
        self.label_contenu = QLabel(self.devoir.contenu)
        self.label_contenu.setWordWrap(True)
        self.label_contenu.setStyleSheet("font-size: 14px; color: #333;")
        self.label_contenu.setCursor(Qt.PointingHandCursor)  # Curseur en main
        self.label_contenu.mousePressEvent = self.activer_edition_contenu
        top_layout.addWidget(self.label_contenu, 1)  # 1 = stretch
        
        # Champ d'édition (caché par défaut)
        self.line_edit_contenu = QLineEdit(self.devoir.contenu)
        self.line_edit_contenu.setStyleSheet("font-size: 14px; color: #333;")
        self.line_edit_contenu.hide()
        self.line_edit_contenu.returnPressed.connect(self.sauvegarder_contenu)
        self.line_edit_contenu.editingFinished.connect(self.sauvegarder_contenu)
        top_layout.addWidget(self.line_edit_contenu, 1)

        # Statut (avec couleur)
        self.label_statut = QLabel(self.devoir.statut)
        self.label_statut.setObjectName("statut")
        if self.devoir.statut == "Terminé" or self.devoir.statut == "Fait":
            self.label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #28a745; color: white;")
        elif self.devoir.statut == "En cours":
            self.label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #ffc107; color: #333;")
        else:  # À faire
            self.label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #dc3545; color: white;")

        top_layout.addWidget(self.label_statut)

        # Bouton supprimer (optionnel, comme dans les classes)
        btn_supprimer = QPushButton("🗑️")
        btn_supprimer.setFixedSize(35, 35)
        btn_supprimer.setStyleSheet("""
            QPushButton {
                background-color: white;
                color: #dc3545;
                border: 2px solid #dc3545;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
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

        # Ligne 2 : Ligne colorée en dessous (ex: pour indiquer la couleur de la classe)
        self.line_color = QFrame()
        self.line_color.setFixedHeight(5)  # hauteur de la ligne

        # Récupérer la couleur de la classe
        couleur_classe = self.devoir.classe_objet.couleur

        # Convertir la couleur en format CSS
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

        # Si la couleur est déjà en format hex, on la garde
        if couleur_classe.startswith('#'):
            self.color_css = couleur_classe
        else:
            self.color_css = color_map.get(couleur_classe.lower(), "#808080")

        # Appliquer la couleur
        self.line_color.setStyleSheet(f"background-color: {self.color_css};")

        layout.addWidget(self.line_color)

        # Appliquer le layout
        self.setLayout(layout)

        # Effet hover (optionnel)
        self.setMouseTracking(True)
        self.installEventFilter(self)

    def mousePressEvent(self, event):
        """Démarre le drag & drop"""
        if event.button() == Qt.LeftButton:
            # Vérifier que le clic n'est pas sur un widget interactif
            widget_under_mouse = QApplication.widgetAt(event.globalPosition().toPoint())
            if widget_under_mouse in [self.checkbox, self.label_contenu, self.line_edit_contenu]:
                super().mousePressEvent(event)
                return
            if isinstance(widget_under_mouse, QPushButton):
                super().mousePressEvent(event)
                return
                
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """Gère le déplacement pendant le drag"""
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_position is None:
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        # Créer le drag
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Stocker l'index de cette carte
        index = self.parent_widget.devoirs_list.index(self.devoir)
        mime_data.setText(str(index))
        drag.setMimeData(mime_data)

        # Effet visuel pendant le drag
        drag.exec(Qt.MoveAction)
        self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        """Fin du drag"""
        self.drag_start_position = None
        self.setCursor(Qt.OpenHandCursor)
        super().mouseReleaseEvent(event)

    def dragEnterEvent(self, event):
        """Accepte le drag d'une autre carte"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Gère le drop sur cette carte"""
        if event.mimeData().hasText():
            source_index = int(event.mimeData().text())
            target_index = self.parent_widget.devoirs_list.index(self.devoir)
            
            if source_index != target_index:
                # Réorganiser la liste
                devoir_deplace = self.parent_widget.devoirs_list.pop(source_index)
                self.parent_widget.devoirs_list.insert(target_index, devoir_deplace)
                
                # Sauvegarder
                sauvegarder_devoirs(self.parent_widget.devoirs_list)
                
                # Recharger l'affichage
                self.parent_widget.charger_devoirs_from_utils()
            
            event.acceptProposedAction()

    def supprimer(self):
        """Supprime ce devoir"""
        if self.parent_widget:
            self.parent_widget.supprimer_devoir(self.devoir)

    def changer_statut(self, state):
        """Change le statut du devoir en fonction de l'état de la case à cocher"""
        # state est un entier: 0 = Unchecked, 2 = Checked
        if state == 2:  # Checked
            self.devoir.statut = "Fait"
        else:  # Unchecked (0)
            self.devoir.statut = "À faire"
        
        # Mettre à jour l'affichage du statut
        self.mettre_a_jour_affichage_statut()
        
        # Sauvegarder les modifications
        if self.parent_widget:
            sauvegarder_devoirs(self.parent_widget.devoirs_list)

    def activer_edition_contenu(self, event):
        """Active le mode édition du contenu"""
        self.label_contenu.hide()
        self.line_edit_contenu.setText(self.devoir.contenu)
        self.line_edit_contenu.show()
        self.line_edit_contenu.setFocus()
        self.line_edit_contenu.selectAll()

    def copier_contenu(self):
        """Copie le contenu du devoir dans le presse-papier"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.devoir.contenu)
        
        # Indication visuelle temporaire (optionnel)
        original_style = self.styleSheet()
        self.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border-radius: 10px;
                border: 2px solid #2196F3;
                padding: 10px;
                margin: 5px;
            }
        """)
        
        # Retour au style normal après 200ms
        QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))

    def sauvegarder_contenu(self):
        """Sauvegarde le contenu modifié"""
        nouveau_contenu = self.line_edit_contenu.text().strip()
        
        if nouveau_contenu:  # Ne pas accepter un contenu vide
            self.devoir.contenu = nouveau_contenu
            self.label_contenu.setText(nouveau_contenu)
            
            # Sauvegarder dans le fichier JSON
            if self.parent_widget:
                sauvegarder_devoirs(self.parent_widget.devoirs_list)
        
        # Retour à l'affichage normal
        self.line_edit_contenu.hide()
        self.label_contenu.show()

    def mettre_a_jour_affichage_statut(self):
        """Met à jour l'affichage du label de statut"""
        self.label_statut.setText(self.devoir.statut)
        # Mettre à jour la couleur
        if self.devoir.statut == "Fait":
            self.label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #28a745; color: white;")
        else:  # À faire
            self.label_statut.setStyleSheet("font-weight: bold; padding: 5px 10px; border-radius: 5px; background-color: #dc3545; color: white;")

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.MouseButtonPress:
                # Copier le contenu quand on clique sur la carte
                widget_under_mouse = QApplication.widgetAt(event.globalPosition().toPoint())
                if widget_under_mouse not in [self.checkbox, self.label_contenu, self.line_edit_contenu]:
                    if not isinstance(widget_under_mouse, QPushButton):
                        self.copier_contenu()
            elif event.type() == QEvent.Enter:
                # Style au survol : bordure plus foncée
                self.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 10px;
                        border: 1px solid #999;
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
                # Réappliquer la couleur de la classe à la ligne
                self.line_color.setStyleSheet(f"background-color: {self.color_css};")
            elif event.type() == QEvent.Leave:
                # Style normal
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
                # Réappliquer la couleur de la classe à la ligne
                self.line_color.setStyleSheet(f"background-color: {self.color_css};")
        return super().eventFilter(obj, event)