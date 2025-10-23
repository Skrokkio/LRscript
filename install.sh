#!/bin/sh
# LRscript Installer Semplice
set -e

# Pulire lo schermo all'inizio
clear

# Funzione per log con timestamp
log() {
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1"
}

# Funzione per messaggi console
console_log() {
    message="[LRscript Install] $1"
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
    
    # Controlla se siamo in un terminale interattivo
    if [ -t 0 ]; then
        # Terminale interattivo - chiedi conferma
        echo -n "Premi Y per continuare o N per uscire dal programma: "
        read user_choice
        # Prendi solo il primo carattere
        user_choice=$(echo "$user_choice" | cut -c1)
        echo ""
        
        # Converti in maiuscolo e controlla la risposta
        user_choice=$(echo "$user_choice" | tr '[:lower:]' '[:upper:]')
        if [ "$user_choice" = "Y" ] || [ "$user_choice" = "YES" ]; then
            return 0  # Confermato
        else
            return 1  # Annullato
        fi
    else
        # Non in un terminale interattivo (curl | sh) - procedi automaticamente
        echo "Modalità non interattiva rilevata. Procedendo con l'installazione..."
        return 0
    fi
}

# Funzione per gestire errori
error_exit() {
    error_msg="$1"
    log "Fatal Error: $error_msg"
    console_log "Installation error: $error_msg"
    exit 1
}

console_log "=== LRscript Retro Game Manager Installer ==="

# Chiedere conferma all'utente prima di procedere
if ! ask_user_confirmation; then

    echo "Installazione annullata dall'utente."
    exit 0
fi

console_log "Confermato, avvio installazione..."

# Controlla se Python è installato
# if ! command -v python &> /dev/null; then
#     console_log "Errore: Python non trovato!"
#     error_exit "Python not found"
# fi

# Crea cartella in ports di Batocera
console_log "Creazione cartella di installazione..."
INSTALL_DIR="/userdata/roms/ports/LRscript"

# Rimuovi installazione precedente se presente
if [ -d "$INSTALL_DIR" ]; then
    console_log "Rimozione installazione precedente..."
    rm -rf "$INSTALL_DIR"
fi

mkdir -p "$INSTALL_DIR"
if [ $? -ne 0 ]; then
    error_exit "Failed to create installation directory"
fi
cd "$INSTALL_DIR"

# Scarica repository
console_log "Scaricamento LRscript da GitHub..."
wget -O LRscript.zip https://github.com/Skrokkio/LRscript/archive/main.zip
if [ $? -ne 0 ]; then
    error_exit "Failed to download LRscript"
fi

console_log "Estrazione LRscript..."
unzip LRscript.zip
if [ $? -ne 0 ]; then
    error_exit "Failed to extract LRscript"
fi

mv LRscript-main/* .
mv LRscript-main/.* . 2>/dev/null || true
rm -rf LRscript-main LRscript.zip 

# Dipendenze già presenti su Batocera
console_log "Dipendenze già presenti su Batocera (pygame, requests)"

# Rendi eseguibile lo script principale
console_log "Rendi eseguibile lo script principale..."
chmod +x LRscript.sh
if [ $? -ne 0 ]; then
    error_exit "Failed to make script executable"
fi

# Finalizzazione
console_log "✅ Installazione completata!"
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