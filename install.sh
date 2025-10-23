#!/bin/sh
# LRscript Installer Semplice
set -e

# Pulire lo schermo all'inizio
clear

# Funzione per output formattato
print_message() {
    echo "[LRscript Install] $1"
}

# Funzione per gestire errori
error_exit() {
    echo "[LRscript Install] ERRORE: $1"
    exit 1
}

# Banner di intestazione
echo ""
echo "========================================"
echo "    LRscript Installer"
echo "========================================"
echo ""

print_message "Avvio installazione LRscript..."

# Funzione per chiedere conferma all'utente
ask_user_confirmation() {
    echo ""
    echo "Questa installazione sovrascriverà"
    echo "installazione precedente se presente"
    echo ""
    sleep 2 # Attesa di 2 secondi
    echo ""
    # Controlla se siamo in un terminale interattivo
    if [ -t 0 ]; then
        # Terminale interattivo - chiedi conferma
        echo "Premi Y per continuare o N per uscire dal programma: "
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

# Chiedere conferma all'utente prima di procedere
if ! ask_user_confirmation; then
    echo "Installazione annullata dall'utente."
    exit 0
fi

print_message "Confermato, avvio installazione..."
sleep 1 # Attesa di 1 secondo
echo ""

# Crea cartella in ports di Batocera
print_message "Creazione cartella di installazione..."
INSTALL_DIR="/userdata/roms/ports/LRscript"
sleep 1 # Attesa di 1 secondo
echo ""
# Rimuovi installazione precedente se presente
if [ -d "$INSTALL_DIR" ]; then
    print_message "Rimozione installazione precedente..."
    rm -rf "$INSTALL_DIR"
fi
sleep 1 # Attesa di 1 secondo
echo "" 
mkdir -p "$INSTALL_DIR"
if [ $? -ne 0 ]; then
    error_exit "Impossibile creare la directory di installazione"
fi
cd "$INSTALL_DIR"

# Scarica repository
sleep 1 # Attesa di 1 secondo
echo ""
print_message "Scaricamento LRscript da GitHub..."
wget -O LRscript.zip https://github.com/Skrokkio/LRscript/archive/main.zip
if [ $? -ne 0 ]; then
    error_exit "Impossibile scaricare LRscript"
fi

print_message "Estrazione LRscript..."
unzip LRscript.zip
if [ $? -ne 0 ]; then
    error_exit "Impossibile estrarre LRscript"
fi

mv LRscript-main/* .
mv LRscript-main/.* . 2>/dev/null || true
rm -rf LRscript-main LRscript.zip 

# Dipendenze già presenti su Batocera
print_message "Dipendenze già presenti su Batocera (pygame, requests)"
sleep 1 # Attesa di 1 secondo
echo ""
# Rendi eseguibile lo script principale
print_message "Rendi eseguibile lo script principale..."
chmod +x LRscript.sh
if [ $? -ne 0 ]; then
    error_exit "Impossibile rendere eseguibile lo script principale"
fi
sleep 1 # Attesa di 1 secondo
echo "" 
# Finalizzazione
print_message "✅ Installazione completata!"

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
echo "Premi INVIO per uscire..."
read dummy_var

exit 0