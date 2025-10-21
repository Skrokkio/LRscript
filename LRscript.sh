#!/bin/bash

# Script di avvio per LRscript
# Attiva l'ambiente virtuale e avvia l'applicazione

echo "🎮 Avvio LRscript..."
echo "===================="

# Vai nella directory del progetto
cd "$(dirname "$0")"

# Attiva l'ambiente virtuale
source pygame_env/bin/activate

# Avvia l'applicazione
python __main__.py

echo "👋 LRscript chiuso"
