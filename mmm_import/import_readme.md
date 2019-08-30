Import des données MMM
======================

Procédure
---------

Données Excel :
- Editer import.xlsx avec les vraies données (voir chapitre abonnements et invitations pour l'ajout de ces données)
- Supprimer les lignes de 1 et 2
- Sauvegarder chacun des tableaux en CSV standard (séparateur point-virgule)
- Excel sauve le fichier en latin-1, le transformer en UTF-8
- Importer le fichier CSV dans le script JavaScript
- Remplacer le contenu du CSV avec ce qui est généré par le script

Module MMM Import :
- Mettre à jour le modèle res.partner du module mmm_import (voir chapitre abonnements)

Installation des modules nécessaires :
- Installer partner_customer_state
- Installer partner_gender
- Installer le module partner_firstname_surname
- Installer le module mmm_import

Création des données nécssaires :
- Créer les templates d'abonnements nécessaires et leurs produits dans Odoo (voir chapitre abonnements)
- Créer les secteurs d'activité, titres, invitations nécessaires
- Installer les langues nécessaires

Import :
- Importer le CSV dans Odoo en précisant "point-virgule" pour le séparateur
- Cliquer une fois sur "Compute MMM" sur un contact au hasard
- Désinstaller le module mmm_import

Abonnements
-----------

Pour le moment il n'y a qu'un exemple d'abonnement dans la procédure (champ : mmm_sub_test, template : Sub Test Template).
Pour abonner des usagers :
- Donner un nom de champ au type d'abonnement (par exemple mmm_sub_type1) et le placer :
	- Dans une nouvelle colonne de l'excel en précisant TRUE pour les partenaires abonnés ou bien la langue pour les abonnements à plusieurs langues.
	- En ajoutant un champ dans le modèle res.partner du module mmm_import (char si plusieurs langues, bool sinon)
	- En ajoutant les lignes suivantes aux alentous des lignes 26-53 :
		`if partner.<nom champ>:`
        `    subs.append({`
        `        'template': <nom du template>,`
        `        'language': partner.<nom champ>, <= Ou bien juste le code de langue en dur si le champ est un bool`
        `        'free': <abonnement gratuit ou non>,`
        `        'company': <code de la compagnie liée aux abonnements>`
        `    })`
    => Les correspondances Code <=> Langue et Code <=> Compagnie se trouvent un peu plus bas dans le même fichier en cas de besoin

Invitations
-----------

2 Colonnes calculées on été faites à titre d'exemple, il faut créer les colonnes calculées relatives à chaque abonnement (nom de l'abonnement suivi d'une virgule). A pres les abonnements, une colonne concatennant toutes les invitations est à mettre à jour aussi
