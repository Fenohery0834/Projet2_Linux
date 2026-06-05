"""
ouvrier.py

Thread de recherche non-bloquant.
"""

import os
import threading
from datetime import datetime


class SearchWorker:

    def __init__(self, dossier, mot_cle, extensions,
                 afficher_lignes, respecter_casse,
                 rappel_resultat, rappel_termine, rappel_erreur):

        self.dossier          = dossier
        self.mot_cle          = mot_cle
        self.extensions       = extensions
        self.afficher_lignes  = afficher_lignes
        self.respecter_casse  = respecter_casse

        # Fonctions de rappel appelees depuis le thread
        self.rappel_resultat  = rappel_resultat
        self.rappel_termine   = rappel_termine
        self.rappel_erreur    = rappel_erreur

        self._arreter  = False
        self._thread   = threading.Thread(target=self._executer, daemon=True)

    # Controle du thread

    def demarrer(self):
        self._thread.start()

    def arreter(self):
        self._arreter = True

    def est_en_cours(self):
        return self._thread.is_alive()

    # Collecte des fichiers

    def _collecter_fichiers(self):
        liste_fichiers = []
        try:
            for dossier_racine, _, noms in os.walk(self.dossier):
                if self._arreter:
                    break
                for nom in noms:
                    if self.extensions:
                        extension = os.path.splitext(nom)[1].lower()
                        if extension not in self.extensions:
                            continue
                    liste_fichiers.append(
                        os.path.join(dossier_racine, nom)
                    )
        except PermissionError:
            self.rappel_erreur("Permission refusee : " + self.dossier)
        return liste_fichiers

    # Analyse d'un fichier

    def _chercher_dans_fichier(self, chemin_fichier, mot_cle):
        correspondance_trouvee = False
        try:
            fichier = open(chemin_fichier, "r",
                           encoding="utf-8", errors="replace")
            numero_ligne = 0
            for ligne in fichier:
                numero_ligne = numero_ligne + 1

                if self.respecter_casse:
                    ligne_test = ligne
                else:
                    ligne_test = ligne.lower()

                if mot_cle not in ligne_test:
                    continue

                if not correspondance_trouvee:
                    correspondance_trouvee = True

                if self.afficher_lignes:
                    self.rappel_resultat(
                        chemin_fichier, numero_ligne, ligne.rstrip()
                    )
                else:
                    self.rappel_resultat(chemin_fichier, 0, "")
                    break   # chemin seulement, inutile de lire la suite
            fichier.close()
        except PermissionError:
            pass
        except OSError:
            pass
        return correspondance_trouvee

    # Boucle principale

    def _executer(self):
        heure_debut      = datetime.now()
        nombre_trouves   = 0

        if self.respecter_casse:
            mot_cle_recherche = self.mot_cle
        else:
            mot_cle_recherche = self.mot_cle.lower()

        liste_fichiers = self._collecter_fichiers()

        for chemin_fichier in liste_fichiers:
            if self._arreter:
                break
            if self._chercher_dans_fichier(chemin_fichier, mot_cle_recherche):
                nombre_trouves = nombre_trouves + 1

        duree = (datetime.now() - heure_debut).total_seconds()
        self.rappel_termine(nombre_trouves, duree)
