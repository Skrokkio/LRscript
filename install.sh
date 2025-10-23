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

# Funzione per gestire cartella esistente
handle_existing_directory() {
    local install_dir="$1"
    
    if [ -d "$install_dir" ]; then
        console_log "⚠️  Directory already exists: $install_dir"
        console_log "Waiting for user response..."
        
        # Pausa per dare tempo all'utente di leggere
        sleep 2
        
        # In modalità grafica, usa zenity se disponibile
        if [ -x "$XTERM" ] && command -v zenity &> /dev/null; then
            console_log "Showing graphical dialog..."
            if zenity --question --title="LRscript Installer" --text="Directory $install_dir already exists.\nDo you want to overwrite it?" --width=400 --timeout=30; then
                console_log "User confirmed: overwriting existing directory"
                rm -rf "$install_dir"
                if [ $? -ne 0 ]; then
                    error_exit "Failed to remove existing directory"
                fi
                console_log "Existing directory removed successfully"
            else
                console_log "Installation cancelled by user"
                exit 0
            fi
        else
            # Modalità console con timeout
            console_log "Do you want to overwrite it? (y/N) - waiting 30 seconds..."
            read -t 30 -p "Overwrite existing directory? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                console_log "User confirmed: overwriting existing directory"
                rm -rf "$install_dir"
                if [ $? -ne 0 ]; then
                    error_exit "Failed to remove existing directory"
                fi
                console_log "Existing directory removed successfully"
            else
                console_log "Installation cancelled by user (timeout or no response)"
                exit 0
            fi
        fi
    fi
}

# Crea cartella in ports di Batocera
console_log "Checking installation directory..."
INSTALL_DIR="/userdata/roms/ports/LRscript"

# Gestisci cartella esistente
handle_existing_directory "$INSTALL_DIR"

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