# screens/gestion_parametres.py
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFrame, QFileDialog, QMessageBox, QSpacerItem, QSizePolicy, QScrollArea, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

import sys
import os
import json
import shutil
from datetime import datetime

# Ajouter le dossier parent au chemin
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.gestion import charger_classes, charger_devoirs, sauvegarder_classes, sauvegarder_devoirs, CLASSES_FILE, DEVOIRS_FILE

# Import du gestionnaire de configuration
from utils.config_manager import get_lien_ent, set_lien_ent

# Import du gestionnaire de thème
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utils'))

class ParametresWidget(QWidget):
    """Écran de gestion des paramètres"""
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main_window = main_window  # Référence à AccueilWindow
        self.init_ui()

    def init_ui(self):
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Zone de scroll
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

        # Widget conteneur pour le contenu scrollable
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(20)
        scroll_layout.setContentsMargins(50, 20, 50, 50)
        scroll_layout.setAlignment(Qt.AlignTop)

        # ==================== SECTION DONNÉES ====================
        section_donnees = self.creer_section("📊 Données", [
            ("Exporter les données", "Exporter toutes vos classes et devoirs dans un fichier JSON", self.exporter_donnees),
            ("Importer des données", "Importer des classes et devoirs depuis un fichier JSON", self.importer_donnees),
            ("Réinitialiser les données", "Supprimer toutes les classes et devoirs (irréversible)", self.reinitialiser_donnees)
        ])
        scroll_layout.addWidget(section_donnees)

        # ==================== SECTION APPARENCE ====================
        section_apparence = self.creer_section("🎨 Apparence", [
            ("Thème", "Basculer entre thème clair et thème sombre (prochainement)", None),
            ("Taille de police", "Ajuster la taille du texte (prochainement)", None)
        ])
        scroll_layout.addWidget(section_apparence)

        # ==================== SECTION PRÉFÉRENCES ====================
        section_preferences = self.creer_section("⚙️ Préférences", [
            ("Lien personnalisé", "Modifier le lien affiché sur la page d'accueil", self.modifier_lien_ent),
            ("Format de date", "Choisir le format d'affichage des dates (prochainement)", None)
        ])
        scroll_layout.addWidget(section_preferences)

        # ==================== SECTION À PROPOS ====================
        section_apropos = self.creer_section_apropos()
        scroll_layout.addWidget(section_apropos)

        # Espaceur en bas
        scroll_layout.addStretch()

        # Appliquer le layout au widget scrollable
        scroll_widget.setLayout(scroll_layout)
        
        # Ajouter le widget dans la zone de scroll
        scroll_area.setWidget(scroll_widget)
        
        # Ajouter la zone de scroll au layout principal
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def creer_section(self, titre, elements):
        """Crée une section de paramètres avec un titre et des éléments"""
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
                padding: 15px;
            }
        """)
        
        section_layout = QVBoxLayout()
        section_layout.setSpacing(15)
        
        # Titre de la section
        titre_label = QLabel(titre)
        titre_label.setFont(QFont("Arial", 14, QFont.Bold))
        titre_label.setStyleSheet("color: #333; border: none; padding: 0;")
        section_layout.addWidget(titre_label)
        
        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ddd; border: none; padding: 0;")
        separator.setFixedHeight(1)
        section_layout.addWidget(separator)
        
        # Éléments de la section
        for nom, description, action in elements:
            element_layout = QHBoxLayout()
            element_layout.setSpacing(10)
            
            # Texte (nom + description)
            text_layout = QVBoxLayout()
            text_layout.setSpacing(5)
            
            nom_label = QLabel(nom)
            nom_label.setFont(QFont("Arial", 12, QFont.Bold))
            nom_label.setStyleSheet("color: #333; border: none; padding: 0;")
            text_layout.addWidget(nom_label)
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666; font-size: 11px; border: none; padding: 0;")
            desc_label.setWordWrap(True)
            text_layout.addWidget(desc_label)
            
            element_layout.addLayout(text_layout, 1)
            
            # Bouton d'action
            if action:
                # Bouton pour "Lien personnalisé"
                if "Lien" in nom:
                    btn = QPushButton("Modifier")
                    btn.setFixedSize(120, 35)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4A90E2;
                            color: white;
                            border-radius: 8px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #357ABD;
                        }
                        QPushButton:pressed {
                            background-color: #2868A8;
                        }
                    """)
                    btn.clicked.connect(action)
                    element_layout.addWidget(btn)
                # Bouton pour Export/Import
                elif "Exporter" in nom or "Importer" in nom:
                    btn = QPushButton("Exécuter")
                    btn.setFixedSize(120, 35)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #4A90E2;
                            color: white;
                            border-radius: 8px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #357ABD;
                        }
                        QPushButton:pressed {
                            background-color: #2868A8;
                        }
                    """)
                    btn.clicked.connect(action)
                    element_layout.addWidget(btn)
                # Bouton pour Réinitialiser
                elif "Réinitialiser" in nom:
                    btn = QPushButton("Réinitialiser")
                    btn.setFixedSize(120, 35)
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: white;
                            color: #dc3545;
                            border: 2px solid #dc3545;
                            border-radius: 8px;
                            font-size: 12px;
                        }
                        QPushButton:hover {
                            background-color: #ffe6e6;
                        }
                        QPushButton:pressed {
                            background-color: #ffcccc;
                        }
                    """)
                    btn.clicked.connect(action)
                    element_layout.addWidget(btn)
            else:
                # Placeholder pour les fonctionnalités à venir
                placeholder = QLabel("Bientôt")
                placeholder.setStyleSheet("color: #999; font-style: italic; border: none; padding: 0;")
                element_layout.addWidget(placeholder)
            
            section_layout.addLayout(element_layout)
        
        section_frame.setLayout(section_layout)
        return section_frame

    def creer_section_apropos(self):
        """Crée la section À propos"""
        section_frame = QFrame()
        section_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #ddd;
                padding: 15px;
            }
        """)
        
        section_layout = QVBoxLayout()
        section_layout.setSpacing(10)
        
        # Titre
        titre_label = QLabel("ℹ️ À propos")
        titre_label.setFont(QFont("Arial", 14, QFont.Bold))
        titre_label.setStyleSheet("color: #333; border: none; padding: 0;")
        section_layout.addWidget(titre_label)
        
        # Ligne de séparation
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #ddd; border: none; padding: 0;")
        separator.setFixedHeight(1)
        section_layout.addWidget(separator)
        
        # Informations
        info_label = QLabel("Mes Devoirs - Version 1.0\n\nApplication de gestion de devoirs scolaires\nDéveloppée avec PySide6")
        info_label.setStyleSheet("color: #666; font-size: 12px; border: none; padding: 0;")
        section_layout.addWidget(info_label)
        
        section_frame.setLayout(section_layout)
        return section_frame

    # ==================== IMPLÉMENTATION SECTION DONNÉES ====================   
        
    def exporter_donnees(self):
        """Exporte toutes les données (classes + devoirs) dans un fichier JSON"""
        # Ouvrir le dialogue de sauvegarde
        fichier, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les données",
            f"sauvegarde_devoirs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            "Fichiers JSON (*.json)"
        )
        
        if not fichier:
            return  # L'utilisateur a annulé
        
        try:
            # Charger les données actuelles
            classes = charger_classes()
            devoirs = charger_devoirs()
            
            # Convertir en dictionnaires
            classes_data = []
            for classe in classes:
                classes_data.append({
                    "nom": classe.nom,
                    "effectif": classe.effectif,
                    "couleur": classe.couleur
                })
            
            devoirs_data = []
            for devoir in devoirs:
                devoirs_data.append({
                    "contenu": devoir.contenu,
                    "classe_nom": devoir.classe_objet.nom,
                    "date": devoir.date,
                    "statut": devoir.statut
                })
            
            # Créer le fichier d'export
            export_data = {
                "version": "1.0",
                "date_export": datetime.now().isoformat(),
                "classes": classes_data,
                "devoirs": devoirs_data
            }
            
            # Sauvegarder
            with open(fichier, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self,
                "Export réussi",
                f"Les données ont été exportées avec succès dans :\n{fichier}"
            )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur d'export",
                f"Une erreur est survenue lors de l'export :\n{str(e)}"
            )

    def importer_donnees(self):
        """Importe des données depuis un fichier JSON"""
        # Ouvrir le dialogue de sélection
        fichier, _ = QFileDialog.getOpenFileName(
            self,
            "Importer des données",
            "",
            "Fichiers JSON (*.json)"
        )
        
        if not fichier:
            return  # L'utilisateur a annulé
        
        # Demander confirmation
        reponse = QMessageBox.question(
            self,
            "Confirmation d'import",
            "L'import va remplacer toutes vos données actuelles.\nVoulez-vous continuer ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reponse != QMessageBox.Yes:
            return
        
        try:
            # Lire le fichier
            with open(fichier, 'r', encoding='utf-8') as f:
                import_data = json.load(f)
            
            # Vérifier la structure
            if "classes" not in import_data or "devoirs" not in import_data:
                raise ValueError("Format de fichier invalide")
            
            # Créer une sauvegarde des données actuelles
            backup_dir = os.path.join(os.path.dirname(CLASSES_FILE), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if os.path.exists(CLASSES_FILE):
                shutil.copy(CLASSES_FILE, os.path.join(backup_dir, f'classes_backup_{timestamp}.json'))
            if os.path.exists(DEVOIRS_FILE):
                shutil.copy(DEVOIRS_FILE, os.path.join(backup_dir, f'devoirs_backup_{timestamp}.json'))
            
            # Écrire les nouvelles données
            with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
                json.dump(import_data["classes"], f, ensure_ascii=False, indent=2)
            
            with open(DEVOIRS_FILE, 'w', encoding='utf-8') as f:
                json.dump(import_data["devoirs"], f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self,
                "Import réussi",
                f"Les données ont été importées avec succès !\n\nUne sauvegarde des anciennes données a été créée dans :\n{backup_dir}"
            )
            
            # Rafraîchir les pages si possible
            self.rafraichir_pages()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur d'import",
                f"Une erreur est survenue lors de l'import :\n{str(e)}"
            )

    def reinitialiser_donnees(self):
        """Supprime toutes les classes et devoirs"""
        # Double confirmation
        reponse1 = QMessageBox.warning(
            self,
            "Confirmation de réinitialisation",
            "⚠️ ATTENTION ⚠️\n\nCette action va supprimer TOUTES vos classes et devoirs.\nCette action est IRRÉVERSIBLE.\n\nÊtes-vous absolument sûr ?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reponse1 != QMessageBox.Yes:
            return
        
        reponse2 = QMessageBox.warning(
            self,
            "Dernière confirmation",
            "Tapez le mot 'SUPPRIMER' pour confirmer la réinitialisation complète.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reponse2 != QMessageBox.Yes:
            return
        
        try:
            # Créer une sauvegarde avant suppression
            backup_dir = os.path.join(os.path.dirname(CLASSES_FILE), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if os.path.exists(CLASSES_FILE):
                shutil.copy(CLASSES_FILE, os.path.join(backup_dir, f'classes_avant_reset_{timestamp}.json'))
            if os.path.exists(DEVOIRS_FILE):
                shutil.copy(DEVOIRS_FILE, os.path.join(backup_dir, f'devoirs_avant_reset_{timestamp}.json'))
            
            # Réinitialiser les fichiers
            with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
            with open(DEVOIRS_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
            
            # Réinitialiser le lien personnalisé
            set_lien_ent("", "")
            
            # Mettre à jour la page d'accueil si elle existe
            if self.main_window and hasattr(self.main_window, 'page_accueil'):
                self.main_window.page_accueil.update_footer_link()
            
            QMessageBox.information(
                self,
                "Réinitialisation réussie",
                f"Toutes les données ont été supprimées (classes, devoirs et lien personnalisé).\n\nUne sauvegarde a été créée dans :\n{backup_dir}"
            )
            
            # Rafraîchir les pages si possible
            self.rafraichir_pages()
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erreur",
                f"Une erreur est survenue :\n{str(e)}"
            )

    def rafraichir_pages(self):
        """Rafraîchit toutes les pages pour recharger les données"""
        if self.main_window:
            # Recharger la page des classes si elle existe
            if hasattr(self.main_window, 'page_classes') and self.main_window.page_classes:
                # Récupérer le widget ClassesWidget
                for i in range(self.main_window.page_classes.layout().count()):
                    widget = self.main_window.page_classes.layout().itemAt(i).widget()
                    if widget and hasattr(widget, 'charger_classes_from_utils'):
                        widget.charger_classes_from_utils()
                        break
            
            # Recharger la page des devoirs si elle existe
            if hasattr(self.main_window, 'page_devoirs') and self.main_window.page_devoirs:
                # Récupérer le widget DevoirsWidget
                for i in range(self.main_window.page_devoirs.layout().count()):
                    widget = self.main_window.page_devoirs.layout().itemAt(i).widget()
                    if widget and hasattr(widget, 'charger_devoirs_from_utils'):
                        widget.charger_devoirs_from_utils()
                        widget.charger_classes_from_utils()
                        break

    def modifier_lien_ent(self):
        """Modifie le lien personnalisé de la page d'accueil"""
        from PySide6.QtWidgets import QDialog, QLineEdit
        
        # Charger le lien actuel
        lien_actuel = get_lien_ent()
        
        # Créer une boîte de dialogue
        dialog = QDialog(self)
        dialog.setWindowTitle("Modifier le lien personnalisé")
        dialog.setFixedSize(500, 200)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Champ URL
        url_label = QLabel("URL du lien :")
        layout.addWidget(url_label)
        
        url_input = QLineEdit()
        url_input.setText(lien_actuel.get("url", ""))
        url_input.setPlaceholderText("https://exemple.com")
        layout.addWidget(url_input)
        
        # Champ Texte
        texte_label = QLabel("Texte affiché :")
        layout.addWidget(texte_label)
        
        texte_input = QLineEdit()
        texte_input.setText(lien_actuel.get("texte", ""))
        texte_input.setPlaceholderText("Mon lien")
        layout.addWidget(texte_input)
        
        # Boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        btn_annuler = QPushButton("Annuler")
        btn_annuler.setFixedSize(120, 35)
        btn_annuler.clicked.connect(dialog.reject)
        buttons_layout.addWidget(btn_annuler)
        
        btn_sauvegarder = QPushButton("Sauvegarder")
        btn_sauvegarder.setFixedSize(120, 35)
        btn_sauvegarder.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border-radius: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        btn_sauvegarder.clicked.connect(dialog.accept)
        buttons_layout.addWidget(btn_sauvegarder)
        
        layout.addLayout(buttons_layout)
        dialog.setLayout(layout)
        
        # Afficher le dialogue
        if dialog.exec():
            url = url_input.text().strip()
            texte = texte_input.text().strip()
            
            if url and texte:
                # Sauvegarder
                set_lien_ent(url, texte)
                
                # Mettre à jour la page d'accueil si elle existe
                if self.main_window and hasattr(self.main_window, 'page_accueil'):
                    self.main_window.page_accueil.update_footer_link()
                
                QMessageBox.information(
                    self,
                    "Lien modifié",
                    "Le lien personnalisé a été mis à jour avec succès !\nIl sera visible sur la page d'accueil."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Champs requis",
                    "Veuillez remplir l'URL et le texte du lien."
                )