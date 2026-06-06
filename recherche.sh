#!/bin/bash
#
# recherche.sh
# Script Bash de recherche de fichiers contenant un mot-cle.
# Utilise grep pour parcourir recursivement un dossier.

# Recuperation des parametres
DOSSIER=$1
MOT_CLE=$2
RESPECTER_CASSE=$3
AFFICHER_LIGNES=$4
EXTENSION=$5

if [ -z "$DOSSIER" ] || [ -z "$MOT_CLE" ]; then
    echo "Erreur : dossier et mot-cle obligatoires."
    exit 1
fi

if [ ! -d "$DOSSIER" ]; then
    echo "Erreur : le dossier $DOSSIER n'existe pas."
    exit 1
fi

COMMANDE="grep -r -s"

if [ "$RESPECTER_CASSE" = "0" ]; then
    COMMANDE="$COMMANDE -i"
fi

if [ "$AFFICHER_LIGNES" = "1" ]; then
    COMMANDE="$COMMANDE -n"
fi

if [ -n "$EXTENSION" ]; then
    COMMANDE="$COMMANDE --include=*$EXTENSION"
fi

COMMANDE="$COMMANDE $MOT_CLE $DOSSIER"

$COMMANDE 2>/dev/null

exit 0