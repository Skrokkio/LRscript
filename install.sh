#!/bin/bash
# LRscript Installer Avanzato
set -e

echo "=== LRscript Retro Game Manager Installer ==="

# Controlla se Python è installato
if ! command -v python3 &> /dev/null; then
    echo "Errore: Python3 non trovato!"
    exit 1
fi

# Crea cartella
INSTALL_DIR="$HOME/LRscript"
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Scarica repository
echo "Scaricamento LRscript..."
git clone https://github.com/Skrokkio/LRscript.git .

# Installa dipendenze
echo "Installazione dipendenze..."
pip3 install pygame requests

# Crea script di avvio
cat > start_lrscript.sh << 'EOF'
#!/bin/bash
cd ~/LRscript
python3 __main__.py
EOF

chmod +x start_lrscript.sh

echo "✅ Installazione completata!"
echo "Per avviare: ~/LRscript/start_lrscript.sh"