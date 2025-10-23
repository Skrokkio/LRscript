#!/bin/bash
# Script pour telecharger et installer l'application RGSX depuis retrogamesets.fr
# et mettre a jour gamelist.xml pour ajouter l'entree RGSX
# Supprime rgsx-install.sh et RGSX.zip apres une installation reussie
# Affiche des messages informatifs sur la console (mode CONSOLE) ou via xterm (mode DISPLAY)

# Variables
URL="https://github.com/RetroGameSets/RGSX/releases/latest/download/RGSX_Full_latest.zip"
ZIP_FILE="/tmp/rgsx.zip"
DEST_DIR="/userdata/roms"
RGSX_DIR="${DEST_DIR}/ports/RGSX"
GAMELIST_FILE="${DEST_DIR}/ports/gamelist.xml"
UPDATE_GAMELIST_PY="${RGSX_DIR}/update_gamelist.py"
LOG_DIR="${DEST_DIR}/ports/RGSX_INSTALL_LOGS"
LOG_FILE="${LOG_DIR}/rgsx_install.log"
TEMP_LOG="/tmp/rgsx_install_temp.log"
SCRIPT_FILE="${DEST_DIR}/rgsx-install.sh"
XTERM="/usr/bin/xterm"
MODE="DISPLAY"  # Par defaut, mode graphique pour PORTS
TEXT_SIZE="72"  # Taille de police pour xterm
TEXT_COLOR="green"

# Chemins absolus pour les commandes
CURL="/usr/bin/curl"
WGET="/usr/bin/wget"
UNZIP="/usr/bin/unzip"
PING="/bin/ping"
RM="/bin/rm"
MKDIR="/bin/mkdir"
CHMOD="/bin/chmod"
FIND="/usr/bin/find"
PYTHON3="/usr/bin/python3"
SYNC="/bin/sync"
SLEEP="/bin/sleep"
LS="/bin/ls"
CAT="/bin/cat"
WHOAMI="/usr/bin/whoami"
ENV="/usr/bin/env"
TOUCH="/bin/touch"
DF="/bin/df"
MOUNT="/bin/mount"
NSLOOKUP="/usr/bin/nslookup"

# Verifier le mode (DISPLAY ou CONSOLE)
if [ "$1" = "CONSOLE" ] || [ "$1" = "console" ]; then
    MODE="CONSOLE"
fi

# Fonction pour journaliser avec horodatage dans les fichiers de log
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    if [ -d "$LOG_DIR" ] && [ -w "$LOG_DIR" ]; then
        echo "[$timestamp] $1" >> "$LOG_FILE" 2>&1
    else
        echo "[$timestamp] $1" >> "$TEMP_LOG" 2>&1
    fi
}

# Fonction pour afficher des messages informatifs (console ou xterm)
console_log() {
    local message="[RGSX Install] $1"
    log "$message"
    echo "$message"  # Toujours afficher dans le terminal
    if [ "$MODE" = "DISPLAY" ] && [ -x "$XTERM" ]; then
        echo "$message" >> /tmp/rgsx_install_display.log
    fi
}

# Fonction pour executer une commande et journaliser son execution
run_command() {
    local cmd_name="$2"
    log "Execution de la commande : $1"
    output=$(eval "$1" 2>&1)
    local exit_code=$?
    log "Sortie de '$cmd_name' :"
    log "$output"
    log "Code de retour : $exit_code"
    return $exit_code
}

# Fonction pour gerer les erreurs avec journalisation et message console/xterm
error_exit() {
    local error_msg="$1"
    log "Fatal Error : $error_msg"
    console_log "Installation error : $error_msg"
    console_log "Read $LOG_FILE for details"
    log "Clean temp file : $ZIP_FILE"
    if [ -f "$ZIP_FILE" ]; then
        run_command "$RM -f $ZIP_FILE" "rm_zip"
    fi
    log "Script aborted with error code 1"
    if [ "$MODE" = "DISPLAY" ] && [ -x "$XTERM" ]; then
        LC_ALL=C $XTERM -fullscreen -fg $TEXT_COLOR -bg black -fs $TEXT_SIZE -e "cat /tmp/rgsx_install_display.log; echo 'Press a key to exit...'; read -n 1; exit"
        rm -f /tmp/rgsx_install_display.log
    fi
    exit 1
}

