# screens/gestion_devoirs.py
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QDateEdit, QComboBox,
    QLineEdit, QPushButton, QFrame, QLabel, QSpacerItem, QSizePolicy, QScrollArea, QCheckBox, QApplication
)
from PySide6.QtCore import Qt, QDate, QTimer, QEvent, QMimeData, QPoint
from PySide6.QtGui import QColor, QFont, QPalette, QDrag, QPixmap, QPainter

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

        # Barre de tri
        tri_layout = QHBoxLayout()
        tri_layout.setSpacing(10)
        tri_layout.setContentsMargins(0, 0, 0, 10)

        tri_label = QLabel("Trier par :")
        tri_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #333;")
        tri_layout.addWidget(tri_label)

        # Bouton tri par date
        self.btn_tri_date = QPushButton("Date")
        self.btn_tri_date.setFixedSize(100, 35)
        self.btn_tri_date.setCheckable(True)
        self.btn_tri_date.clicked.connect(self.trier_par_date)
        tri_layout.addWidget(self.btn_tri_date)

        # Bouton tri par classe
        self.btn_tri_classe = QPushButton("Classe")
        self.btn_tri_classe.setFixedSize(100, 35)
        self.btn_tri_classe.setCheckable(True)
        self.btn_tri_classe.clicked.connect(self.trier_par_classe)
        tri_layout.addWidget(self.btn_tri_classe)

        # Bouton ordre manuel
        self.btn_tri_manuel = QPushButton("Manuel")
        self.btn_tri_manuel.setFixedSize(100, 35)
        self.btn_tri_manuel.setCheckable(True)
        self.btn_tri_manuel.setChecked(True)  # Activé par défaut
        self.btn_tri_manuel.clicked.connect(self.trier_manuel)
        tri_layout.addWidget(self.btn_tri_manuel)

        #tri_layout.addStretch()
        
        # Bouton Projection
        self.btn_projection = QPushButton("Projection")
        self.btn_projection.setFixedSize(120, 35)
        self.btn_projection.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: 2px solid #28a745;
                border-radius: 8px;
                font-size: 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #218838;
                border-color: #218838;
            }
            QPushButton:checked {
                background-color: #1e7e34;
                border-color: #1e7e34;
            }
        """)
        self.btn_projection.clicked.connect(self.ouvrir_projection)
        tri_layout.addWidget(self.btn_projection)

        # Style des boutons de tri
        style_btn_tri = """
            QPushButton {
                background-color: white;
                color: #333;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 12px;
                font-weight: normal;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
                border-color: #999;
            }
            QPushButton:checked {
                background-color: #4A90E2;
                color: white;
                border-color: #4A90E2;
            }
        """
        self.btn_tri_date.setStyleSheet(style_btn_tri)
        self.btn_tri_classe.setStyleSheet(style_btn_tri)
        self.btn_tri_manuel.setStyleSheet(style_btn_tri)

        tri_layout.addStretch()
        main_layout.addLayout(tri_layout)

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
        self.scroll_layout.setSpacing(40)
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
        
        # Réinitialiser seulement le champ de contenu (garder la date et la classe)
        self.line_content.clear()

    def supprimer_devoir(self, devoir):
        """Supprime un devoir de la liste et sauvegarde"""
        if devoir in self.devoirs_list:
            self.devoirs_list.remove(devoir)
            sauvegarder_devoirs(self.devoirs_list)
            self.charger_devoirs_from_utils()

    def trier_par_date(self):
        """Trie les devoirs par date (tri visuel uniquement, non sauvegardé)"""
        # Désactiver les autres boutons
        self.btn_tri_classe.setChecked(False)
        self.btn_tri_manuel.setChecked(False)
        
        if not self.btn_tri_date.isChecked():
            # Si on déclique, revenir au tri manuel
            self.btn_tri_manuel.setChecked(True)
            self.trier_manuel()
            return
        
        # Trier par date
        devoirs_tries = sorted(self.devoirs_list, key=lambda d: d.date)
        
        # Afficher sans sauvegarder
        self.afficher_devoirs(devoirs_tries)

    def trier_par_classe(self):
        """Trie les devoirs par classe (tri visuel uniquement, non sauvegardé)"""
        # Désactiver les autres boutons
        self.btn_tri_date.setChecked(False)
        self.btn_tri_manuel.setChecked(False)
        
        if not self.btn_tri_classe.isChecked():
            # Si on déclique, revenir au tri manuel
            self.btn_tri_manuel.setChecked(True)
            self.trier_manuel()
            return
        
        # Trier par nom de classe
        devoirs_tries = sorted(self.devoirs_list, key=lambda d: d.classe_objet.nom)
        
        # Afficher sans sauvegarder
        self.afficher_devoirs(devoirs_tries)

    def trier_manuel(self):
        """Revient à l'ordre manuel (celui du fichier JSON)"""
        # Désactiver les autres boutons
        self.btn_tri_date.setChecked(False)
        self.btn_tri_classe.setChecked(False)
        self.btn_tri_manuel.setChecked(True)
        
        # Recharger depuis le fichier pour avoir l'ordre original
        self.charger_devoirs_from_utils()

    def afficher_devoirs(self, devoirs):
        """Affiche une liste de devoirs (sans sauvegarder)"""
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

        # Ajouter un espaceur à la fin
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.scroll_layout.addItem(spacer)

    def ouvrir_projection(self):
        """Ouvre la page de projection"""
        from screens.gestion_projection import ProjectionWidget
        
        if hasattr(self, 'parent') and self.parent():
            # Trouver la fenêtre principale
            main_window = self.parent()
            while main_window.parent():
                main_window = main_window.parent()
            
            # Créer la page de projection
            page_projection = ProjectionWidget(main_window=main_window)
            page_complete = main_window.create_page_with_back_button(
                page_projection, 
                "Projection"
            )
            main_window.stacked_widget.addWidget(page_complete)
            main_window.stacked_widget.setCurrentWidget(page_complete)


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
        couleur_classe = self.devoir.classe_objet.couleur
        if couleur_classe.startswith('#'):
            # Convertir hex en RGB
            hex_color = couleur_classe.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            rgb_values = f"{r}, {g}, {b}"
        else:
            rgb_values = color_map.get(couleur_classe.lower(), "128, 128, 128")
        
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
        
        # Créer une image de la carte pour le drag (pixmap)
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter, QPoint(0, 0))
        painter.end()
        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # Effet visuel pendant le drag
        result = drag.exec(Qt.MoveAction)
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
            # Indication visuelle : bordure bleue épaisse
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(74, 144, 226, 0.2);
                    border-radius: 10px;
                    border: 3px solid #4A90E2;
                    padding: 10px;
                    margin: 5px;
                }
            """)

    def dragLeaveEvent(self, event):
        """Restaure le style quand le drag quitte la carte"""
        # Récupérer les valeurs RGB de la couleur de classe
        self.restaurer_style_normal()

    def dropEvent(self, event):
        """Gère le drop sur cette carte"""
        if event.mimeData().hasText():
            source_index = int(event.mimeData().text())
            target_index = self.parent_widget.devoirs_list.index(self.devoir)
            
            if source_index != target_index:
                # Effet visuel : flash vert pour confirmer
                self.setStyleSheet("""
                    QFrame {
                        background-color: rgba(40, 167, 69, 0.3);
                        border-radius: 10px;
                        border: 2px solid #28a745;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
                
                # Réorganiser la liste
                devoir_deplace = self.parent_widget.devoirs_list.pop(source_index)
                self.parent_widget.devoirs_list.insert(target_index, devoir_deplace)
                
                # Sauvegarder
                sauvegarder_devoirs(self.parent_widget.devoirs_list)
                
                # Recharger l'affichage après un court délai
                QTimer.singleShot(200, lambda: self.parent_widget.charger_devoirs_from_utils())
            else:
                self.restaurer_style_normal()
            
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

    def restaurer_style_normal(self):
        """Restaure le style normal avec la couleur de la classe"""
        # Récupérer les valeurs RGB
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
        
        couleur_classe = self.devoir.classe_objet.couleur
        if couleur_classe.startswith('#'):
            hex_color = couleur_classe.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            rgb_values = f"{r}, {g}, {b}"
        else:
            rgb_values = color_map.get(couleur_classe.lower(), "128, 128, 128")
        
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

    def eventFilter(self, obj, event):
        if obj == self:
            if event.type() == QEvent.MouseButtonPress:
                # Copier le contenu quand on clique sur la carte
                widget_under_mouse = QApplication.widgetAt(event.globalPosition().toPoint())
                if widget_under_mouse not in [self.checkbox, self.label_contenu, self.line_edit_contenu]:
                    if not isinstance(widget_under_mouse, QPushButton):
                        self.copier_contenu()
            elif event.type() == QEvent.Enter:
                # Style au survol : bordure plus visible
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
                
                couleur_classe = self.devoir.classe_objet.couleur
                if couleur_classe.startswith('#'):
                    hex_color = couleur_classe.lstrip('#')
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    rgb_values = f"{r}, {g}, {b}"
                else:
                    rgb_values = color_map.get(couleur_classe.lower(), "128, 128, 128")
                
                self.setStyleSheet(f"""
                    QFrame {{
                        background-color: rgba({rgb_values}, 0.25);
                        border-radius: 10px;
                        border: 2px solid rgba({rgb_values}, 0.5);
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
            elif event.type() == QEvent.Leave:
                # Style normal
                self.restaurer_style_normal()
        return super().eventFilter(obj, event)