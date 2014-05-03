POBOT Junior Cup - Gestion de la compétition
============================================

Avertissement
-------------

Le projet n'a pas été publié sur ce repository pour être réutilisé tel quel, car il est spécifique à notre
compétition, et est de plus calé sur le règlement de l'édition 2014. L'adapter à d'autres règles de calcul est
cependant très simple, l'objectif étant justement qu'il soit facilement réutilisable pour les éditions à venir.

Il a été publié pour illustrer des exemples de solutions possibles utilisant Python et ses biliothèques pour traiter
ce type de problème. Il illustre aussi des aspects complémentaires, tels que la création d'un package Debian pour
en simplifier le déploiement.

Il s'agit donc plus d'une publication à des fins pédagogiques qu'à des fins utilitaires.

**Note:** les commentaires dans les sources sont en Anglais... par déformation professionnelle.


Description rapide
------------------

Cette application Python aide à gérer le déroulement et l'animation de la compétition en fournissant
deux types de fonctionnalités :

* gestion des scores et du classement
* diffusion d'information au public via écrans TV

L'ensemble de ces fonctions est proposé via une interface Web, y compris les affichages sur écran TV.

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

La configuration des "clients" (les Raspberry n'assurant que la fonction d'affichage sur TV), se reporter à la section
"Configuration des clients".

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
`NO_START`.

Comportement par défaut :

* les dépendances ne sont pas installées (pour éviter de le refaire à chaque mise à jour). Préfixer la commande `dpkg`
par `INSTALL_DEPS=1` pour les installer avant toute autre opération.
* le service est démarré automatiquement en fin d'installation, ce qui convient au cas d'usage
commun. Si on ne souhaite pas le démarrage automatique (par exemple, si on a oublié de demander l'installation
des dépendances ou qu'on préfère le faire manuellement), il suffit de préfixer la commande `dpkg` par `NO_START=1`

Quelques exemples d'utilisation :

    sudo INSTALL_DEPS=1 dpkg -i pjc-compmgr_<version>_all.deb
Installe l'application et ses dépendances, puis la démarre. A utiliser pour la toute première installation.

    sudo dpkg -i pjc-compmgr_<version>_all.deb
Installe l'application sans les dépendances, et la démarre ensuite. A n'utiliser que pour une mise à jour, sauf si
les dépendances sont déjà installées.

    sudo NO_START=1 dpkg -i pjc-compmgr_<version>_all.deb
La même chose sans démarrer l'application.


### Installation manuelle (utilisateur)

Décompresser le paquet Debian sans l'installer :

    dpkg -x pjc-compmgr_<version>_all.deb pjc-compmgr

L'arboresence système standard est alors créée dans la directory cible choisie (`pjc-compmgr` ici).

### Installation manuelle des dépendances

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

Configuration des clients pour affichage TV
-------------------------------------------

Les clients sont des Raspberry sans logiciel particulier, utilisant le navigateur Web en mode plein écran.

Afin d'en rendre le démarrage automatique, les étapes suivantes sont à exécuter :

* copier le fichier `<project-root>/client/start-tv-display-lxde` dans le home dir de l'utilisateur `pi` par exemple (en fait
l'emplacement de ce fichier importe peu, l'avantage du home dir est de ne pas nécessiter d'être sudo pour y écrire).

* remplacer le fichier `/etc/xdg/lxsession/LXED/autostart` par :

        @xset -dpms
        @xset s off

        @unclutter
        /home/pi/start-tv-display-lxde

Le script `start-tv-display-lxde` a pour fonction de s'assurer que la machine faisant office de serveur est en ligne
avant de lancer le navigateur, afin d'éviter que celui n'affiche un message d'erreur de type "page non trouvée", et
oblige à connecter un clavier à la Raspberry pour débloquer la situation. Ce script est basé sur le fait que
l'identification réseau du serveur est `pjc-display-1.local`. Modifiez-le pour l'adapter aux identificateurs des
machines de la configuration.

Si vous avez copié le script `start-tv-display-lxde` à un autre emplacement que celui suggéré, modifiez la dernière
commande du script en conséquence.

Les commandes `xset` servent à désactiver le DPMS et le screensaver pour éviter que l'écran ne s'éteigne au bout de
10 minutes. `xset` fait partie du package `x11-xserver-utils`. Vérifiez si elle est installée en l'appelant depuis la
ligne de commande.

`unclutter` permet de supprimer le pointeur de la souris lorsqu'elle reste à la même position. Il s'installe depuis
le repository standard via `sudo apt-get install unclutter`.

Pour plus de détails sur ces sujets : [http://www.pobot.org/Utiliser-la-Raspberry-en-mode.html](http://www.pobot.org/Utiliser-la-Raspberry-en-mode.html)
