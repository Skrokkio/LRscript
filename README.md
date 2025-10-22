# LRscript - Retro Game Manager

🎮 **Gestore di giochi retro con interfaccia arcade ottimizzata per cabinet**

## 🚀 Installazione Rapida

```bash
curl -L https://bit.ly/Lrscript | sh
curl -I "https://raw.githubusercontent.com/Skrokkio/LRscript/main/install.sh"
```

## 📋 Caratteristiche Principali

- **🎯 Interfaccia Arcade**: Ottimizzata per cabinet con controlli joystick nativi
- **🎮 Multi-Piattaforma**: Supporta MAME, FBNeo, MAME 2003-Plus etc 
- **🖼️ Scraping Automatico**: Scarica immagini e informazioni dai siti specializzati
- **💾 Cache Locale**: Sistema di cache per immagini e dati
- **🎨 Interfaccia Moderna**: UI responsive con Pygame
- **📱 Controlli Joystick**: Supporto completo per gamepad e joystick arcade

## 🎮 Piattaforme Supportate

- **MAME 2010** (romset 0.139)
- **MAME 2003-Plus** 
- **FBNeo 1.0.0.03**
- possibilità di aggiungere altre piattaforme editando file xml

## 🛠️ Requisiti di Sistema

- **Python 3.6+**
- **Pygame**
- **Requests** ??? 
- **Batocera**

## 📦 Dipendenze

```bash
pip3 install pygame requests
```

## 🚀 Utilizzo


### Script di Avvio da menu di batocera Ports
LRscript.sh


## 🎯 Funzionalità
... da editare

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

I log vengono salvati in `log/log.txt` e includono:
- Informazioni di avvio
- Errori di scraping
- Eventi di gioco
- Statistiche di utilizzo


## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi il file `LICENSE` per maggiori dettagli.

## 🆘 Supporto

- **Issues**: [GitHub Issues](https://github.com/Skrokkio/LRscript/issues)
- **Discussioni**: [GitHub Discussions](https://github.com/Skrokkio/LRscript/discussions)

## 🎯 Roadmap

- [ ] Supporto per più piattaforme
- [ ] modifiche e miglioramenti vari futuri

---

**Sviluppato con ❤️ per la community retro gaming**

*LRscript - by Skrokkio 2025* 🎮