# Configurer l'environnement graphique pour xterm
if [ "$MODE" = "DISPLAY" ]; then
    export DISPLAY=:0.0
    export LC_ALL=C  # Definir la locale pour eviter l'avertissement Xlib
    if [ -x "$XTERM" ]; then
        cp $XTERM /tmp/rgsx-install-xterm && chmod 777 /tmp/rgsx-install-xterm
        echo "[RGSX Install] Starting RGSX Installation..." > /tmp/rgsx_install_display.log
        # Lancer xterm en arriere-plan pour afficher la progression
        LC_ALL=C /tmp/rgsx-install-xterm -fullscreen -fg $TEXT_COLOR -bg black -fs $TEXT_SIZE -e "tail -f /tmp/rgsx_install_display.log" &
        XTERM_PID=$!
        sleep 1  # Attendre que xterm demarre
    else
        log "xterm non disponible, passage en mode journalisation uniquement."
        MODE="CONSOLE"
    fi
else
    console_log "[RGSX Install] Starting RGSX Installation..."
fi

# Verifier l'accessibilite de /tmp pour le journal temporaire
log "Verification de l'accessibilite de /tmp pour le journal temporaire"
run_command "$TOUCH $TEMP_LOG && $RM $TEMP_LOG" "test_tmp_access" || error_exit "Le repertoire /tmp n'est pas accessible en ecriture."

# Nettoyer les dossiers mal crees
log "Verification des dossiers mal crees sous /userdata"
if [ -d "/userdata/\"/userdata/roms/ports\"" ]; then
    log "Suppression du dossier incorrect /userdata/\"/userdata/roms/ports\""
    run_command "$RM -rf /userdata/\\\"/userdata/roms/ports\\\"" "rm_incorrect_dir"
fi

# Journaliser l'etat du systeme de fichiers
log "etat du systeme de fichiers :"
run_command "$DF -h" "df_filesystem"
log "Points de montage :"
run_command "$MOUNT" "mount_points"

# Verifier et creer le repertoire /userdata/roms/ports
console_log "Verify destination directory $DEST_DIR..."
log "Verification et creation du repertoire $DEST_DIR"
run_command "$MKDIR -p $DEST_DIR" "mkdir_dest_dir" || error_exit "Impossible de creer $DEST_DIR."
log "Verification de l'existence de $DEST_DIR"
if [ ! -d "$DEST_DIR" ]; then
    error_exit "$DEST_DIR n'a pas ete cree."
fi
log "Permissions de $DEST_DIR apres creation"
run_command "$LS -ld $DEST_DIR" "ls_dest_dir"
if [ ! -w "$DEST_DIR" ]; then
    log "Tentative de correction des permissions de $DEST_DIR"
    run_command "$CHMOD u+w $DEST_DIR" "chmod_dest_dir" || error_exit "Impossible de rendre $DEST_DIR accessible en ecriture."
fi

# Creer le repertoire des logs
log "Creation du repertoire des logs : $LOG_DIR"
run_command "$MKDIR -p $LOG_DIR" "mkdir_log_dir" || error_exit "Impossible de creer $LOG_DIR."

# Copier le journal temporaire dans LOG_FILE
if [ -f "$TEMP_LOG" ] && [ -d "$LOG_DIR" ]; then
    log "Copie du journal temporaire $TEMP_LOG vers $LOG_FILE"
    run_command "$CAT $TEMP_LOG >> $LOG_FILE" "copy_temp_log"
    run_command "$RM -f $TEMP_LOG" "rm_temp_log"
fi

# Journaliser l'environnement d'execution
log "Utilisateur actuel :"
run_command "$WHOAMI" "whoami"
log "Variables d'environnement :"
run_command "$ENV" "env"
log "Chemin PATH : $PATH"

# Verifier les dependances
log "Verification des commandes necessaires"
for cmd in "$CURL" "$UNZIP" "$PING" "$RM" "$MKDIR" "$CHMOD" "$FIND" "$PYTHON3" "$SYNC" "$SLEEP" "$LS" "$CAT" "$TOUCH" "$DF" "$MOUNT"; do
    if [ ! -x "$cmd" ]; then
        error_exit "Commande $cmd non trouvee ou non executable."
    fi
    log "Commande $cmd : OK"
done
if [ -x "$WGET" ]; then
    log "Commande $WGET : OK"
else
    log "Commande $WGET : Non disponible, utilisation de curl uniquement."
