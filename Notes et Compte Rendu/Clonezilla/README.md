# Mise en place d’un serveur de clonage Clonezilla (DRBL) sur Proxmox

##  Objectif

Mettre en place un **serveur de clonage Clonezilla** accessible via **PXE**, permettant :

* la **capture** d’images système,
* le **stockage centralisé** des images,
* le **déploiement automatisé** sur plusieurs postes,

pour des systèmes **Windows ou Linux**, dans un environnement virtualisé Proxmox.

---

## Environnement cible

| Élément            | Description                                  |
| ------------------ | -------------------------------------------- |
| Hyperviseur        | Proxmox VE                                   |
| VM serveur         | Debian 12 minimal (sans interface graphique) |
| Service de clonage | DRBL / Clonezilla Server                     |
| Clients            | VM ou machines physiques avec boot PXE       |

---

## 1️ Création et configuration de la VM Debian

### 1.1 Création de la VM dans Proxmox

* **OS** : Debian 12 (64 bits)
* **CPU** : 2 vCPU
* **RAM** : 2 à 4 Go
* **Disque système** : 20 Go (SSD recommandé)
* **Disque images** : 50 à 100 Go (dédié au stockage Clonezilla)
* **Carte réseau** : Bridge (ex. `vmbr0`) connecté au LAN
* **Accès console Proxmox** : activé

---

### 1.2 Installation minimale de Debian 12

1. Lancer l’installation depuis l’ISO Debian 12
2. Sélection des logiciels :

   *  Serveur SSH
   *  Utilitaires usuels du système
   * Environnement graphique (GNOME, KDE, XFCE…)
3. Créer un utilisateur avec mot de passe sécurisé
4. Installer **GRUB** sur le disque principal (`/dev/sda` ou `/dev/vda`)
5. Finaliser l’installation et redémarrer

---

### 1.3 Accès initial et mise à jour

Connexion via console Proxmox ou SSH, puis :

```bash
su -
apt update && apt upgrade -y
```

---

## 2️ Installation et configuration de Clonezilla Server (DRBL)

### 2.1 Installation des paquets nécessaires

```bash
apt install drbl clonezilla -y
```

---

### 2.2 Initialisation du serveur DRBL

```bash
drblsrv -i
```

 Accepter toutes les valeurs par défaut.

---

### 2.3 Configuration PXE / DHCP / NFS

```bash
drblpush -i
```

Paramètres recommandés :

* **Mode Clonezilla Server** : Oui
* **DHCP** : Oui (réseau de test isolé)
* **Interface réseau** : ex. `ens18` ou `eth0`
* **Plage DHCP** : `192.168.100.50` → `192.168.100.100`
* **PXE** : Activé
* **Serveur NFS (images)** : Activé
* **Multicast** : Non (optionnel)

Accepter les autres valeurs par défaut.

---

### 2.4 Vérification des services

```bash
systemctl status isc-dhcp-server
systemctl status nfs-server
```

Les services doivent être **actifs** et sans erreur.

---

## 3️ Sécurisation et configuration SSH

### 3.1 Accès SSH

Utiliser un utilisateur avec `sudo` ou autoriser temporairement `root`.

Modifier `/etc/ssh/sshd_config` :

```ini
PermitRootLogin yes
PasswordAuthentication yes
```

Redémarrer le service SSH :

```bash
systemctl restart ssh
```

---

## 4️ Capture d’une image système (poste Master)

### 4.1 Préparation du poste Master

* Installer Windows ou Linux
* Configurer logiciels, paramètres, utilisateurs
* **Windows** : exécuter `Sysprep` avant la capture (obligatoire)

---

### 4.2 Démarrage PXE du poste Master

* Activer le **boot PXE** dans le BIOS / UEFI
* Le menu Clonezilla s’affiche automatiquement

---

### 4.3 Capture de l’image

1. `device-image`
2. `save-disk`
3. Destination : **Serveur NFS**
4. Nom de l’image : `master-windows` ou `master-ubuntu`
5. Lancer la sauvegarde

---

## 5️Déploiement d’une image sur un poste client

### 5.1 Préparation du client

* Boot PXE activé
* Disque vierge ou réinitialisé

---

### 5.2 Restauration de l’image

1. `device-image`
2. `restore-disk`
3. Sélectionner l’image
4. Confirmer le déploiement

---

### 5.3 Vérification

* Démarrage normal du système cloné
* Vérification des fichiers et applications

---

## 6️ Problèmes courants et solutions

| Problème                  | Solution                                              |
| ------------------------- | ----------------------------------------------------- |
| Accès SSH refusé          | Vérifier utilisateurs, mots de passe et `sshd_config` |
| PXE ne démarre pas        | Vérifier DHCP, interface réseau, firewall             |
| Windows non bootable      | `Sysprep` obligatoire avant capture                   |
| Espace disque insuffisant | Ajouter un disque dédié aux images                    |
| Multicast bloqué          | Vérifier switch et configuration DRBL                 |

---

## 7️⃣ Commandes utiles

```bash
# Mise à jour système
apt update && apt upgrade -y

# Installation Clonezilla / DRBL
apt install drbl clonezilla -y

# Configuration DRBL
drblsrv -i
drblpush -i

# Vérification services
systemctl status isc-dhcp-server
systemctl status nfs-server

# Redémarrer SSH
systemctl restart ssh
```

---

## 8️ Résumé pour présentation orale

* Mise en place d’un **serveur Clonezilla** sur Debian minimal
* Fonctionnement **PXE + DHCP + NFS**
* Capture et déploiement d’images système réussis
* Administration **100 % en ligne de commande via SSH**
* Pistes d’amélioration : multicast, optimisation pilotes Windows

---

 *Document prêt pour dépôt GitHub (README.md ou documentation projet)*
