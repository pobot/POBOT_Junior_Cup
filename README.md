POBOT Junior Cup - Gestion de la compétition
============================================

Cette application aide à gérer le déroulement et l'animation de la compétition en fournissant
deux types de fonctionnalités :

* gestion des scores et du classement
* diffusion d'information au public

L'ensemble de ces fonctions est proposés via interface Web sur navigateur, y compris la diffusion
d'information au public.

Pour plus d'information sur la POBOT Junior Cup, faites un tour sur notre
[site Web](http://www.pobot.org/-POBOT-Junior-Cup-.html).

Gestion de la compétition
-------------------------

* saisie du décompte des points marqués par les équipes aux différentes épreuves de robotique
* saisie des évaluations faites par le jury aux dossiers de rechercher
* saisie des appréciations globales des équipes par le jury
* calcul automatique en temps réel des scores combinés
* calcul automatique en temps réel du classement final
* définition du planing de la compétition

En plus de la gestion des scores, l'application fournit un statut temps réel de l'avancement du déroulement
de la compétition par rapport au planning, en mettant en évidences l'approche des échéances et les éventuels
retards de passage.

Diffusion d'information au public
---------------------------------

Elle est assuré par des pages spécifiquement formattées, appelées par les machines reliées aux écrans de diffusion.
Les pages disponibles sont :
* score
* classement
* avancement

Une page de diffusion de message est également gérée automatiquement.

La configuration de l'enchaînement des différents affichages, ainsi que du message à diffuser si nécessaire,
est proposé dans des pages spécifiques de l'application.

Installation
------------

**Avertissement** Bien qu'écrite en Python, cette application est prévu pour être utilisée sous Linux. Il se peut
qu'elle fonctionne sous d'autres systèmes (comme Fenêtres par exemple :) mais je n'ai rien fait pour. Ceci étant le
code source peut toujours être exploité pour explorer l'utilisation de Tornado par exemple.

### Dépendances

* Python 2.7
* Serveur Python Tornado (3.2)

### Installation automatique (système)

L'application est disponible sous forme d'un paquet Debian, qui peut être généré au moyen du Makefile fourni
(`make dist`). L'installation du paquet configure également le script init et peut gérer
l'installation automatique des dépendances grâce aux variables d'environnements suivantes `INSTALL_DEPS` et
`START_SERVICE`.

La commande *full options* est donc :

    sudo INSTALL_DEPS=1 START_SERVICE=1 dpkg -i pjc-compmgr_<version>_all.deb

### Installation manuelle (utilisateur)

Décompresser le paquet Debian sans l'installer :

    dpkg -x pjc-compmgr_<version>_all.deb pjc-compmgr

L'arboresence système standard est alors créée dans la directory cible choisie (`pjc-compmgr` ici).

### Installation des dépendances

#### Python

S'installe par la commande habituelle :

    sudo apt-get install python

#### Tornado

**ATTENTION:** Ne pas l'installer depuis les dépôts officiels, car seule la version 2 y est pour le moment
disponible.

Il faut donc utiliser la commande `pip` pour cela :

    sudo pip install tornado

Si `pip` n'est pas déjà installé :

    sudo apt-get install pip

### Exécution

Si l'application a été installée au niveau système, elle peut être démarrée sous forme de service :

    sudo service pjc-compmgr start

Le répertoire utilisé pour les données (fichier `tournament.dat`) est dans ce cas `/var/db/pjc-compmgr`.

Si elle a été installée comme application utilisateur (cf paragraphe *Installation manuelle* ci-dessus) dans le
répertoire `<app-dir>` le lancement s'effectue par :

    cd <app-dir>/opt/pjc-compmgr
    PYTHONPATH=./lib python bin/webapp.py

Le répertoire de données est alors `$HOME/.pjc-compmgr/`.