fi
if [ -x "$NSLOOKUP" ]; then
    log "Commande $NSLOOKUP : OK"
else
    log "Commande $NSLOOKUP : Non disponible."
fi

# Verifier la connexion Internet
log "Test de connexion Internet..."
run_command "$PING 8.8.8.8 -c 1" "ping_google" || error_exit "Pas de connexion Internet."

# Tester la resolution DNS
log "Test de resolution DNS pour retrogamesets.fr"
if [ -x "$NSLOOKUP" ]; then
    run_command "$NSLOOKUP retrogamesets.fr" "nslookup_retrogamesets"
fi
run_command "$PING -c 1 retrogamesets.fr" "ping_retrogamesets"

# Telecharger le ZIP avec curl
console_log "Downloading RGSX..."
log "Tentative de telechargement avec curl : $URL vers $ZIP_FILE..."
run_command "$CURL -L --insecure -v -o $ZIP_FILE $URL" "curl_download"
if [ $? -ne 0 ]; then
    log "echec du telechargement avec curl, tentative avec wget si disponible..."
    if [ -x "$WGET" ]; then
        run_command "$WGET --no-check-certificate -O $ZIP_FILE $URL" "wget_download" || error_exit "echec du telechargement avec wget."
    else
        error_exit "echec du telechargement avec curl et wget non disponible."
    fi
fi
log "Details du fichier telecharge :"
run_command "$LS -l $ZIP_FILE" "ls_zip_file"

# Verifier si le fichier ZIP existe
log "Verification de l'existence de $ZIP_FILE"
if [ ! -f "$ZIP_FILE" ]; then
    error_exit "Le fichier ZIP $ZIP_FILE n'a pas ete telecharge."
fi
log "Fichier $ZIP_FILE trouve."

# Verifier si le fichier ZIP est valide
log "Verification de l'integrite du fichier ZIP : $ZIP_FILE"
run_command "$UNZIP -t $ZIP_FILE" "unzip_test" || error_exit "Le fichier ZIP est corrompu ou invalide."
log "Contenu du ZIP :"
run_command "$UNZIP -l $ZIP_FILE" "unzip_list"

# Supprimer l'ancien dossier RGSX s'il existe
if [ -d "$RGSX_DIR" ]; then
    log "Suppression de l'ancien dossier $RGSX_DIR..."
    run_command "$RM -rf $RGSX_DIR" "rm_rgsx_dir" || error_exit "Impossible de supprimer $RGSX_DIR."
    run_command "$SYNC" "sync_after_rm"
    log "Attente de 2 secondes apres suppression..."
    run_command "$SLEEP 2" "sleep_after_rm"
    if [ -d "$RGSX_DIR" ]; then
        error_exit "Le dossier $RGSX_DIR existe toujours apres tentative de suppression."
    fi
    log "Ancien dossier $RGSX_DIR supprime avec succes."
else
    log "Aucun dossier $RGSX_DIR existant trouve."
fi

# Extraire le ZIP
console_log "Extracting files..."
log "Extraction de $ZIP_FILE vers $DEST_DIR..."
run_command "$UNZIP -q -o $ZIP_FILE -d $DEST_DIR" "unzip_extract" || error_exit "echec de l'extraction de $ZIP_FILE."
log "Contenu de $DEST_DIR apres extraction :"
run_command "$LS -la $DEST_DIR" "ls_dest_dir_after_extract"

# Verifier si le dossier RGSX a ete extrait
log "Verification de l'existence de $RGSX_DIR"
if [ ! -d "$RGSX_DIR" ]; then
    error_exit "Le dossier RGSX n'a pas ete trouve dans $DEST_DIR apres extraction."
fi
log "Dossier $RGSX_DIR trouve."

# Rendre les fichiers .sh executables
log "Rendre les fichiers .sh executables dans $RGSX_DIR..."
run_command "$FIND $RGSX_DIR -type f -name \"*.sh\" -exec $CHMOD +x {} \;" "chmod_sh_files" || log "Avertissement : Impossible de rendre certains fichiers .sh executables."
log "Fichiers .sh dans $RGSX_DIR :"
run_command "$FIND $RGSX_DIR -type f -name \"*.sh\" -ls" "find_sh_files"

# Rendre update_gamelist.py executable
log "Rendre $UPDATE_GAMELIST_PY executable..."
if [ -f "$UPDATE_GAMELIST_PY" ]; then
    run_command "$CHMOD +x $UPDATE_GAMELIST_PY" "chmod_update_gamelist" || log "Avertissement : Impossible de rendre $UPDATE_GAMELIST_PY executable."
