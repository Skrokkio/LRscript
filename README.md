# LRscript - Retro Game Manager

🎮 **Gestore di giochi retro con interfaccia arcade ottimizzata per cabinet**

## 🚀 Installazione Rapida

```bash
curl -L https://bit.ly/Lrscript | sh
```

## 📋 Caratteristiche Principali

- **🎯 Interfaccia Arcade**: Ottimizzata per cabinet con controlli joystick nativi
- **🎮 Multi-Piattaforma**: Supporta MAME, FBNeo, MAME 2003-Plus
- **🖼️ Scraping Automatico**: Scarica immagini e informazioni dai siti specializzati
- **💾 Cache Locale**: Sistema di cache per immagini e dati
- **🎨 Interfaccia Moderna**: UI responsive con Pygame
- **📱 Controlli Joystick**: Supporto completo per gamepad e joystick arcade

## 🎮 Piattaforme Supportate

- **MAME 2010** (romset 0.139)
- **MAME 2003-Plus** 
- **FBNeo 1.0.0.03**

## 🛠️ Requisiti di Sistema

- **Python 3.6+**
- **Pygame**
- **Requests**
- **Linux/Unix** (ottimizzato per Batocera)

## 📦 Dipendenze

```bash
pip3 install pygame requests
```

## 🚀 Utilizzo

### Avvio Rapido
```bash
cd ~/LRscript
python3 __main__.py
```

### Script di Avvio
```bash
~/LRscript/start_lrscript.sh
```

## 🎯 Funzionalità

### Gestione Romset
- **Scansione automatica** delle romset
- **Validazione** dei file ROM
- **Organizzazione** per piattaforma
- **Cache intelligente** per prestazioni ottimali

### Interfaccia Utente
- **Menu navigabile** con joystick
- **Anteprime** dei giochi
- **Informazioni dettagliate** (anno, genere, sviluppatore)
- **Screenshot** e video di gioco
- **Ricerca** e filtri avanzati

### Scraping Automatico
- **Immagini di copertina** da archive.org
- **Screenshot in-game** da adb.arcadeitalia.net
- **Informazioni dettagliate** sui giochi
- **Supporto multilingua** (italiano/inglese)

## 📁 Struttura del Progetto

```
LRscript/
├── __main__.py              # File principale
├── platforms.xml            # Configurazione piattaforme
├── joystick_mapping.json    # Mappatura controlli
├── code/                    # Moduli Python
│   ├── arcade_ui.py         # Interfaccia arcade
│   ├── game_scraper.py      # Scraping automatico
│   ├── joystick_manager.py  # Gestione controlli
│   └── platform_manager.py # Gestione piattaforme
├── resources/               # Risorse grafiche
│   ├── fonts/              # Font personalizzati
│   ├── icons/              # Icone controlli
│   └── logos/              # Logo piattaforme
├── cache/                  # Cache locale
└── log/                    # File di log
```

## ⚙️ Configurazione

### Piattaforme
Modifica `platforms.xml` per aggiungere nuove piattaforme:

```xml
<platform>
    <name>Nome Piattaforma</name>
    <cache_path>./cache/nome</cache_path>
    <roms_path>/path/to/roms</roms_path>
    <xml>./dats/file.dat</xml>
    <image>logo.png</image>
</platform>
```

### Controlli
Configura i controlli in `joystick_mapping.json`:

```json
{
    "up": "button_1",
    "down": "button_2",
    "left": "button_3",
    "right": "button_lr",
    "start": "button_start"
}
```

## 🔧 Sviluppo

### Clonare il Repository
```bash
git clone https://github.com/Skrokkio/LRscript.git
cd LRscript
```

### Installazione Dipendenze
```bash
pip3 install -r requirements.txt
```

### Esecuzione in Modalità Debug
```bash
python3 __main__.py --debug
```

## 📝 Log e Debug

I log vengono salvati in `log/log.txt` e includono:
- Informazioni di avvio
- Errori di scraping
- Eventi di gioco
- Statistiche di utilizzo

## 🤝 Contributi

1. **Fork** del repository
2. **Crea** un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. **Push** al branch (`git push origin feature/AmazingFeature`)
5. **Apri** una Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 🆘 Supporto

- **Issues**: [GitHub Issues](https://github.com/Skrokkio/LRscript/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/Skrokkio/LRscript/discussions)

## 🎯 Roadmap

- [ ] Supporto per più piattaforme
- [ ] Interfaccia web
- [ ] Cloud sync
- [ ] Plugin system
- [ ] Multiplayer support

---

**Sviluppato con ❤️ per la community retro gaming**

*LRscript - Il tuo gestore di giochi retro preferito!* 🎮
