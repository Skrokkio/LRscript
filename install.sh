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

# Installa dipendenze
echo "Installazione dipendenze..."
pip install pygame requests

# Crea script di avvio
cat > start_lrscript.sh << 'EOF'
#!/bin/bash
cd /userdata/roms/ports/LRscript
python __main__.py
EOF

chmod +x start_lrscript.sh

# Crea link simbolico per accesso rapido
ln -sf /userdata/roms/ports/LRscript/LRscript.sh /userdata/roms/ports/LRscript.sh

echo "✅ Installazione completata!"
echo "LRscript installato in: /userdata/roms/ports/LRscript"
echo "Per avviare: /userdata/roms/ports/LRscript/LRscript.sh"
echo "Oppure dal menu Ports di Batocera"