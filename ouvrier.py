"""
ouvrier.py

Thread de recherche non-bloquant.
Appelle le script Bash recherche.sh.
"""

import os
import subprocess
import threading
from datetime import datetime


class SearchWorker:

    def __init__(self, dossier, mot_cle, extensions,
                 afficher_lignes, respecter_casse,
                 rappel_resultat, rappel_termine, rappel_erreur):

        self.dossier         = dossier
        self.mot_cle         = mot_cle
        self.extensions      = extensions
        self.afficher_lignes = afficher_lignes
        self.respecter_casse = respecter_casse
        self.rappel_resultat = rappel_resultat
        self.rappel_termine  = rappel_termine
        self.rappel_erreur   = rappel_erreur

        self._arreter = False
        self._thread  = threading.Thread(
            target=self._executer, daemon=True)

    def demarrer(self):
        self._thread.start()

    def arreter(self):
        self._arreter = True

    def est_en_cours(self):
        return self._thread.is_alive()

    def _executer(self):
        heure_debut     = datetime.now()
        nombre_trouves  = 0
        fichier_courant = ""

        dossier_script = os.path.dirname(os.path.abspath(__file__))
        chemin_script  = os.path.join(dossier_script, "recherche.sh")

        if not os.path.isfile(chemin_script):
            self.rappel_erreur("Script introuvable : " + chemin_script)
            return

        commande = [
            "bash", chemin_script,
            self.dossier,
            self.mot_cle,
            "1" if self.respecter_casse  else "0",
            "1" if self.afficher_lignes  else "0",
            self.extensions[0] if self.extensions else ""
        ]

        try:
            processus = subprocess.Popen(
                commande,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True
            )

            for ligne_resultat in processus.stdout:
                if self._arreter:
                    processus.terminate()
                    break

                ligne_resultat = ligne_resultat.rstrip()
                if not ligne_resultat:
                    continue

                if self.afficher_lignes:
                    parties = ligne_resultat.split(":", 2)
                    if len(parties) >= 3:
                        chemin       = parties[0]
                        numero_ligne = int(parties[1])
                        contenu      = parties[2]
                        if chemin != fichier_courant:
                            fichier_courant = chemin
                            self.rappel_resultat(chemin, 1, contenu)
                            nombre_trouves = nombre_trouves + 1
                        else:
                            self.rappel_resultat(
                                chemin, numero_ligne, contenu)
                else:
                    chemin = ligne_resultat.split(":", 1)[0]
                    if chemin != fichier_courant:
                        fichier_courant = chemin
                        self.rappel_resultat(chemin, 0, "")
                        nombre_trouves = nombre_trouves + 1

            processus.wait()

        except FileNotFoundError:
            self.rappel_erreur("Bash introuvable sur ce systeme.")
        except OSError as erreur:
            self.rappel_erreur("Erreur : " + str(erreur))

        duree = (datetime.now() - heure_debut).total_seconds()
        self.rappel_termine(nombre_trouves, duree)