else
    error_exit "Le script Python $UPDATE_GAMELIST_PY n'existe pas."
fi

# Definir les permissions du dossier RGSX
log "Definition des permissions de $RGSX_DIR..."
run_command "$CHMOD -R u+rwX $RGSX_DIR" "chmod_rgsx_dir" || log "Avertissement : Impossible de definir les permissions de $RGSX_DIR."

# Verifier les permissions d'ecriture
log "Verification des permissions d'ecriture sur $DEST_DIR"
if [ ! -w "$DEST_DIR" ]; then
    error_exit "Le repertoire $DEST_DIR n'est pas accessible en ecriture."
fi
log "Permissions d'ecriture sur $DEST_DIR : OK"

# Mettre a jour gamelist.xml avec Python
console_log "Updating gamelist.xml..."
log "Mise a jour de $GAMELIST_FILE avec Python..."
run_command "$PYTHON3 $UPDATE_GAMELIST_PY" "python_update_gamelist" || error_exit "echec de la mise a jour de $GAMELIST_FILE avec Python."
log "Contenu de $GAMELIST_FILE apres mise a jour :"
run_command "$CAT $GAMELIST_FILE" "cat_gamelist"

# Verifier les permissions du fichier gamelist.xml
log "Definition des permissions de $GAMELIST_FILE..."
run_command "$CHMOD 644 $GAMELIST_FILE" "chmod_gamelist" || log "Avertissement : Impossible de definir les permissions de $GAMELIST_FILE."

# Nettoyer le fichier ZIP temporaire
console_log "Cleanup temp files.."
log "Nettoyage du fichier ZIP temporaire : $ZIP_FILE"
if [ -f "$ZIP_FILE" ]; then
    run_command "$RM -f $ZIP_FILE" "rm_zip" || log "Avertissement : Impossible de supprimer $ZIP_FILE."
fi

# Nettoyer le fichier ZIP dans /userdata/roms/ports
log "Nettoyage du fichier ZIP dans $DEST_DIR : $DEST_DIR/RGSX.zip"
if [ -f "$DEST_DIR/RGSX.zip" ]; then
    run_command "$RM -f $DEST_DIR/RGSX.zip" "rm_dest_zip" || log "Avertissement : Impossible de supprimer $DEST_DIR/RGSX.zip."
fi

# Nettoyer le launcher retrobat
log "Nettoyage du launcher windows inutile ici"
if [ -f "$DEST_DIR/windows/RGSX Retrobat.bat" ]; then
    run_command "$RM -f $DEST_DIR/windows/RGSX Retrobat.bat" "rm_retrobat_launcher" || log "Avertissement : Impossible de supprimer $DEST_DIR/windows/RGSX Retrobat.bat"
fi

# Finalisation
console_log "Install successful in ports system!" 
console_log "Press enter to quit or wait 5 seconds more. Please update gamelist in Menu>Games>Update Games List"
log "Installation reussie dans le système PORTS! Appuyez sur entrée pour quitter. Actualisez la liste des jeux si RGSX n'apparait pas."
log "L'entree RGSX a ete ajoutee a $GAMELIST_FILE."
log "Fin du script avec code de retour 0"
run_command "$PING -q www.google.fr -c 5" "ping_google"
curl -s http://127.0.0.1:1234/reloadgames

# Afficher la finalisation dans xterm et attendre une entree utilisateur
if [ "$MODE" = "DISPLAY" ] && [ -x "$XTERM" ]; then
    kill $XTERM_PID 2>/dev/null
    LC_ALL=C $XTERM -fullscreen -fg $TEXT_COLOR -bg black -fs $TEXT_SIZE -e "cat /tmp/rgsx_install_display.log; echo 'Installation terminee. Appuyez sur une touche pour quitter...'; read -n 1; exit"
    rm -f /tmp/rgsx_install_display.log
    rm -f /tmp/rgsx-install-xterm
fi

# Supprimer le script d'installation
log "Suppression du script d'installation : $SCRIPT_FILE"
if [ -f "$SCRIPT_FILE" ]; then
    run_command "$RM -f $SCRIPT_FILE" "rm_script" || log "Avertissement : Impossible de supprimer $SCRIPT_FILE."
fi

exit 0