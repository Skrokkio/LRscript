#!/bin/bash
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

# Funzione per chiedere conferma all'utente
ask_user_confirmation() {
    local response
    if [ -x "$XTERM" ]; then
        # Usa xterm per chiedere conferma
        response=$(LC_ALL=C $XTERM -fullscreen -fg yellow -bg black -fs $TEXT_SIZE -e "
            echo '========================================'
            echo '    LRscript Installer'
            echo '========================================'
            echo ''
            echo 'Questa installazione sovrascriverà'
            echo 'installazione precedente se presente'
            echo ''
            echo 'Premi Y per continuare o N per uscire'
            echo 'dal programma'
            echo ''
            echo '========================================'
            echo -n 'La tua scelta (Y/N): '
            read -n 1 response
            echo
            echo \"Hai scelto: \$response\"
            echo \"\$response\"
        " 2>/dev/null)
    else
        # Fallback per console normale
        echo "========================================"
        echo "    LRscript Installer"
        echo "========================================"
        echo ""
        echo "Questa installazione sovrascriverà"
        echo "installazione precedente se presente"
        echo ""
        echo -n "Premi Y per continuare o N per uscire dal programma: "
        read -n 1 response
        echo
    fi
    
    # Converti in maiuscolo e controlla la risposta
    response=$(echo "$response" | tr '[:lower:]' '[:upper:]')
    if [ "$response" = "Y" ] || [ "$response" = "YES" ]; then
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

# Chiedere conferma all'utente prima di procedere
console_log "Asking user confirmation..."
if ! ask_user_confirmation; then
    console_log "Installation cancelled by user"
    if [ -x "$XTERM" ]; then
        LC_ALL=C $XTERM -fullscreen -fg red -bg black -fs $TEXT_SIZE -e "
            echo '========================================'
            echo '    Installazione Annullata'
            echo '========================================'
            echo ''
            echo 'L''installazione è stata annullata'
            echo 'dall''utente.'
            echo ''
            echo 'Premi un tasto per uscire...'
            read -n 1
        "
    fi
    exit 0
fi

console_log "User confirmed installation, proceeding..."

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

# Mostrare la finalizzazione in xterm
if [ -x "$XTERM" ]; then
    kill $XTERM_PID 2>/dev/null
    LC_ALL=C $XTERM -fullscreen -fg $TEXT_COLOR -bg black -fs $TEXT_SIZE -e "cat $DISPLAY_LOG; echo 'Installation completed. Press a key to exit...'; read -n 1; exit"
    rm -f "$DISPLAY_LOG"
fi

exit 0