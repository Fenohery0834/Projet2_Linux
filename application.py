"""
application.py

Interface graphique Tkinter de Check_file.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime

import configuration as config
from ouvrier import SearchWorker


# ParamsPanel -- formulaire de saisie des parametres de recherche

class ParamsPanel(tk.Frame):

    TEXTE_PLACEHOLDER = "Entrez un mot-cle..."

    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        theme = config.THEME
        self.configure(bg=theme["bg2"])
        self.historique_mots_cles = []
        self._construire()

    def _titre_section(self, texte):
        theme = config.THEME
        etiquette = tk.Label(
            self, text=texte,
            font=("Courier New", 8, "bold"),
            bg=theme["bg2"], fg=theme["text3"]
        )
        etiquette.pack(anchor="w", pady=(14, 3))

    def _ligne_separation(self):
        theme = config.THEME
        separateur = tk.Frame(self, bg=theme["border"], height=1)
        separateur.pack(fill="x", pady=10)

    # Construction principale

    def _construire(self):
        theme = config.THEME

        # Mot-cle
        self._titre_section("MOT-CLE")
        self.variable_mot_cle = tk.StringVar()
        self.entree_mot_cle = ttk.Combobox(
            self,
            textvariable=self.variable_mot_cle,
            font=("Courier New", 12),
            values=[],
        )
        self.entree_mot_cle.pack(fill="x", ipady=4)
        self._afficher_placeholder()

        self.entree_mot_cle.bind("<FocusIn>",  self._focus_entree_mot_cle)
        self.entree_mot_cle.bind("<FocusOut>", self._focus_sortie_mot_cle)

        # Dossier cible
        self._titre_section("REPERTOIRE CIBLE")
        ligne_dossier = tk.Frame(self, bg=theme["bg2"])
        ligne_dossier.pack(fill="x")

        self.entree_dossier = tk.Entry(
            ligne_dossier,
            font=("Courier New", 11),
            bg=theme["entry_bg"], fg=theme["entry_fg"],
            relief="flat", bd=0,
        )
        self.entree_dossier.insert(0, config.DEFAULT_DIRECTORY)
        self.entree_dossier.pack(
            side="left", fill="x", expand=True, ipady=7
        )

        bouton_parcourir = tk.Button(
            ligne_dossier, text="[...]",
            font=("Courier New", 11),
            bg=theme["btn_bg"], fg=theme["text2"],
            relief="flat", bd=0, padx=8,
            cursor="hand2",
            command=self._parcourir_dossier,
        )
        bouton_parcourir.pack(side="left", padx=(6, 0))

        self._ligne_separation()

        # Filtre extension
        self._titre_section("FILTRE EXTENSION")
        self.variable_extension = tk.StringVar(value=config.EXTENSIONS[0])
        self.liste_extensions = ttk.Combobox(
            self,
            textvariable=self.variable_extension,
            values=config.EXTENSIONS,
            font=("Courier New", 11),
            state="readonly",
        )
        self.liste_extensions.pack(fill="x", ipady=4)

        self._ligne_separation()

        # Options
        self._titre_section("OPTIONS")
        self.variable_afficher_lignes = tk.BooleanVar(value=True)
        self.variable_respecter_casse = tk.BooleanVar(value=False)

        style_case = {
            "bg":               theme["bg2"],
            "fg":               theme["text"],
            "selectcolor":      theme["bg3"],
            "activebackground": theme["bg2"],
            "activeforeground": theme["text"],
            "font":             ("Courier New", 11),
            "relief":           "flat",
            "bd":               0,
            "cursor":           "hand2",
            "highlightthickness": 0,
        }

        self.case_afficher_lignes = tk.Checkbutton(
            self, text="  Afficher les lignes",
            variable=self.variable_afficher_lignes,
            **style_case
        )
        self.case_afficher_lignes.pack(anchor="w", pady=5)

        self.case_respecter_casse = tk.Checkbutton(
            self, text="  Respecter la casse",
            variable=self.variable_respecter_casse,
            **style_case
        )
        self.case_respecter_casse.pack(anchor="w", pady=5)

    # Placeholder

    def _afficher_placeholder(self):
        theme = config.THEME
        self.variable_mot_cle.set(self.TEXTE_PLACEHOLDER)
        self.entree_mot_cle.configure(foreground=theme["text3"])

    def _focus_entree_mot_cle(self, evenement=None):
        if self.variable_mot_cle.get() == self.TEXTE_PLACEHOLDER:
            self.variable_mot_cle.set("")
            theme = config.THEME
            self.entree_mot_cle.configure(foreground=theme["entry_fg"])

    def _focus_sortie_mot_cle(self, evenement=None):
        if not self.variable_mot_cle.get().strip():
            self._afficher_placeholder()

    # Historique des mots-cles

    def ajouter_historique(self, mot_cle):
        if mot_cle in self.historique_mots_cles:
            self.historique_mots_cles.remove(mot_cle)
        self.historique_mots_cles.insert(0, mot_cle)
        if len(self.historique_mots_cles) > config.KEYWORD_HISTORY_MAX:
            self.historique_mots_cles.pop()
        self.entree_mot_cle.configure(values=self.historique_mots_cles)

    # Parcours dossier

    def _parcourir_dossier(self):
        dossier_choisi = filedialog.askdirectory(
            initialdir=self.entree_dossier.get() or "/"
        )
        if dossier_choisi:
            self.entree_dossier.delete(0, "end")
            self.entree_dossier.insert(0, dossier_choisi)

    # Accesseurs simples

    def get_mot_cle(self):
        mot_cle = self.variable_mot_cle.get().strip()
        if mot_cle == self.TEXTE_PLACEHOLDER:
            return ""
        return mot_cle

    def get_dossier(self):
        return self.entree_dossier.get().strip()

    def get_extensions(self):
        extension = self.variable_extension.get()
        if extension.startswith("Tous"):
            return []
        return [extension.lower()]

    def get_afficher_lignes(self):
        return self.variable_afficher_lignes.get()

    def get_respecter_casse(self):
        return self.variable_respecter_casse.get()


# ResultsPanel -- zone d'affichage coloree

class ResultsPanel(tk.Frame):

    # Noms des tags de couleur
    TAG_FICHIER       = "fichier"
    TAG_CORRESPONDANCE = "correspondance"
    TAG_CONTEXTE      = "contexte"
    TAG_META          = "meta"
    TAG_ERREUR        = "erreur"

    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.liste_lignes = []
        self._construire()

    def _construire(self):
        theme = config.THEME
        self.configure(bg=theme["bg2"])

        self.zone_texte = tk.Text(
            self,
            font=("Courier New", 11),
            bg=theme["bg2"], fg=theme["text2"],
            relief="flat", bd=0,
            wrap="none", state="disabled",
            padx=14, pady=14,
        )

        barre_verticale   = ttk.Scrollbar(self, orient="vertical",
                                          command=self.zone_texte.yview)
        barre_horizontale = ttk.Scrollbar(self, orient="horizontal",
                                          command=self.zone_texte.xview)
        self.zone_texte.configure(
            yscrollcommand=barre_verticale.set,
            xscrollcommand=barre_horizontale.set
        )

        barre_verticale.pack(side="right",  fill="y")
        barre_horizontale.pack(side="bottom", fill="x")
        self.zone_texte.pack(side="left", fill="both", expand=True)

        self._configurer_tags()

    def _configurer_tags(self):
        theme = config.THEME
        self.zone_texte.tag_configure(
            self.TAG_FICHIER,
            foreground=theme["result_file"],
            font=("Courier New", 11, "bold")
        )
        self.zone_texte.tag_configure(
            self.TAG_CORRESPONDANCE,
            foreground=theme["result_match"]
        )
        self.zone_texte.tag_configure(
            self.TAG_CONTEXTE,
            foreground=theme["result_ctx"]
        )
        self.zone_texte.tag_configure(
            self.TAG_META,
            foreground=theme["result_meta"]
        )
        self.zone_texte.tag_configure(
            self.TAG_ERREUR,
            foreground=theme["result_err"]
        )

    # API publique

    def effacer(self):
        self.liste_lignes = []
        self.zone_texte.configure(state="normal")
        self.zone_texte.delete("1.0", "end")
        self.zone_texte.configure(state="disabled")

    def ajouter_meta(self, texte):
        self._ajouter_ligne(texte + "\n", self.TAG_META)

    def ajouter_fichier(self, chemin):
        self._ajouter_ligne("\n  >> %s\n" % chemin, self.TAG_FICHIER)

    def ajouter_correspondance(self, numero_ligne, contenu):
        self._ajouter_ligne(
            "       L%4d  |  %s\n" % (numero_ligne, contenu),
            self.TAG_CORRESPONDANCE
        )

    def ajouter_contexte(self, numero_ligne, contenu):
        self._ajouter_ligne(
            "       L%4d  |  %s\n" % (numero_ligne, contenu),
            self.TAG_CONTEXTE
        )

    def ajouter_erreur(self, message):
        self._ajouter_ligne("  [ERR]  %s\n" % message, self.TAG_ERREUR)

    def contient_resultats(self):
        return len(self.liste_lignes) > 0

    def get_texte_brut(self):
        return "".join(self.liste_lignes)

    def _ajouter_ligne(self, ligne, tag):
        self.liste_lignes.append(ligne)
        self.zone_texte.configure(state="normal")
        self.zone_texte.insert("end", ligne, tag)
        self.zone_texte.see("end")
        self.zone_texte.configure(state="disabled")


# MainWindow -- fenetre principale

class MainWindow:

    def __init__(self, fenetre_principale):
        self.fenetre_principale = fenetre_principale
        self.worker             = None
        self.nombre_trouves     = 0

        self.fenetre_principale.title(
            "%s  v%s" % (config.APP_NAME, config.APP_VERSION)
        )
        self.fenetre_principale.minsize(1000, 680)
        self.fenetre_principale.geometry("1160x760")

        # Raccourcis clavier
        self.fenetre_principale.bind("<Escape>", self._sur_echap)
        self.fenetre_principale.bind("<F5>",     self._sur_f5)

        self._construire_interface()

    # Raccourcis clavier

    def _sur_echap(self, evenement=None):
        self._arreter_recherche()

    def _sur_f5(self, evenement=None):
        self._lancer_recherche()

    # Construction de l'interface

    def _construire_interface(self):
        theme = config.THEME

        # Barre de statut en bas
        self.variable_statut = tk.StringVar(
            value="Pret  --  %s v%s  |  F5 : Rechercher  |  Echap : Arreter"
                  % (config.APP_NAME, config.APP_VERSION)
        )
        self.barre_statut = tk.Label(
            self.fenetre_principale,
            textvariable=self.variable_statut,
            font=("Courier New", 9), anchor="w",
            bg=theme["bg3"], fg=theme["text3"],
            padx=16, pady=5,
        )
        self.barre_statut.pack(side="bottom", fill="x")

        # Sidebar gauche
        panneau_gauche = tk.Frame(
            self.fenetre_principale, bg=theme["bg2"], width=280
        )
        panneau_gauche.pack(side="left", fill="y")
        panneau_gauche.pack_propagate(False)

        # Logo
        cadre_logo = tk.Frame(panneau_gauche, bg=theme["bg2"])
        cadre_logo.pack(fill="x", padx=20, pady=(24, 0))

        etiquette_nom = tk.Label(
            cadre_logo,
            text=config.APP_NAME.upper(),
            font=("Courier New", 16, "bold"),
            bg=theme["bg2"], fg=theme["text"]
        )
        etiquette_nom.pack(anchor="w")

        etiquette_description = tk.Label(
            cadre_logo,
            text="Recherche de fichiers specifiques",
            font=("Courier New", 9),
            bg=theme["bg2"], fg=theme["text3"]
        )
        etiquette_description.pack(anchor="w")

        separateur_haut = tk.Frame(panneau_gauche, bg=theme["border"], height=1)
        separateur_haut.pack(fill="x", padx=20, pady=16)

        # Boutons en bas de sidebar
        cadre_boutons = tk.Frame(panneau_gauche, bg=theme["bg2"])
        cadre_boutons.pack(side="bottom", fill="x", padx=20, pady=(0, 20))

        separateur_bas = tk.Frame(panneau_gauche, bg=theme["border"], height=1)
        separateur_bas.pack(side="bottom", fill="x", padx=20, pady=12)

        # Formulaire
        self.panneau_params = ParamsPanel(panneau_gauche)
        self.panneau_params.pack(fill="both", expand=True, padx=20)

        self.panneau_params.entree_mot_cle.bind("<Return>", self._sur_f5)
        self.panneau_params.entree_dossier.bind("<Return>", self._sur_f5)

        # Bouton RECHERCHER
        self.bouton_rechercher = tk.Button(
            cadre_boutons,
            text="[ RECHERCHER ]",
            font=("Courier New", 12, "bold"),
            bg=theme["btn_search_bg"], fg=theme["btn_search_fg"],
            relief="flat", bd=0, pady=12,
            cursor="hand2",
            command=self._lancer_recherche,
        )
        self.bouton_rechercher.pack(fill="x")

        # Bouton ARRETER
        self.bouton_arreter = tk.Button(
            cadre_boutons,
            text="[ Arreter ]",
            font=("Courier New", 11),
            bg=theme["btn_stop_bg"], fg=theme["btn_stop_fg"],
            relief="flat", bd=0, pady=8,
            cursor="hand2",
            state="disabled",
            command=self._arreter_recherche,
        )
        self.bouton_arreter.pack(fill="x", pady=(8, 0))

        # Zone principale droite
        panneau_principal = tk.Frame(self.fenetre_principale, bg=theme["bg"])
        panneau_principal.pack(side="left", fill="both", expand=True)

        # Barre superieure
        barre_superieure = tk.Frame(panneau_principal, bg=theme["bg"])
        barre_superieure.pack(fill="x", padx=20, pady=(20, 0))

        cadre_compteur = tk.Frame(barre_superieure, bg=theme["bg"])
        cadre_compteur.pack(side="left")

        self.etiquette_compteur = tk.Label(
            cadre_compteur, text="0",
            font=("Courier New", 26, "bold"),
            bg=theme["bg"], fg=theme["text"]
        )
        self.etiquette_compteur.pack(anchor="w")

        etiquette_sous_compteur = tk.Label(
            cadre_compteur, text="FICHIERS TROUVES",
            font=("Courier New", 8),
            bg=theme["bg"], fg=theme["text3"]
        )
        etiquette_sous_compteur.pack(anchor="w")

        # Boutons utilitaires
        cadre_utilitaires = tk.Frame(barre_superieure, bg=theme["bg"])
        cadre_utilitaires.pack(side="right")

        self.bouton_effacer = tk.Button(
            cadre_utilitaires, text="[x] Effacer",
            font=("Courier New", 10),
            bg=theme["btn_clear_bg"], fg=theme["btn_clear_fg"],
            relief="flat", bd=0, padx=12, pady=6,
            cursor="hand2", state="disabled",
            command=self._effacer_resultats,
        )
        self.bouton_effacer.pack(side="left", padx=4)

        self.bouton_exporter = tk.Button(
            cadre_utilitaires, text="[v] Exporter .txt",
            font=("Courier New", 10),
            bg=theme["btn_export_bg"], fg=theme["btn_export_fg"],
            relief="flat", bd=0, padx=12, pady=6,
            cursor="hand2", state="disabled",
            command=self._exporter_resultats,
        )
        self.bouton_exporter.pack(side="left", padx=4)

        separateur_milieu = tk.Frame(
            panneau_principal, bg=theme["border"], height=1
        )
        separateur_milieu.pack(fill="x", padx=20, pady=10)

        # Zone de resultats
        self.panneau_resultats = ResultsPanel(panneau_principal)
        self.panneau_resultats.pack(fill="both", expand=True, padx=20, pady=12)

    # Recherche

    def _lancer_recherche(self):
        mot_cle = self.panneau_params.get_mot_cle()
        dossier = self.panneau_params.get_dossier()

        if not mot_cle:
            self.variable_statut.set("[!]  Mot-cle manquant.")
            self.panneau_params.entree_mot_cle.focus_set()
            return
        if not dossier or not os.path.isdir(dossier):
            self.variable_statut.set("[!]  Repertoire invalide.")
            self.panneau_params.entree_dossier.focus_set()
            return

        self.panneau_params.ajouter_historique(mot_cle)
        self.nombre_trouves = 0
        self.etiquette_compteur.config(text="0")
        self.panneau_resultats.effacer()
        self._definir_etat(recherche_en_cours=True)
        self._afficher_entete(mot_cle, dossier)

        # Creation du worker de recherche
        self.worker = SearchWorker(
            dossier          = dossier,
            mot_cle          = mot_cle,
            extensions       = self.panneau_params.get_extensions(),
            afficher_lignes  = self.panneau_params.get_afficher_lignes(),
            respecter_casse  = self.panneau_params.get_respecter_casse(),
            rappel_resultat  = self._envelopper(self._sur_resultat),
            rappel_termine   = self._envelopper(self._sur_termine),
            rappel_erreur    = self._envelopper(self._sur_erreur),
        )
        self.worker.demarrer()
        self.variable_statut.set(
            "Recherche de << %s >> dans %s..." % (mot_cle, dossier)
        )

    def _envelopper(self, fonction_rappel):
        def executeur(*arguments):
            self.fenetre_principale.after(0, fonction_rappel, *arguments)
        return executeur

    def _arreter_recherche(self):
        if self.worker and self.worker.est_en_cours():
            self.worker.arreter()
            self.variable_statut.set("[x]  Recherche interrompue.")
            self._definir_etat(recherche_en_cours=False)

    def _effacer_resultats(self):
        self.panneau_resultats.effacer()
        self.nombre_trouves = 0
        self.etiquette_compteur.config(text="0")
        self.bouton_effacer.config(state="disabled")
        self.bouton_exporter.config(state="disabled")
        self.variable_statut.set("Resultats effaces.")

    def _sur_resultat(self, chemin_fichier, numero_ligne, contenu):
        if numero_ligne == 0:
            self.panneau_resultats.ajouter_fichier(chemin_fichier)
            self.nombre_trouves = self.nombre_trouves + 1
        elif numero_ligne == 1:
            self.panneau_resultats.ajouter_fichier(chemin_fichier)
            self.panneau_resultats.ajouter_correspondance(numero_ligne, contenu)
            self.nombre_trouves = self.nombre_trouves + 1
        else:
            self.panneau_resultats.ajouter_contexte(numero_ligne, contenu)
        self.etiquette_compteur.config(text=str(self.nombre_trouves))

    def _sur_termine(self, nombre_trouves, duree):
        self._definir_etat(recherche_en_cours=False)
        separateur = "-" * 60
        self.panneau_resultats.ajouter_meta(
            "\n%s\n  Termine -- %d fichier(s) en %.2fs\n%s"
            % (separateur, nombre_trouves, duree, separateur)
        )
        self.variable_statut.set(
            "[ok]  Termine  --  %d fichier(s) en %.2fs"
            % (nombre_trouves, duree)
        )

    def _sur_erreur(self, message):
        self.panneau_resultats.ajouter_erreur(message)
        self.variable_statut.set("Erreur : " + message)

    # Etat de l'interface

    def _definir_etat(self, recherche_en_cours):
        if recherche_en_cours:
            self.bouton_rechercher.config(state="disabled")
            self.bouton_arreter.config(state="normal")
            self.panneau_params.entree_mot_cle.config(state="disabled")
            self.panneau_params.entree_dossier.config(state="disabled")
            self.panneau_params.liste_extensions.config(state="disabled")
        else:
            self.bouton_rechercher.config(state="normal")
            self.bouton_arreter.config(state="disabled")
            self.panneau_params.entree_mot_cle.config(state="normal")
            self.panneau_params.entree_dossier.config(state="normal")
            self.panneau_params.liste_extensions.config(state="readonly")

        contient_resultats = self.panneau_resultats.contient_resultats()
        if contient_resultats and not recherche_en_cours:
            self.bouton_exporter.config(state="normal")
            self.bouton_effacer.config(state="normal")
        else:
            self.bouton_exporter.config(state="disabled")
            self.bouton_effacer.config(state="disabled")

    # Export

    def _exporter_resultats(self):
        maintenant = datetime.now().strftime("%Y%m%d_%H%M%S")
        chemin_sauvegarde = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="check_file_%s.txt" % maintenant,
            filetypes=[("Fichiers texte", "*.txt")],
        )
        if not chemin_sauvegarde:
            return
        try:
            fichier_sortie = open(chemin_sauvegarde, "w", encoding="utf-8")
            fichier_sortie.write(self.panneau_resultats.get_texte_brut())
            fichier_sortie.close()
            self.variable_statut.set("[ok]  Exporte : " + chemin_sauvegarde)
            messagebox.showinfo(
                "Export reussi",
                "Fichier sauvegarde :\n" + chemin_sauvegarde
            )
        except OSError as erreur:
            messagebox.showerror("Erreur d'export", str(erreur))

    # En-tete de recherche

    def _afficher_entete(self, mot_cle, dossier):
        maintenant = datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        extension  = self.panneau_params.variable_extension.get()
        separateur = "-" * 60
        self.panneau_resultats.ajouter_meta(separateur)
        self.panneau_resultats.ajouter_meta(
            "  %s v%s  --  %s"
            % (config.APP_NAME, config.APP_VERSION, maintenant)
        )
        self.panneau_resultats.ajouter_meta("  Mot-cle    : %s" % mot_cle)
        self.panneau_resultats.ajouter_meta("  Repertoire : %s" % dossier)
        self.panneau_resultats.ajouter_meta("  Extension  : %s" % extension)
        self.panneau_resultats.ajouter_meta(separateur)
        self.panneau_resultats.ajouter_meta("")
        
