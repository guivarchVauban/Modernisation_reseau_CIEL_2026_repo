Intégration des classes et utilisateurs sur SambaEdu 


SambaÉdu utilise un annuaire LDAP pour gérer les droits. La création d'une "Classe" est une étape cruciale car elle génère automatiquement les partages réseaux nécessaires (Dossier d'échange, dossiers personnels, etc.).
1. Création d'une Classe (Groupe)
Pour qu'une classe existe dans le système, elle doit d'abord être créée en tant que groupe dans l'annuaire.
Procédure (voir image "Import CIEL_2") :
Connectez-vous à l'interface de SambaÉdu avec un compte administrateur.
Dans le menu de gauche, allez dans Annuaire > Ajout d'un groupe.
Préfixe : Vous pouvez laisser vide ou mettre un préfixe court (ex: LP).
Catégorie : Sélectionnez impérativement Classe dans le menu déroulant.
Intitulé : Saisissez le nom de la classe (ex: CIEL_2).
Cliquez sur le bouton Lancer.












2. Initialisation des ressources de la classe
Une fois le groupe créé dans l'annuaire, il faut générer les dossiers partagés sur le serveur de fichiers.
Procédure (voir image "Creation des classes") :
Allez dans le menu Gestion des partages > Répertoires Classes.
Si la classe vient d'être créée, elle devrait apparaître dans la colonne "Classes à créer".
Cochez la classe correspondante (ex: CIEL_2) et validez.
Si la classe est déjà créée mais que vous voulez réinitialiser les droits, utilisez la colonne "Partages classes existants", sélectionnez la classe, cochez "Rafraîchir" et cliquez sur Valider.
Note : Cela créera automatiquement l'arborescence /var/sambaedu/Classes/Classe_CIEL_2.











3. Ajout et Importation d'Utilisateurs
Il existe deux méthodes principales pour ajouter des utilisateurs (élèves ou professeurs) :
A. Ajout manuel (pour un utilisateur unique)
Allez dans Annuaire > Ajout d'un utilisateur.
Remplissez les champs (Nom, Prénom, Sexe).
Dans la section "Groupes", affectez l'utilisateur à sa classe (ex: Classe_CIEL_2).
Validez pour générer ses identifiants.
B. Importation en masse (Méthode recommandée)
SambaÉdu permet d'importer les comptes directement depuis les fichiers Siècle (pour les élèves) ou STS Web (pour les professeurs).
Allez dans Annuaire > Importation Sconet/Siècle.
Téléversez le fichier XML fourni par l'administration de l'établissement.
Le système créera automatiquement :
Les comptes utilisateurs.
Les groupes de classes.
Les appartenances (élèves dans les bonnes classes).












4. Points de vigilance (Conseils issus de la documentation officielle)
Synchronisation : Après une création massive, il est conseillé de vérifier dans Gestion des parages que les répertoires personnels ont bien été créés.
Mots de passe : Lors du premier import, un mot de passe provisoire (souvent la date de naissance au format AAAAMMJJ) est attribué. L'utilisateur devra le changer à la première connexion.
Suppression : Ne supprimez jamais un utilisateur manuellement dans les dossiers Windows. Passez toujours par l'interface SambaÉdu (Annuaire > Rechercher) pour que le nettoyage se fasse proprement dans le LDAP et sur le disque.



