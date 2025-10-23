# LRscript - Retro Game Manager


Attenzione Readme preliminare . work in progress

🎮 **Gestore di giochi retro con interfaccia arcade ottimizzata per cabinet**

Questo script prende libera ispirazione al ben migliore e piu' conosciuto RGSX script per 
sistemi Batocera.
Avevo necessità di avere uno script simile per Batocera ma che "pescasse" rom da Archive.

## Cosa fà questo script 
All' avvio carica il file platforms.xml e per ogni voce "<platform>" crea un pulsante nella app.
premendo il pulsante si carica il rispettivo Dat, e crea una lista di Roms col nome ufficiale.
Scegliendo un gioco nella lista, il programma cerca le informazioni utilizzando il nome della Rom ufficiale su internet usando il percorso  "<info>", e i media dal percorso dato in "<ingame>"  e  "<title>"

Infine premendo da tastiera Space oppure il relatico Button3 mappato col Joystick e' possibile scaricare la Rom nel percorso "<roms_path>"



## 🚀 Installazione Rapida

```bash
curl -L "https://tinyurl.com/lrscript" | sh

oppure 

curl -L "https://raw.githubusercontent.com/Skrokkio/LRscript/refs/heads/main/install.sh" | sh
```

## 📋 Caratteristiche Principali

- **🎯 Interfaccia Arcade**: Ottimizzata per cabinet con controlli joystick nativi
- **🎮 Multi-Piattaforma**: Supporta MAME, FBNeo, MAME 2003-Plus etc 
- **🖼️ Scraping Automatico**: Scarica immagini e informazioni dai siti specializzati
- **💾 Cache Locale**: Sistema di cache per immagini e dati
- **🎨 Interfaccia Grafica**: UI responsive con Pygame
- **📱 Controlli Joystick**: Supporto completo per gamepad e joystick arcade

## 🎮 Piattaforme Supportate

- **MAME** 
- **FBNeo**
- possibilità di aggiungere altre piattaforme editando file xml, il programma salva le Rom 
  nella cartella   "<roms_path>" specificata nel file platforms.xml. Attenzione se non esiste la crea! 

  
## 🛠️ Requisiti di Sistema
- **Batocera**
- **Python**
- **Pygame**
- **Requests**
-   Tutte queste dipendenze dovrebbero già fare parte di Batocera 

### Script di Avvio da menu di batocera Ports
LRscript.sh

## 🎯 Funzionalità
... 


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
Configura i controlli da batocera 
il file di configurazione comandi e'  joystick_mapping.json



## 📝 Log e Debug

I log vengono salvati in `log/log.txt` 


## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 🆘 Supporto

- **Issues**: [GitHub Issues](https://github.com/Skrokkio/LRscript/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/Skrokkio/LRscript/discussions)

## 🎯 Roadmap

- [ ] Supporto per più piattaforme
- [ ] modifiche e miglioramenti vari futuri

## Struttura attuale Work in progress

LRscript/
├── 📄 __main__.py                    # File principale dell'applicazione
├── 📄 platforms.xml                 # Configurazione piattaforme
├── 📄 joystick_mapping.json         # Mappatura pulsanti joystick
├── 📄 LRscript.sh                   # Script di avvio
├── 📄 install.sh                    # Script di installazione
├── 📄 README.md                     # Documentazione
│
├── 📁 code/                         # Codice sorgente modulare
│   ├── 📄 __init__.py
│   ├── 📄 arcade_ui.py              # Interfaccia arcade principale
│   ├── 📄 config_ui.py              # Interfaccia configurazione joystick
│   ├── 📄 constants.py              # Costanti e configurazioni
│   ├── 📄 game_scraper.py           # Scraper per informazioni giochi
│   ├── 📄 joystick_manager.py       # Gestore joystick
│   ├── 📄 platform_manager.py      # Gestore piattaforme
│   └── 📄 platform_menu.py          # Menu selezione piattaforme
│
├── 📁 resources/                    # Risorse grafiche e audio
│   ├── 📄 LRscript.png             # Logo applicazione
│   ├── 📄 sfondo_arcade.jpg        # Sfondo principale
│   │
│   ├── 📁 fonts/                   # Font personalizzati
│   │   ├── 📄 Free.ttf
│   │   ├── 📄 Mario.ttf
│   │   ├── 📄 Pixel-UniCode.ttf
│   │   └── 📄 zelek.ttf
│   │
│   ├── 📁 icons/                   # Icone pulsanti footer
│   │   ├── 📄 button_1.png
│   │   ├── 📄 button_2.png
│   │   ├── 📄 button_3.png
│   │   ├── 📄 button_lr.png
│   │   ├── 📄 button_start.png
│   │   └── 📄 system.png           # Icona configurazione
│   │
│   └── 📁 logos/                   # Loghi piattaforme
│       ├── 📄 arcade.png
│       ├── 📄 fbneo.png
│       ├── 📄 mame-libretro.png
│       ├── 📄 mame.png
│       ├── 📄 mame2003plus.png
│       └── 📄 mario.png
│
├── 📁 cache/                       # Cache immagini giochi
│   ├── 📁 FBNeo/
│   └── 📁 etc ...
│
├── 📁 dats/                        # File DAT per ROM
│   ├── 📄 FBNeo1.0.0.03.dat
│   ├── 📄 MAME0.139u4.dat
│   ├── 📄 etc ..
│
└── 📁 log/                         # File di log
    └── 📄 log.txt

**Sviluppato con ❤️ per il retro gaming**

*LRscript - by Skrokkio 2025* 🎮
