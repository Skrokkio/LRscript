#!/bin/bash
# LRscript Installer Semplice
set -e

# Pulire lo schermo all'inizio
clear

# Funzione per log con timestamp
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1"
}

# Funzione per messaggi console
console_log() {
    local message="[LRscript Install] $1"
    log "$message"
    echo "$message"
}

# Funzione per chiedere conferma all'utente
ask_user_confirmation() {
    echo ""
    echo "========================================"
    echo "    LRscript Installer"
    echo "========================================"
    echo ""
    echo "Questa installazione sovrascriverà"
    echo "installazione precedente se presente"
    echo ""
    read -r -p "Premi Y per continuare o N per uscire dal programma: " user_choice
    user_choice=${user_choice:0:1}
    echo ""
    
    # Converti in maiuscolo e controlla la risposta
    user_choice=$(echo "$user_choice" | tr '[:lower:]' '[:upper:]')
    if [ "$user_choice" = "Y" ] || [ "$user_choice" = "YES" ]; then
        return 0  # Confermato
    else
        return 1  # Annullato
    fi
}

# Funzione per gestire errori
error_exit() {
    local error_msg="$1"
    log "Fatal Error: $error_msg"
    console_log "Installation error: $error_msg"
    exit 1
}

console_log "=== LRscript Retro Game Manager Installer ==="

# Chiedere conferma all'utente prima di procedere
if ! ask_user_confirmation; then
    console_log "Installation cancelled by user"
    echo "Installazione annullata dall'utente."
    exit 0
fi

console_log "User confirmed installation, proceeding..."

# Controlla se Python è installato
# if ! command -v python &> /dev/null; then
#     console_log "Errore: Python non trovato!"
#     error_exit "Python not found"
# fi

# Crea cartella in ports di Batocera
console_log "Creating installation directory..."
INSTALL_DIR="/userdata/roms/ports/LRscript"

# Rimuovi installazione precedente se presente
if [ -d "$INSTALL_DIR" ]; then
    console_log "Removing previous installation..."
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
if [ $? -ne 0 ]; then
    error_exit "Failed to create installation directory"
fi
cd "$INSTALL_DIR"

# Scarica repository
console_log "Downloading LRscript from GitHub..."
wget -O LRscript.zip https://github.com/Skrokkio/LRscript/archive/main.zip
if [ $? -ne 0 ]; then
    error_exit "Failed to download LRscript"
fi

console_log "Extracting LRscript..."
unzip LRscript.zip
if [ $? -ne 0 ]; then
    error_exit "Failed to extract LRscript"
fi

mv LRscript-main/* .
mv LRscript-main/.* . 2>/dev/null || true
rm -rf LRscript-main LRscript.zip 

# Dipendenze già presenti su Batocera
console_log "Dependencies already available on Batocera (pygame, requests)"

# Rendi eseguibile lo script principale
console_log "Making script executable..."
chmod +x LRscript.sh
if [ $? -ne 0 ]; then
    error_exit "Failed to make script executable"
fi

# Finalizzazione
console_log "✅ Installation completed!"
console_log "LRscript installed in: /userdata/roms/ports/LRscript"
console_log "To start: /userdata/roms/ports/LRscript/LRscript.sh"
console_log "Or from Batocera Ports menu"

echo ""
echo "========================================"
echo "    Installazione Completata!"
echo "========================================"
echo ""
echo "LRscript è stato installato con successo!"
echo "Percorso: /userdata/roms/ports/LRscript"
echo "Per avviare: /userdata/roms/ports/LRscript/LRscript.sh"
echo "Oppure dal menu Ports di Batocera"
echo ""
echo "Premi un tasto per uscire..."
read -n 1

exit 0