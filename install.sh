#!/bin/bash
# LRscript Installer Avanzato
set -e

echo "=== LRscript Retro Game Manager Installer ==="

# Controlla se Python è installato
if ! command -v python3 &> /dev/null; then
    echo "Errore: Python3 non trovato!"
    exit 1
fi

# Crea cartella in ports di Batocera
INSTALL_DIR="/userdata/roms/ports/LRscript"
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
cd /userdata/roms/ports/LRscript
python3 __main__.py
EOF

chmod +x start_lrscript.sh

# Crea link simbolico per accesso rapido
ln -sf /userdata/roms/ports/LRscript/LRscript.sh /userdata/roms/ports/LRscript.sh

echo "✅ Installazione completata!"
echo "LRscript installato in: /userdata/roms/ports/LRscript"
echo "Per avviare: /userdata/roms/ports/LRscript/LRscript.sh"
echo "Oppure dal menu Ports di Batocera"