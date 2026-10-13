# Telegram Media Leecher

**Téléchargeur automatisé de médias depuis des canaux & discussions Telegram directement vers votre médiathèque Jellyfin, Plex ou Emby.**

[Read in English](README.md) · [Exemple de configuration](.env.example) · [Contribuer](CONTRIBUTING.md) · [Licence](LICENSE)

## Fonctionnalités

Telegram Media Leecher surveille un groupe ou un canal Telegram dédié, détecte les fichiers vidéos transférés ou envoyés et les télécharge automatiquement sur votre serveur de stockage :

- **Téléchargement direct Telegram** : Récupère les médias directement depuis les serveurs de contenu Telegram avec accélération matérielle AES (`cryptg`). Sans BitTorrent, sans partage P2P, sans contrainte de ratio et sans risque de surveillance FAI / Arcom.
- **Classification intelligente** : Utilise [GuessIt](https://guessit-io.github.io/guessit/) et des règles de mots-clés pour analyser les titres et ranger automatiquement les fichiers dans les dossiers films, séries, animes ou contenus adultes.
- **Organisation propre pour médiathèques** : Structure les séries et animes en dossiers `Titre/Season XX/` et préserve les extensions d'origine (même pour les œuvres contenant des points dans leur titre).
- **Permissions de fichiers sécurisées** : Applique un `chmod 0666` dès la fin du téléchargement afin que Jellyfin ou Plex (exécutés sous un autre utilisateur système) puissent lire et diffuser les médias immédiatement.
- **Barre de progression anti-flood** : Affiche une jauge visuelle dynamique avec le volume téléchargé en Mo/Go, régulée pour éviter les blocages `FloodWait` de Telegram.
- **Actualisation automatique du serveur média** : Envoie un signal d'actualisation de bibliothèque à l'API de Jellyfin, Emby ou Plex dès qu'un fichier est prêt.

## Architecture

~~~text
Canaux / Groupes Telegram (Toute source publique ou privée)
                     │
                     │ (Transfert / Envoi de vidéo)
                     ▼
         Groupe Telegram Dédié (ex: Jellyfin)
                     │
                     ▼
   Telegram Media Leecher (Telethon + GuessIt)
                     │
                     ├── Analyse du nom & métadonnées
                     │   ├── Films       ──> /media/films/Titre (Année)/
                     │   ├── Séries TV   ──> /media/series/Titre/Season XX/
                     │   ├── Animes      ──> /media/animes/Titre/Season XX/
                     │   └── Contenus adultes ──> /media/adulte/
                     │
                     └── Actualisation API ──> Jellyfin / Emby (HTTP)
~~~

## Prérequis

| Composant | Prérequis |
| --- | --- |
| API Telegram | `TG_API_ID` et `TG_API_HASH` obtenus gratuitement sur [my.telegram.org](https://my.telegram.org) |
| Hôte applicatif | Linux, Python 3.10 ou supérieur (ou Docker / Docker Compose) |
| Stockage | Dossiers locaux ou partages NFS/SMB pour vos bibliothèques |
| Serveur média (optionnel) | Jellyfin, Plex ou Emby avec une clé d'API pour le scan automatique |

## Démarrage rapide avec Docker Compose

### Option A : Installation guidée en une commande (Recommandé)

Depuis la racine du projet, lancez :

~~~bash
./install.sh
~~~

Le script valide la présence de Docker et Compose v2, demande vos identifiants d'API Telegram et vos chemins de stockage, sécurise le fichier `.env` (`umask 077`), guide la première authentification Telegram et démarre le service.

### Option B : Configuration manuelle

1. Copier le fichier d'exemple :
   ~~~bash
   cp .env.example .env
   nano .env
   ~~~
2. Effectuer la première authentification Telegram :
   ~~~bash
   docker compose run --rm telegram-leecher python main.py
   ~~~
3. Démarrer le conteneur en arrière-plan :
   ~~~bash
   docker compose up -d
   docker compose logs -f
   ~~~

## Installation bare-metal ou conteneur LXC (systemd)

Pour Debian, Ubuntu ou conteneur Proxmox LXC :

### 1. Installer les paquets requis

~~~bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git gcc libffi-dev build-essential
~~~

### 2. Cloner le projet dans `/opt`

~~~bash
sudo git clone https://github.com/HarpToubdra/telegram-media-leecher.git /opt/telegram-media-leecher
cd /opt/telegram-media-leecher
~~~

### 3. Créer l'environnement virtuel et installer les dépendances

~~~bash
python3 -m venv .venv
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -r requirements.txt
~~~

### 4. Configurer et effectuer le premier login

~~~bash
cp .env.example .env
nano .env
.venv/bin/python main.py
~~~

Entrez votre numéro et le code SMS reçu, puis quittez avec `Ctrl+C`.

### 5. Activer le service systemd

~~~bash
sudo cp systemd/telegram-leecher.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-leecher
sudo journalctl -u telegram-leecher -f
~~~

## Variables de configuration

| Paramètre | Défaut | Description |
| --- | --- | --- |
| `TG_API_ID` | vide | ID numérique de l'API Telegram depuis my.telegram.org |
| `TG_API_HASH` | vide | Chaîne de hachage de l'API Telegram depuis my.telegram.org |
| `TG_SESSION_PATH` | `./data/telegram_session` | Emplacement du fichier de session Telethon |
| `TARGET_CHAT` | `Jellyfin` | Titre exact ou identifiant du groupe Telegram surveillé |
| `DOWNLOAD_DIR_FILMS` | `/media/films` | Répertoire cible pour les films |
| `DOWNLOAD_DIR_SERIES` | `/media/series` | Répertoire cible pour les séries TV |
| `DOWNLOAD_DIR_ANIMES` | `/media/animes` | Répertoire cible pour les animes |
| `DOWNLOAD_DIR_ADULTE` | `/media/adulte` | Répertoire cible pour les contenus adultes |
| `JELLYFIN_ENABLED` | `false` | Active le rafraîchissement automatique de la médiathèque |
| `JELLYFIN_URL` | `http://localhost:8096` | URL de base du serveur Jellyfin |
| `JELLYFIN_API_KEY` | vide | Clé d'API créée dans Jellyfin (Tableau de bord > Clés API) |

Les variables d'environnement du système prévalent sur les valeurs de `.env`.

## Règles de tri et de routage

| Catégorie | Modèle de destination | Condition de routage |
| --- | --- | --- |
| **Films** | `/media/films/<Titre> (<Année>)/` | Catégorie par défaut sans numérotation d'épisode ni mot-clé particulier |
| **Séries TV** | `/media/series/<Titre>/Season <XX>/` | Présence d'une numérotation de saison/épisode (ex: `S01E04`, `1x04`) |
| **Animes** | `/media/animes/<Titre>/Season <XX>/` | Légende ou nom de fichier contenant les termes `anime`, `manga` ou `vostfr` |
| **Contenus adultes** | `/media/adulte/` | Légende ou nom de fichier contenant des mots-clés (`adulte`, `xxx`, `porn`, `hentai`, `nsfw`) |

## Dépannage

| Symptôme | Vérification |
| --- | --- |
| « Missing TG_API_ID or TG_API_HASH » | Vérifiez que les deux variables sont définies dans le fichier `.env` ou l'environnement systemd. |
| Demande du numéro de téléphone au démarrage | Comportement normal lors du premier lancement. Lancez le script en mode interactif pour créer le fichier `.session`. |
| `FloodWaitError` lors de l'édition du message | Telegram limite la cadence de modification des messages. L'intervalle de rafraîchissement est bridé à 3,5 secondes. |
| Jellyfin renvoie HTTP 401 Unauthorized | Vérifiez la valeur de `JELLYFIN_API_KEY`. Le bot transmet automatiquement les en-têtes `Authorization: MediaBrowser Token="..."` et `X-Emby-Token`. |
| Droits d'accès insuffisants dans Jellyfin | Le bot applique `chmod 0666` aux fichiers téléchargés. Vérifiez que l'utilisateur de Jellyfin possède le droit d'exécution (`+x`) sur les dossiers parents. |
| Fichier classé en Film au lieu d'Anime | Ajoutez le terme `anime` ou `vostfr` dans la légende lors du transfert du fichier. |

## Sécurité et limites

- **Protection de la session** : Le fichier `.session` confère l'accès complet à votre compte Telegram. Ne le publiez jamais dans un dépôt git public, tout comme votre fichier `.env`. Conservez le dossier `./data` hors de Git.
- **Limites Telegram** : La bande passante et la taille maximale par fichier dépendent de votre type de compte (jusqu'à 2 Go pour un compte gratuit, jusqu'à 4 Go pour un abonnement Telegram Premium).
- **Téléchargements séquentiels** : Les fichiers sont traités un par un par instance afin d'éviter la saturation réseau et les sanctions Telegram pour requêtes excessives.
- **Permissions de fichiers** : Les fichiers téléchargés reçoivent les droits `0666` (`rw-rw-rw-`) pour garantir leur lecture immédiate par les services médias conteneurisés ou partagés en réseau.

## Développement et tests

~~~bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
pytest -v
~~~

## Licence

MIT. Voir [LICENSE](LICENSE).
