# utils/gestion.py
import json
import os
from datetime import datetime
from models.Classe import Classe
from models.Devoir import Devoir

# Chemin vers les fichiers JSON
CLASSES_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'classes.json')
DEVOIRS_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'devoirs.json')

def charger_classes():
    """Charge les classes depuis le fichier JSON et retourne une liste d'instances de Classe"""
    if not os.path.exists(CLASSES_FILE):
        return []  # Retourne une liste vide si le fichier n'existe pas

    with open(CLASSES_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Reconstruire les instances de Classe
    classes = []
    for item in data:
        classe = Classe(
            nom=item["nom"],
            effectif=item["effectif"],
            couleur=item.get("couleur", "gris")  # valeur par défaut si absent
        )
        classes.append(classe)

    return classes

def sauvegarder_classes(classes):
    """Sauvegarde une liste d'instances de Classe dans un fichier JSON"""
    # Convertir chaque instance en dictionnaire
    data = []
    for classe in classes:
        data.append({
            "nom": classe.nom,
            "effectif": classe.effectif,
            "couleur": classe.couleur
        })

    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(CLASSES_FILE), exist_ok=True)

    # Sauvegarder dans le fichier
    with open(CLASSES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def charger_devoirs():
    """Charge les devoirs depuis le fichier JSON et retourne une liste d'instances de Devoir"""
    if not os.path.exists(DEVOIRS_FILE):
        return []  # Retourne une liste vide si le fichier n'existe pas

    with open(DEVOIRS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Charger les classes pour les lier aux devoirs
    classes = charger_classes()  # Appel à charger_classes() ici → pas besoin de passer en paramètre
    classes_dict = {classe.nom: classe for classe in classes}  # dictionnaire nom -> objet

    # Reconstruire les instances de Devoir
    devoirs = []
    for item in data:
        classe_objet = classes_dict.get(item["classe_nom"])  # récupère l'objet Classe par nom
        if not classe_objet:
            # Si la classe n'existe pas, on la crée temporairement avec une couleur par défaut
            classe_objet = Classe(nom=item["classe_nom"], effectif=0, couleur="gris")

        devoir = Devoir(
            contenu=item["contenu"],
            classe_objet=classe_objet,
            date=item["date"],
            statut=item["statut"]
        )
        devoirs.append(devoir)

    return devoirs

def sauvegarder_devoirs(devoirs):
    """Sauvegarde une liste d'instances de Devoir dans un fichier JSON"""
    # Convertir chaque instance en dictionnaire
    data = []
    for devoir in devoirs:
        data.append({
            "contenu": devoir.contenu,
            "classe_nom": devoir.classe_objet.nom,  # on stocke le nom, pas l'objet
            "date": devoir.date,
            "statut": devoir.statut
        })

    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(DEVOIRS_FILE), exist_ok=True)

    # Sauvegarder dans le fichier
    with open(DEVOIRS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)