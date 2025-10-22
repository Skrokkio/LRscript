#!/bin/bash
# LRscript Installer Avanzato
set -e

echo "=== LRscript Retro Game Manager Installer ==="

# Controlla se Python è installato
# if ! command -v python &> /dev/null; then
#     echo "Errore: Python non trovato!"
#     exit 1
# fi

# Crea cartella in ports di Batocera
INSTALL_DIR="/userdata/roms/ports/LRscript"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Scarica repository
echo "Scaricamento LRscript..."
wget -O LRscript.zip https://github.com/Skrokkio/LRscript/archive/main.zip
unzip LRscript.zip
mv LRscript-main/* .
mv LRscript-main/.* . 2>/dev/null || true
rm -rf LRscript-main LRscript.zip 

# Dipendenze già presenti su Batocera
echo "Dipendenze già disponibili su Batocera (pygame, requests)"

# Rendi eseguibile lo script principale
chmod +x LRscript.sh

echo "✅ Installazione completata!"
echo "LRscript installato in: /userdata/roms/ports/LRscript"
echo "Per avviare: /userdata/roms/ports/LRscript/LRscript.sh"
echo "Oppure dal menu Ports di Batocera"