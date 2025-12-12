class Classe:
    def __init__(self, nom, effectif, couleur="gris"):
        self.nom = nom
        self.effectif = self._valider_effectif(effectif)
        self.couleur = couleur

    def _valider_effectif(self, effectif):
        """Valide que l'effectif est un nombre entier positif."""
        if not isinstance(effectif, int) or effectif < 0:
            raise ValueError("L'effectif doit être un entier positif ou nul.")
        return effectif

    def afficher(self):
        return f"Classe : {self.nom} | Effectif : {self.effectif} | Couleur : {self.couleur}"

    def modifier_effectif(self, nouvel_effectif):
        self.effectif = self._valider_effectif(nouvel_effectif)

    def modifier_couleur(self, nouvelle_couleur):
        self.couleur = nouvelle_couleur