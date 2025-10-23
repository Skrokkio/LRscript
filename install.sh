fix#!/bin/bash
# LRscript Installer Avanzato con Interfaccia Grafica
set -e

# Variabili per l'interfaccia grafica
XTERM="/usr/bin/xterm"
TEXT_SIZE="72"
TEXT_COLOR="green"
DISPLAY_LOG="/tmp/lrscript_install_display.log"

# Funzione per log con timestamp
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$DISPLAY_LOG" 2>&1
}

# Funzione per messaggi console e xterm
console_log() {
    local message="[LRscript Install] $1"
    log "$message"
    echo "$message"
    if [ -x "$XTERM" ]; then
        echo "$message" >> "$DISPLAY_LOG"
    fi
}

# Funzione per gestire errori
error_exit() {
    local error_msg="$1"
    log "Fatal Error: $error_msg"
    console_log "Installation error: $error_msg"
    console_log "Read $DISPLAY_LOG for details"
    if [ -x "$XTERM" ]; then
        LC_ALL=C $XTERM -fullscreen -fg red -bg black -fs $TEXT_SIZE -e "cat $DISPLAY_LOG; echo 'Press a key to exit...'; read -n 1; exit"
        rm -f "$DISPLAY_LOG"
    fi
    exit 1
}

# Configurare l'ambiente grafico per xterm
export DISPLAY=:0.0
export LC_ALL=C

# Inizializzare il log di display
echo "[LRscript Install] Starting LRscript Installation..." > "$DISPLAY_LOG"

# Avviare xterm in background per mostrare il progresso
if [ -x "$XTERM" ]; then
    LC_ALL=C $XTERM -fullscreen -fg $TEXT_COLOR -bg black -fs $TEXT_SIZE -e "tail -f $DISPLAY_LOG" &
    XTERM_PID=$!
    sleep 1
    console_log "Graphical interface started"
else
    console_log "xterm not available, using console mode only"
fi

console_log "=== LRscript Retro Game Manager Installer ==="

# Controlla se Python è installato
# if ! command -v python &> /dev/null; then
#     console_log "Errore: Python non trovato!"
#     error_exit "Python not found"
# fi

# Crea cartella in ports di Batocera
console_log "Checking installation directory..."
INSTALL_DIR="/userdata/roms/ports/LRscript"

# Controlla se la cartella esiste già
if [ -d "$INSTALL_DIR" ]; then
    console_log "Directory $INSTALL_DIR already exists!"
    echo ""
    echo "La cartella di destinazione esiste già: $INSTALL_DIR"
    echo "Vuoi sovrascriverla? (s/n): "
    read -r response
    
    if [[ "$response" =~ ^[Ss]$ ]]; then
        console_log "Rimuovendo cartella esistente..."
        rm -rf "$INSTALL_DIR"
        if [ $? -ne 0 ]; then
            error_exit "Failed to remove existing directory"
        fi
        console_log "Cartella rimossa con successo"
    else
        console_log "Installazione annullata dall'utente"
        error_exit "Installation cancelled by user"
    fi
fi

console_log "Creating installation directory..."
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

# Mostrare la finalizzazione in xterm
if [ -x "$XTERM" ]; then
    kill $XTERM_PID 2>/dev/null
    LC_ALL=C $XTERM -fullscreen -fg $TEXT_COLOR -bg black -fs $TEXT_SIZE -e "cat $DISPLAY_LOG; echo 'Installation completed. Press a key to exit...'; read -n 1; exit"
    rm -f "$DISPLAY_LOG"
fi

exit 0