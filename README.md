# LRscript - Retro Game Manager

[![Status](https://img.shields.io/badge/Status-Work%20in%20Progress-orange)](https://github.com/Skrokkio/LRscript)
[![Platform](https://img.shields.io/badge/Platform-Batocera-blue)](https://batocera.org)
[![Python](https://img.shields.io/badge/Python-3.x-green)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

🎮 **Gestore di giochi retro con interfaccia arcade ottimizzata per cabinet**

> ⚠️ **Attenzione**: Readme preliminare - work in progress

## 📑 Indice

- [🎯 Cosa fa questo script](#-cosa-fa-questo-script)
- [🚀 Installazione Rapida](#-installazione-rapida)
- [📋 Caratteristiche Principali](#-caratteristiche-principali)
- [🎮 Piattaforme Supportate](#-piattaforme-supportate)
- [🛠️ Requisiti di Sistema](#️-requisiti-di-sistema)
- [🎯 Funzionalità](#-funzionalità)
- [📁 Struttura del Progetto](#-struttura-del-progetto)
- [📝 Log e Debug](#-log-e-debug)
- [📄 Licenza](#-licenza)
- [🆘 Supporto](#-supporto)
- [🎯 Roadmap](#-roadmap)

## 🎯 Cosa fa questo script

Questo script prende libera ispirazione al ben migliore e più conosciuto RGSX script per sistemi Batocera.
Avevo necessità di avere uno script simile per Batocera ma che "pescasse" rom da Archive.

All'avvio carica il file `platforms.xml` e per ogni voce `<platform>` crea un pulsante nella app.
Premendo il pulsante si carica il rispettivo DAT, e crea una lista di ROMs col nome ufficiale.
Scegliendo un gioco nella lista, il programma cerca le informazioni utilizzando il nome della ROM ufficiale su internet usando il percorso `<info>`, e i media dal percorso dato in `<ingame>` e `<title>`.

Infine premendo da tastiera **Space** oppure il relativo **Button3** mappato col Joystick è possibile scaricare la ROM nel percorso `<roms_path>`.



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
- Possibilità di aggiungere altre piattaforme editando file XML, il programma salva le ROM nella cartella `<roms_path>` specificata nel file `platforms.xml`. **Attenzione**: se non esiste la crea!

## 🛠️ Requisiti di Sistema

- **Batocera**
- **Python**
- **Pygame**
- **Requests**

> 💡 Tutte queste dipendenze dovrebbero già fare parte di Batocera

### Script di Avvio da menu di Batocera Ports
`LRscript.sh`

## 🎯 Funzionalità

### 🔧 Piattaforme
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

### 🎮 Controlli
Configura i controlli da Batocera - il file di configurazione comandi è `joystick_mapping.json`



## 📝 Log e Debug

I log vengono salvati in `log/log.txt`

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 🆘 Supporto

- **Issues**: [GitHub Issues](https://github.com/Skrokkio/LRscript/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/Skrokkio/LRscript/discussions)

## 🎯 Roadmap

- [ ] Supporto per più piattaforme
- [ ] Modifiche e miglioramenti vari futuri

## 📁 Struttura del Progetto

```text
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
```

---

## 💝 Contributi

**Sviluppato con ❤️ per il retro gaming**

*LRscript - by Skrokkio 2025* 🎮
