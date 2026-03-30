<?php
// api_blacklist.php

// --- 1. GESTION DES AUTORISATIONS (CORS) ---
// Ces lignes sont cruciales. Elles autorisent ta page web (qui tourne dans un navigateur) 
// à discuter avec ce script PHP. Sans ça, le navigateur bloquerait la requête par sécurité.
header("Access-Control-Allow-Origin: *"); 
header("Access-Control-Allow-Headers: X-Auth-Token, Content-Type"); // On autorise explicitement notre en-tête personnalisé "X-Auth-Token"
header("Access-Control-Allow-Methods: GET, POST, OPTIONS");
header("Content-Type: text/plain; charset=UTF-8");

// Les navigateurs envoient parfois une requête "OPTIONS" avant une requête "POST" 
// pour vérifier que le serveur est d'accord. On lui répond que oui (Code 200).
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit();
}

// --- 2. SÉCURITÉ : VÉRIFICATION DU MOT DE PASSE ---
// ⚠️ REMPLACE CETTE VALEUR PAR TON PROPRE HASH
$hash_enregistre = '$2y$10$731d/KQbH6Kn2tCpRsDwEeJfkT1DXZlosPtAIWkte.M7npGiOmvxO';

// On va chercher le mot de passe en clair que le JavaScript nous a envoyé dans l'en-tête "X-Auth-Token"
$mdp_recu = isset($_SERVER['HTTP_X_AUTH_TOKEN']) ? $_SERVER['HTTP_X_AUTH_TOKEN'] : '';

// password_verify() est la fonction magique : elle prend le mot de passe en clair,
// le hache, et regarde si ça correspond au $hash_enregistre. 
if (!password_verify($mdp_recu, $hash_enregistre)) {
    http_response_code(401); // 401 signifie "Non autorisé"
    die("Accès refusé : mot de passe incorrect."); // On coupe tout ici si le mdp est faux.
}

// --- 3. LECTURE ET ÉCRITURE DU FICHIER ---
$fichier_conf = 'blacklistoffi.conf';

// LIRE LE FICHIER (Méthode GET)
if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    if (file_exists($fichier_conf)) {
        // file_get_contents lit tout le contenu du fichier d'un coup et l'envoie à la page web
        echo file_get_contents($fichier_conf);
    } else {
        echo ""; 
    }
}

// MODIFIER LE FICHIER (Méthode POST)
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // php://input permet de lire les données brutes envoyées par le "body" de la requête JS (notre nouvelle liste)
    $nouvelles_donnees = file_get_contents("php://input");
    
    // file_put_contents écrase l'ancien fichier avec $nouvelles_donnees. 
    // Si ça retourne "false", c'est souvent un problème de permissions (chmod/chown) sur le serveur.
    if (file_put_contents($fichier_conf, $nouvelles_donnees) !== false) {
        http_response_code(200); // 200 = OK
        echo "Sauvegarde réussie";
    } else {
        http_response_code(500); // 500 = Erreur interne du serveur
        echo "Erreur d'écriture sur le serveur.";
    }
}
?>
