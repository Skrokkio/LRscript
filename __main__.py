# -*- coding: utf-8 -*-

"""
LRscript - Retro Game Manager (Pygame Version)
=======================================================
Versione arcade con Pygame per controlli joystick nativi
e interfaccia ottimizzata per cabinet arcade.
"""

import pygame
import sys
import os
import time
import requests
import threading
import xml.etree.ElementTree as ET
import logging
import json
from datetime import datetime
from io import StringIO

# Configurazione logging
def setup_logging():
    """Configura il sistema di logging"""
    # Crea la cartella log se non esiste
    os.makedirs('log', exist_ok=True)
    
    # Cancella il file di log precedente per pulizia
    log_file = 'log/log.txt'
    if os.path.exists(log_file):
        os.remove(log_file)
    
    # Configura il logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()  # Mantiene anche l'output su console per errori critici
        ]
    )
    
    # Crea un logger specifico per l'applicazione
    logger = logging.getLogger('LRscript')
    logger.info("=== LRscript - Retro Game Manager ===")
    logger.info(f"Avvio applicazione: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return logger

# Inizializza il logging
logger = setup_logging()

# Inizializza Pygame
pygame.init()
pygame.joystick.init()

# Configurazione
CartellaHome = os.path.expanduser("~")
nomefilerom = "CIAO"
LinguaArcade = "&lang=it"

# =============================================================================
# CONFIGURAZIONE FONT - MODIFICA QUESTI VALORI PER CAMBIARE FONT E DIMENSIONI
# =============================================================================
FONT_NAME = "Pixel-UniCode.ttf"  # Nome del font da usare (Mario.ttf, zelek.ttf, Pixel-UniCode.ttf o None per font di sistema)
FONT_SCALE_FACTOR = 1.4  # Riduce le dimensioni del font (0.5 = metà, 1.0 = normale, 1.5 = più grande)
# =============================================================================

# Colori arcade ispirati a RGSX
ARCADE_COLORS = {
    'background': (26, 26, 26),        # Nero profondo
    'surface': (45, 45, 45),           # Grigio scuro
    'accent': (255, 107, 53),          # Arancione acceso
    'accent2': (78, 205, 196),         # Turchese
    'text': (255, 255, 255),           # Bianco
    'text_secondary': (204, 204, 204), # Grigio chiaro
    'border': (255, 107, 53),          # Bordo arancione
    'selected': (255, 107, 53),        # Elemento selezionato
    'button': (61, 61, 61),            # Grigio per pulsanti
    'button_hover': (77, 77, 77),      # Grigio più chiaro per hover
    'yellow': (249, 240, 107)          # Giallo per elementi speciali
}

# Configurazione schermo - Risoluzione dinamica
FPS = 60

# Funzione per ottenere la risoluzione del monitor
def get_screen_resolution():
    """Ottiene la risoluzione del monitor principale"""
    import pygame
    pygame.init()
    info = pygame.display.Info()
    return info.current_w, info.current_h

# Ottieni la risoluzione del monitor
SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_resolution()
logger.info(f"Risoluzione monitor rilevata: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")

# Font scalabili basati sulla risoluzione
def get_scaled_font_size(base_size, screen_width):
    """Calcola la dimensione del font basata sulla risoluzione dello schermo"""
    # Usa 1920 come risoluzione di riferimento
    scale_factor = screen_width / 1920.0
    # Applica il fattore di scala configurabile
    final_size = base_size * scale_factor * FONT_SCALE_FACTOR
    return max(int(final_size), 8)  # Minimo 8px per evitare font troppo piccoli

# Font scalabili
FONT_SIZE_LARGE = get_scaled_font_size(32, SCREEN_WIDTH)
FONT_SIZE_MEDIUM = get_scaled_font_size(24, SCREEN_WIDTH)
FONT_SIZE_SMALL = get_scaled_font_size(18, SCREEN_WIDTH)
FONT_SIZE_TINY = get_scaled_font_size(14, SCREEN_WIDTH)

logger.info(f"Font scalati per {SCREEN_WIDTH}x{SCREEN_HEIGHT} (fattore: {FONT_SCALE_FACTOR}): L={FONT_SIZE_LARGE}, M={FONT_SIZE_MEDIUM}, S={FONT_SIZE_SMALL}, T={FONT_SIZE_TINY}")

# Carica font personalizzato se disponibile
def load_custom_font():
    """Carica il font personalizzato se disponibile"""
    if FONT_NAME is None:
        logger.info("Font di sistema configurato, uso font di sistema")
        return None
    
    font_path = f"./resources/fonts/{FONT_NAME}"
    if os.path.exists(font_path):
        try:
            logger.info(f"Font personalizzato caricato: {font_path}")
            return font_path
        except Exception as e:
            logger.warning(f"Errore caricamento font personalizzato: {e}")
            return None
    else:
        logger.warning(f"Font personalizzato non trovato: {font_path}, uso font di sistema")
        return None

# Font personalizzato
CUSTOM_FONT_PATH = load_custom_font()

# PlatformManager è stato spostato in code/platform_manager.py

# PlatformMenu è stato spostato in code/platform_menu.py

# PlatformMenu è stato spostato in code/platform_menu.py

# ConfigUI è stata spostata in code/config_ui.py

# GameScraper e ImageDownloader sono stati spostati in code/game_scraper.py

# JoystickConfig e JoystickManager sono stati spostati in code/joystick_manager.py

# Import delle classi dai moduli separati
from code.platform_manager import PlatformManager
from code.platform_menu import PlatformMenu
from code.joystick_manager import JoystickManager, JoystickConfig
from code.config_ui import ConfigUI
from code.game_scraper import GameScraper, ImageDownloader


class ArcadeUI:
    """Interfaccia arcade principale"""
    
    def __init__(self):
        # Inizializza sempre con la risoluzione nativa del monitor
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("LRscript - Retro Game Manager")
        logger.info(f"Avviato in modalità fullscreen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
        logger.info("Premi F11 per passare a modalità finestra")
        
        # Font - usa font personalizzato se disponibile
        if CUSTOM_FONT_PATH:
            self.font_large = pygame.font.Font(CUSTOM_FONT_PATH, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(CUSTOM_FONT_PATH, FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.Font(CUSTOM_FONT_PATH, FONT_SIZE_SMALL)
            self.font_tiny = pygame.font.Font(CUSTOM_FONT_PATH, FONT_SIZE_TINY)
        else:
            self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
            self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
            self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)
            self.font_tiny = pygame.font.Font(None, FONT_SIZE_TINY)
        
        # Colori
        self.colors = ARCADE_COLORS
        
        # Componenti
        self.platform_manager = PlatformManager()
        self.platform_menu = PlatformMenu(self.platform_manager, SCREEN_WIDTH, SCREEN_HEIGHT, self.colors)
        self.game_scraper = GameScraper()
        self.image_downloader = ImageDownloader()
        self.joystick_manager = JoystickManager()
        
        # Tracking per tasto INVIO (hold function)
        self.enter_press_time = 0  # Timestamp quando è stato premuto INVIO
        self.enter_held = False    # Flag se INVIO è tenuto premuto
        self.enter_hold_time = 0.8  # Tempo per tenere premuto (secondi) - stesso del joystick
        
        # Aggiungi ConfigUI
        self.config_ui = ConfigUI(
            self.joystick_manager.config,
            SCREEN_WIDTH,
            SCREEN_HEIGHT,
            self.colors,
            {
                'large': self.font_large,
                'medium': self.font_medium,
                'small': self.font_small
            }
        )
        
        # Carica immagine di sfondo
        self.background_image = self.load_background_image()
        self.background_overlay_alpha = 128  # Trasparenza overlay fissa al 50%
        
        # Stato applicazione
        self.current_screen = 'menu'  # 'menu' o 'main'
        self.selected_platform = None
        
        # Stato UI
        self.current_section = 0  # 0: lista, 1: ricerca, 2: pulsanti
        self.selected_item = 0
        self.edit_mode = False
        self.search_text = ""
        self.games_list = []
        self.current_game_index = 0
        
        # Sistema di navigazione migliorato
        self.sections = ['lista', 'central_images', 'info']
        self.current_section_index = 0
        self.selected_central_image = 0  # Per la sezione immagini centrali
        
        # Immagini e informazioni gioco - solo titolo e ingame
        self.game_images = {
            'titolo': None,
            'ingame': None
        }
        self.game_info = {
            'name': '',
            'rom_name': '',
            'description': '',
            'year': '',
            'manufacturer': ''
        }
        
        # Variabili per scroll descrizione
        self.description_scroll = 0
        self.description_lines = []
        
        # Variabili per feedback joystick detection
        self.joystick_detection_message = ""
        self.joystick_detection_timer = 0
        self.joystick_detection_duration = 3.0  # Mostra per 3 secondi
        
        # Debug input
        self.last_input_message = ""
        self.last_input_timer = 0
        self.input_debug_duration = 2.0  # Mostra per 2 secondi
        
        # Download ROM confirmation
        self.download_confirmation_active = False
        self.download_info = {}
        self.download_state = None  # None, 'downloading', 'success', 'error'
        self.download_result_message = ""
        
        # Clock per FPS
        self.clock = pygame.time.Clock()
        
        # Carica le icone PNG per il footer
        self.footer_icons = self.load_footer_icons()
        
        # Non carichiamo più la lista giochi qui - verrà caricata quando si seleziona una piattaforma
    
    def load_footer_icons(self):
        """Carica le icone PNG per il footer"""
        icons = {}
        icon_size = (40, 40)  # Dimensione ottimizzata per le icone
        
        # Mappa delle icone e delle loro funzioni
        icon_config = {
            'button_1.png': 'info',      # Cerca Info
            'button_2.png': 'rom',       # Scarica ROM
            'button_3.png': 'download',  # Scarica ROM (Pulsante 3)
            'button_lr.png': 'scroll',   # L1/R1 Scrolling
            'button_start.png': 'start'  # Start/Esci
        }
        
        for png_file, function in icon_config.items():
            icon_path = f"./resources/icons/{png_file}"
            if os.path.exists(icon_path):
                # Carica direttamente il PNG
                icon = self.load_png_icon(icon_path, icon_size)
                if icon:
                    icons[function] = icon
                    logger.debug(f"Icona caricata: {png_file} -> {function}")
        
        logger.info(f"Caricate {len(icons)} icone PNG per il footer")
        return icons
    
    def load_png_icon(self, png_path, size):
        """Carica direttamente un'icona PNG in superficie Pygame"""
        try:
            # Carica direttamente il PNG con Pygame
            icon = pygame.image.load(png_path)
            # Ridimensiona se necessario
            icon = pygame.transform.scale(icon, size)
            return icon
        except Exception as e:
            logger.warning(f"Errore caricamento icona PNG {png_path}: {e}")
            return None
    
    def update_input_debug(self, input_type, key_name):
        """Aggiorna il messaggio di debug per l'input"""
        self.last_input_message = f"DEBUG {input_type}: {key_name}"
        self.last_input_timer = time.time()
        # Log solo per debug interno, non stampa nel terminale
        logger.debug(f"Input: {input_type}: {key_name}")
    
    def load_background_image(self):
        """Carica l'immagine di sfondo dell'applicazione"""
        try:
            background_path = "./resources/sfondo_arcade.jpg"
            if os.path.exists(background_path):
                logger.info(f"Caricamento sfondo: {background_path}")
                # Carica l'immagine
                background = pygame.image.load(background_path)
                # Ridimensiona l'immagine per adattarla alla risoluzione dello schermo
                background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
                logger.info(f"Sfondo caricato: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
                return background
            else:
                logger.warning(f"File sfondo non trovato: {background_path}")
                return None
        except Exception as e:
            logger.error(f"Errore caricamento sfondo: {e}")
            return None
    
    def load_games_list(self):
        """Carica la lista dei giochi dinamicamente dal file XML della piattaforma"""
        try:
            # Controlla se abbiamo un percorso XML per la piattaforma selezionata
            if hasattr(self, 'platform_paths') and self.platform_paths.get('xml_path'):
                xml_path = self.platform_paths['xml_path']
                if os.path.exists(xml_path):
                    self.games_list = self.load_games_from_xml(xml_path)
                    return
            else:
                    logger.warning(f"File XML non trovato: {xml_path}")
                    self.games_list = [f"Errore: File XML non trovato - {xml_path}"]
                    return
            
            # Se non c'è un percorso XML, mostra errore
            logger.error("Nessun file XML configurato per questa piattaforma")
            self.games_list = ["Errore: Nessun file XML configurato per questa piattaforma"]
            
        except Exception as e:
            logger.error(f"Errore caricamento lista: {e}")
            self.games_list = [f"Errore caricamento lista: {e}"]
    
    def load_games_from_xml(self, xml_path):
        """Carica la lista dei giochi dal file XML MAME"""
        try:
            logger.info(f"Caricamento giochi da XML: {xml_path}")
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            games_list = []
            game_count = 0
            
            # Itera attraverso tutti gli elementi <game>
            for game in root.findall('game'):
                # Ottieni il nome del gioco (attributo name)
                game_name = game.get('name', '')
                
                # Ottieni la descrizione
                description_elem = game.find('description')
                description = description_elem.text if description_elem is not None else game_name
                
                # Ottieni l'anno
                year_elem = game.find('year')
                year = year_elem.text if year_elem is not None else ''
                
                # Ottieni il produttore
                manufacturer_elem = game.find('manufacturer')
                manufacturer = manufacturer_elem.text if manufacturer_elem is not None else ''
                
                # Tronca la descrizione a 30 caratteri
                truncated_description = description[:30] + "..." if len(description) > 30 else description
                
                # Crea la stringa nel formato: "Nome_rom - Descrizione troncata"
                game_string = f"{game_name} - {truncated_description}"
                
                games_list.append(game_string)
                game_count += 1
                
            
            
            # Ordina la lista alfabeticamente per nome del gioco (prima parte prima della virgola)
            logger.info("Ordinamento alfabetico in corso...")
            games_list.sort(key=lambda x: x.split(' , ')[0].lower())
            logger.info("Ordinamento completato")
            
            return games_list
            
        except ET.ParseError as e:
            logger.error(f"Errore parsing XML: {e}")
            return []
        except Exception as e:
            logger.error(f"Errore caricamento XML: {e}")
            return []
    
    def load_test_images(self):
        """Carica immagini di test per dimostrare il funzionamento"""
        try:
            print("🖼️ Caricamento immagini di test...")
            
            # Non creiamo placeholder colorati all'avvio - mostreremo "IMAGE PREVIEW"
            self.game_images = {
                'titolo': None,   # Nessun placeholder all'avvio
                'ingame': None    # Nessun placeholder all'avvio
            }
            
            # Carica anche le informazioni di test
            if self.games_list:
                game_text = self.games_list[0]
                # Nuovo formato: "Nome_rom - Descrizione troncata (anno, produttore)"
                parts = game_text.split(' - ', maxsplit=1)
                if len(parts) >= 2:
                    rom_name = parts[0].strip()
                    description_part = parts[1].strip()
                    self.game_info = {
                        'name': description_part,
                        'rom_name': rom_name,
                        'description': f"Descrizione per {rom_name}. Gioco arcade classico con gameplay coinvolgente e grafiche caratteristiche dell'epoca.",
                        'year': "1980-1990",
                        'manufacturer': "Arcade Manufacturer"
                    }
                    
                    # Prepara le righe della descrizione per lo scroll
                    # Calcola la larghezza della sezione info dinamicamente
                    screen_info = self.get_screen_info()
                    screen_width = screen_info['width']
                    section_width = (screen_width - 40) // 3  # Larghezza sezione info
                    max_chars = self.get_description_max_chars(section_width)
                    self.description_lines = self.wrap_text(self.game_info['description'], max_chars)
                    self.description_scroll = 0  # Reset scroll
            
            logger.info("Immagini e informazioni di test caricate")
            
        except Exception as e:
            logger.error(f"Errore caricamento test: {e}")
    
    def handle_input(self, events):
        """Gestisce tutti gli input"""
        # Controlla periodicamente se è stato collegato un joystick
        if not self.joystick_manager.joystick_detected:
            self.joystick_manager.recheck_joystick()
        
        for event in events:
            if event.type == pygame.QUIT:
                logger.info("Chiusura applicazione...")
                return False
            elif event.type == pygame.KEYDOWN:
                result = self._handle_keyboard(event)
                if result == False:  # ESC premuto
                    return False
            elif event.type == pygame.KEYUP:
                result = self._handle_keyboard_release(event)
                if result == False:  # ESC premuto
                    return False
            elif event.type == pygame.JOYBUTTONDOWN:
                # Debug: mostra il numero del pulsante premuto
                self.update_input_debug("Joystick", f"Button {event.button}")
                
                # Se siamo in schermata config, gestisci TUTTI i pulsanti con ConfigUI
                if self.current_screen == 'config':
                    logger.info(f"Pulsante {event.button} premuto in schermata config, modalità cattura: {self.config_ui.capture_mode}")
                    if self.config_ui.capture_mode:
                        # In modalità cattura, passa il numero del pulsante
                        result = self.config_ui.handle_input(None, event.button)
                        logger.info(f"Risultato cattura pulsante: {result}")
                    else:
                        # In modalità normale, gestisci la configurazione con il joystick
                        config = self.joystick_manager.config.current_mapping
                        
                        # Se il pulsante premuto corrisponde al pulsante attualmente selezionato,
                        # entra in modalità cattura per quel pulsante
                        if self.config_ui.selected_index < len(self.config_ui.buttons):
                            selected_button_key = self.config_ui.buttons[self.config_ui.selected_index]
                            if event.button == config[selected_button_key]:
                                # Entra in modalità cattura per il pulsante selezionato
                                result = self.config_ui.handle_input('confirm')
                            elif event.button == config['button_1']:
                                result = self.config_ui.handle_input('confirm')
                            elif event.button == config['button_2']:
                                result = self.config_ui.handle_input('back')
                            elif event.button == config['button_3']:
                                result = self.config_ui.handle_input('download_rom')
                            elif event.button == config['l1']:
                                result = self.config_ui.handle_input('scroll_up')
                            elif event.button == config['r1']:
                                result = self.config_ui.handle_input('scroll_down')
                            elif event.button == config['select']:
                                result = self.config_ui.handle_input('back')
                            else:
                                result = None
                        else:
                            # Se siamo sui pulsanti di controllo (SALVA/RESET), usa i controlli standard
                            if event.button == config['button_1']:
                                result = self.config_ui.handle_input('confirm')
                            elif event.button == config['button_2']:
                                result = self.config_ui.handle_input('back')
                            elif event.button == config['l1']:
                                result = self.config_ui.handle_input('scroll_up')
                            elif event.button == config['r1']:
                                result = self.config_ui.handle_input('scroll_down')
                            elif event.button == config['select']:
                                result = self.config_ui.handle_input('back')
                            else:
                                result = None
                    
                    if result == 'exit':
                        logger.info("Uscita dalla schermata config")
                        self.current_screen = 'menu'
                    
                    # IMPORTANTE: In schermata config, NON processare il pulsante con JoystickManager normale
                    # Usa 'continue' per saltare al prossimo evento
                    continue
                
                # Solo se NON siamo in schermata config, processa con JoystickManager
                action = self.joystick_manager._handle_button_press(event.button, time.time(), in_config_screen=(self.current_screen == 'config'))
                if action:
                    result = self._handle_joystick_action(action)
                    if result == False:  # Start premuto per uscita
                        return False
            elif event.type == pygame.JOYBUTTONUP:
                # Gestisci il rilascio del pulsante
                action = self.joystick_manager._handle_button_release(event.button, time.time())
                if action:
                    result = self._handle_joystick_action(action)
                    if result == False:  # Start premuto per uscita
                        return False
            elif event.type == pygame.JOYHATMOTION:
                # Debug: mostra il movimento del D-Pad
                hat_names = {0: "Center", 1: "Up", 2: "Right", 3: "Up+Right", 4: "Down", 5: "Down+Right", 6: "Left", 7: "Up+Left", 8: "Down+Left"}
                hat_name = hat_names.get(event.value, f"Unknown({event.value})")
                self.update_input_debug("Joystick", f"D-Pad {hat_name}")
                action = self.joystick_manager._handle_hat_motion(event.value, time.time())
                if action:
                    result = self._handle_joystick_action(action)
                    if result == False:  # Start premuto per uscita
                        return False
            elif event.type == pygame.JOYAXISMOTION:
                # Debug: mostra il movimento degli assi analogici
                if abs(event.value) > 0.5:  # Solo se il movimento è significativo
                    axis_names = {0: "Left Stick X", 1: "Left Stick Y", 2: "Right Stick X", 3: "Right Stick Y", 4: "L2", 5: "R2"}
                    axis_name = axis_names.get(event.axis, f"Axis {event.axis}")
                    direction = "Left" if event.value < -0.5 else "Right" if event.value > 0.5 else "Center"
                    if event.axis in [1, 3]:  # Assi Y
                        direction = "Up" if event.value < -0.5 else "Down" if event.value > 0.5 else "Center"
                    self.update_input_debug("Joystick", f"{axis_name} {direction}")
                action = self.joystick_manager._handle_axis_motion(event.axis, event.value, time.time())
                if action:
                    result = self._handle_joystick_action(action)
                    if result == False:  # Start premuto per uscita
                        return False
        
        # Controlla scorrimento veloce solo se non siamo nel menu
        if self.current_screen == 'main':
            # Controlla D-pad per scrolling veloce
            fast_scroll = self.joystick_manager.check_fast_scroll()
            if fast_scroll:
                result = self._handle_joystick_action(fast_scroll)
                if result == False:  # Select + Start premuti
                    return False
            
            # Controlla L1/R1 per scrolling veloce continuo
            l1_r1_scroll = self.joystick_manager.check_l1_r1_fast_scroll()
            if l1_r1_scroll:
                if l1_r1_scroll == 'l1_fast_scroll_up':
                    self.l1_fast_scroll_up()
                elif l1_r1_scroll == 'r1_fast_scroll_down':
                    self.r1_fast_scroll_down()
        
        return True
    
    def _handle_keyboard_release(self, event):
        """Gestisce il rilascio dei tasti da tastiera"""
        if event.key == pygame.K_RETURN:
            # Gestisci il rilascio del tasto INVIO per la funzione hold
            if self.enter_press_time > 0:
                current_time = time.time()
                # Se è stato tenuto premuto abbastanza a lungo, invia segnale hold
                if (current_time - self.enter_press_time >= self.enter_hold_time and 
                    not self.enter_held):
                    self.enter_held = True
                    self.enter_press_time = 0  # Reset per evitare trigger multipli
                    # Gestisci hold nel menu delle piattaforme
                    if self.current_screen == 'menu':
                        result = self.platform_menu.handle_input('confirm_hold')
                        if result:
                            self._handle_joystick_action(result)
                    return
                # Se non è stato tenuto abbastanza a lungo, invia confirm normale
                elif self.enter_press_time > 0:
                    self.enter_press_time = 0
                    self.enter_held = False
                    # Gestisci confirm normale
                    if self.current_screen == 'menu':
                        selected_platform = self.platform_menu.handle_input('confirm')
                        if selected_platform:
                            if selected_platform == 'config':
                                self.current_screen = 'config'
                            else:
                                self.select_platform(selected_platform)
                    elif self.current_screen == 'main':
                        self.confirm_action()
                    elif self.current_screen == 'config':
                        result = self.config_ui.handle_input('confirm')
                        if result == 'exit':
                            self.current_screen = 'menu'
                    return
                else:
                    self.enter_press_time = 0
                    self.enter_held = False
        return True
    
    def _handle_keyboard(self, event):
        """Gestisce input tastiera"""
        # Debug: mostra il tasto premuto
        key_name = pygame.key.name(event.key)
        self.update_input_debug("Tastiera", key_name)
        
        # Se siamo in schermata config
        if self.current_screen == 'config':
            # Gestisci input per la configurazione
            if event.key == pygame.K_UP:
                result = self.config_ui.handle_input('up')
            elif event.key == pygame.K_DOWN:
                result = self.config_ui.handle_input('down')
            elif event.key == pygame.K_RETURN:
                # Inizia il tracking del tempo di pressione per la funzione hold
                self.enter_press_time = time.time()
                self.enter_held = False
                # Non processare immediatamente, aspetta il rilascio
            elif event.key == pygame.K_ESCAPE:
                result = self.config_ui.handle_input('back')
            else:
                return  # Ignora altri tasti
            
            if result == 'exit':
                self.current_screen = 'menu'
            return
        
        # Gestisci conferma download ROM
        if self.download_confirmation_active:
            # Se è in stato di risultato, qualsiasi tasto chiude
            if self.download_state in ['success', 'error']:
                if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE]:
                    self.download_confirmation_active = False
                    self.download_info = {}
                    self.download_state = None
                    self.download_result_message = ""
                return
            
            # Se è in downloading, blocca l'input
            if self.download_state == 'downloading':
                return
            
            # Altrimenti gestione normale conferma/annulla
            if event.key == pygame.K_SPACE:  # Stesso tasto usato per aprire il modal
                # Verifica se la cartella esiste prima di permettere la conferma
                if self.download_info.get('folder_exists', False):
                    self.confirm_download()
                else:
                    print("❌ Conferma non disponibile: cartella destinazione non presente")
                return
            elif event.key == pygame.K_ESCAPE:
                self.cancel_download()
                return
        
        if event.key == pygame.K_ESCAPE:
            if self.current_screen == 'main':
                # Torna al menu
                self.current_screen = 'menu'
                logger.info("Torno al menu delle piattaforme")
            else:
                logger.info("Chiusura applicazione...")
            return False
        elif event.key == pygame.K_BACKSPACE:
            # Backspace come funzione back/cancel
            if self.current_screen == 'main':
                # Torna al menu delle piattaforme
                self.current_screen = 'menu'
                logger.info("Backspace: Torno al menu delle piattaforme")
            else:
                # Nel menu, backspace non fa nulla (non c'è livello precedente)
                logger.debug("Backspace: Nel menu - nessuna azione")
        elif event.key == pygame.K_F11:
            self.toggle_fullscreen()
        elif self.current_screen == 'menu':
            # Gestisci input nel menu delle piattaforme
            if event.key == pygame.K_UP:
                selected_platform = self.platform_menu.handle_input('up')
                if selected_platform:
                    self.select_platform(selected_platform)
            elif event.key == pygame.K_DOWN:
                selected_platform = self.platform_menu.handle_input('down')
                if selected_platform:
                    self.select_platform(selected_platform)
            elif event.key == pygame.K_LEFT:
                selected_platform = self.platform_menu.handle_input('left')
                if selected_platform:
                    self.select_platform(selected_platform)
            elif event.key == pygame.K_RIGHT:
                selected_platform = self.platform_menu.handle_input('right')
                if selected_platform:
                    self.select_platform(selected_platform)
            elif event.key == pygame.K_RETURN:
                # Inizia il tracking del tempo di pressione per la funzione hold
                self.enter_press_time = time.time()
                self.enter_held = False
                # Non processare immediatamente, aspetta il rilascio
        else:
            # Gestisci input nella schermata principale
            if event.key == pygame.K_UP:
                self.navigate_up()
            elif event.key == pygame.K_DOWN:
                self.navigate_down()
            elif event.key == pygame.K_LEFT:
                self.navigate_left()
            elif event.key == pygame.K_RIGHT:
                self.navigate_right()
            elif event.key == pygame.K_RETURN:
                # Inizia il tracking del tempo di pressione per la funzione hold
                self.enter_press_time = time.time()
                self.enter_held = False
                # Non processare immediatamente, aspetta il rilascio
            elif event.key == pygame.K_SPACE:
                self.alternative_action()
            elif event.key == pygame.K_l:
                # L per cambiare sezione a sinistra
                self.current_section_index = (self.current_section_index - 1) % len(self.sections)
                print(f"Sezione: {self.sections[self.current_section_index]}")
            elif event.key == pygame.K_r:
                # R per cambiare sezione a destra
                self.current_section_index = (self.current_section_index + 1) % len(self.sections)
                print(f"Sezione: {self.sections[self.current_section_index]}")
            elif event.key == pygame.K_j:
                # J per forzare il rilevamento del joystick
                self.joystick_manager.detect_joystick()
                if self.joystick_manager.joystick_detected:
                    self.joystick_detection_message = f"✅ Joystick rilevato: {self.joystick_manager.joystick_name}"
                else:
                    self.joystick_detection_message = "❌ Nessun joystick valido rilevato"
                self.joystick_detection_timer = time.time()
        
        return True
    
    def _handle_joystick_action(self, action):
        """Gestisce azioni joystick"""
        # Se siamo in schermata config
        if self.current_screen == 'config':
            # Gestisci input per la configurazione
            result = self.config_ui.handle_input(action)
            if result == 'exit':
                self.current_screen = 'menu'
            return
        
        # Gestisci conferma download ROM
        if self.download_confirmation_active:
            # Se è in stato di risultato, qualsiasi pulsante chiude
            if self.download_state in ['success', 'error']:
                if action in ['confirm', 'back']:
                    self.download_confirmation_active = False
                    self.download_info = {}
                    self.download_state = None
                    self.download_result_message = ""
                return
            
            # Se è in downloading, blocca l'input
            if self.download_state == 'downloading':
                return
            
            # Altrimenti gestione normale conferma/annulla
            if action == 'confirm':  # Pulsante 1 - Conferma download
                # Verifica se la cartella esiste prima di permettere la conferma
                if self.download_info.get('folder_exists', False):
                    self.confirm_download()
                else:
                    print("❌ Conferma non disponibile: cartella destinazione non presente")
                return
            elif action == 'back':  # Pulsante 2 - Annulla download
                self.cancel_download()
                return
        
        # Gestisci l'azione di uscita prima di tutto
        if action == 'quit_app':
            print("👋 Chiusura applicazione...")
            return False  # Indica che l'applicazione deve chiudersi
        elif action == 'back':
            # Backspace/Back come funzione back/cancel
            if self.current_screen == 'main':
                # Torna al menu delle piattaforme
                self.current_screen = 'menu'
                logger.info("Back: Torno al menu delle piattaforme")
            else:
                # Nel menu, back non fa nulla (non c'è livello precedente)
                logger.debug("Back: Nel menu - nessuna azione")
        
        if self.current_screen == 'menu':
            # Gestisci input nel menu delle piattaforme
            if action == 'confirm_hold':
                # Gestisci il tenere premuto per aprire menu immagini
                result = self.platform_menu.handle_input('confirm_hold')
                if result:
                    self._handle_joystick_action(result)
            else:
                selected_platform = self.platform_menu.handle_input(action)
                if selected_platform:
                    if selected_platform == 'config':
                        self.current_screen = 'config'
                    else:
                        self.select_platform(selected_platform)
        else:
            # Gestisci input nella schermata principale
            if action == 'up':
                self.navigate_up()
            elif action == 'down':
                self.navigate_down()
            elif action == 'left':
                self.navigate_left()
            elif action == 'right':
                self.navigate_right()
            elif action == 'confirm_hold':
                # Gestisci il tenere premuto per aprire menu immagini
                if hasattr(self, 'platform_menu'):
                    result = self.platform_menu.handle_input('confirm_hold')
                    if result:
                        self._handle_joystick_action(result)
            elif action == 'confirm':
                self.confirm_action()
            elif action == 'alternative':
                # Space - download ROM
                self.download_rom()
            elif action == 'download_rom':
                # Pulsante 3 - download ROM
                self.download_rom()
            elif action == 'search_info':
                # B del joystick - download ROM
                self.download_rom()
            elif action == 'fast_scroll_up':
                self.fast_scroll_up()
            elif action == 'fast_scroll_down':
                self.fast_scroll_down()
            elif action == 'scroll_up' or action == 'scroll_down':
                # L1 e R1 ora vengono usati per scorrimento veloce della lista
                if action == 'scroll_up':  # L1 - scorrimento veloce verso l'alto
                    self.fast_scroll_up()
                else:  # R1 - scorrimento veloce verso il basso
                    self.fast_scroll_down()
        
        return True  # Continua l'esecuzione
    
    def select_platform(self, platform):
        """Seleziona una piattaforma e passa alla schermata principale"""
        self.selected_platform = platform
        self.current_screen = 'main'
        logger.info(f"Piattaforma selezionata: {platform['name']}")
        
        # Aggiorna i percorsi dinamici per questa piattaforma
        self.update_platform_paths(platform)
        
        # Carica la lista giochi per questa piattaforma
        self.load_games_list()
        
        # Carica immagini di test per il primo gioco
        if self.games_list:
            self.load_test_images()
    
    def update_platform_paths(self, platform):
        """Aggiorna i percorsi dinamici basati sulla piattaforma selezionata"""
        # Salva i percorsi della piattaforma per uso futuro
        self.platform_paths = {
            'cache_path': platform['path'],
            'roms_path': platform['roms_path'],
            'xml_path': platform['xml'],
            'ingame_url': platform['ingame'],
            'title_url': platform['title'],
            'info_url': platform['info'],
            'rom_url': platform['rom']
        }
        logger.info(f"Percorsi aggiornati per: {platform['name']}")
        logger.debug(f"Cache: {platform['path']}")
        if platform['xml']:
            logger.debug(f"XML: {platform['xml']}")
        logger.debug(f"Info: {platform['info']}")
    
    def navigate_up(self):
        """Naviga verso l'alto"""
        if self.current_section_index == 0:  # Lista
            if self.current_game_index > 0:
                self.current_game_index -= 1
        elif self.current_section_index == 2:  # Sezione info
            # Scroll descrizione su
            if self.description_scroll > 0:
                self.description_scroll -= 1
                print(f"📜 Scroll descrizione: {self.description_scroll}")
        
        # Scroll descrizione con tasti speciali
        if pygame.key.get_pressed()[pygame.K_PAGEUP] or pygame.key.get_pressed()[pygame.K_HOME]:
            if self.description_scroll > 0:
                self.description_scroll -= 1
                print(f"📜 Scroll descrizione: {self.description_scroll}")
    
    def navigate_down(self):
        """Naviga verso il basso"""
        if self.current_section_index == 0:  # Lista
            if self.current_game_index < len(self.games_list) - 1:
                self.current_game_index += 1
        elif self.current_section_index == 2:  # Sezione info
            # Scroll descrizione giù
            max_visible_lines = self.get_max_visible_description_lines()
            max_scroll = max(0, len(self.description_lines) - max_visible_lines)
            if self.description_scroll < max_scroll:
                self.description_scroll += 1
                print(f"📜 Scroll descrizione: {self.description_scroll}")
        
        # Scroll descrizione con tasti speciali
        if pygame.key.get_pressed()[pygame.K_PAGEDOWN] or pygame.key.get_pressed()[pygame.K_END]:
            max_visible_lines = self.get_max_visible_description_lines()
            max_scroll = max(0, len(self.description_lines) - max_visible_lines)
            if self.description_scroll < max_scroll:
                self.description_scroll += 1
                print(f"📜 Scroll descrizione: {self.description_scroll}")
    
    def navigate_left(self):
        """Naviga verso sinistra - salta 40 righe indietro nella lista"""
        if self.current_section_index == 0:  # Se siamo nella lista, saltiamo 40 righe indietro
            new_index = max(0, self.current_game_index - 40)
            if new_index != self.current_game_index:
                self.current_game_index = new_index
                print(f"⏫ Salto di 40 righe indietro: posizione {self.current_game_index}/{len(self.games_list)-1}")
    
    def navigate_right(self):
        """Naviga verso destra - salta 40 righe nella lista"""
        if self.current_section_index == 0:  # Se siamo nella lista, saltiamo 40 righe
            new_index = min(len(self.games_list) - 1, self.current_game_index + 40)
            if new_index != self.current_game_index:
                self.current_game_index = new_index
                print(f"⏬ Salto di 40 righe: posizione {self.current_game_index}/{len(self.games_list)-1}")
    
    def fast_scroll_up(self):
        """Scorrimento veloce verso l'alto - salta sempre 20 righe per D-pad"""
        if self.current_section_index == 0:  # Solo nella lista
            scroll_amount = 20  # Salta sempre 20 righe per il D-pad
            
            # Calcola la posizione di destinazione
            new_index = max(0, self.current_game_index - scroll_amount)
            
            # Aggiorna solo se è cambiato
            if new_index != self.current_game_index:
                self.current_game_index = new_index
                print(f"⏫ Salto di 20 righe: posizione {self.current_game_index}/{len(self.games_list)-1}")
    
    def fast_scroll_down(self):
        """Scorrimento veloce verso il basso - salta sempre 20 righe per D-pad"""
        if self.current_section_index == 0:  # Solo nella lista
            scroll_amount = 20  # Salta sempre 20 righe per il D-pad
            
            # Calcola la posizione di destinazione
            new_index = min(len(self.games_list) - 1, self.current_game_index + scroll_amount)
            
            # Aggiorna solo se è cambiato
            if new_index != self.current_game_index:
                self.current_game_index = new_index
                print(f"⏬ Salto di 20 righe: posizione {self.current_game_index}/{len(self.games_list)-1}")
    
    def l1_fast_scroll_up(self):
        """Scorrimento veloce continuo verso l'alto con L1 - salta 5 righe alla volta"""
        if self.current_section_index == 0:  # Solo nella lista
            scroll_amount = 5  # Salta 5 righe alla volta per L1 continuo
            
            new_index = max(0, self.current_game_index - scroll_amount)
            if new_index != self.current_game_index:
                self.current_game_index = new_index
                print(f"⏫ L1 continuo: posizione {self.current_game_index}/{len(self.games_list)-1}")
    
    def r1_fast_scroll_down(self):
        """Scorrimento veloce continuo verso il basso con R1 - salta 5 righe alla volta"""
        if self.current_section_index == 0:  # Solo nella lista
            scroll_amount = 5  # Salta 5 righe alla volta per R1 continuo
            
            new_index = min(len(self.games_list) - 1, self.current_game_index + scroll_amount)
            if new_index != self.current_game_index:
                self.current_game_index = new_index
                print(f"⏬ R1 continuo: posizione {self.current_game_index}/{len(self.games_list)-1}")
    
    def confirm_action(self):
        """Conferma azione"""
        if self.current_section_index == 0:  # Lista
            self.select_game()
            # Cerca automaticamente le informazioni e le immagini quando si seleziona un gioco
            self.search_game_info()
        elif self.current_section_index == 1:  # Immagini centrali
            # Azione per le immagini centrali
            pass
        elif self.current_section_index == 2:  # Informazioni
            # Azione per la sezione informazioni
            pass
    
    def alternative_action(self):
        """Azione alternativa - Download ROM"""
        if self.current_section_index == 0:  # Lista
            # Space per avviare download ROM
            self.select_game()
            self.download_rom()
        elif self.current_section_index == 1:  # Immagini centrali
            # Azione per le immagini centrali
            pass
        elif self.current_section_index == 2:  # Informazioni
            # Azione per la sezione informazioni
            pass
    
    def select_game(self):
        """Seleziona un gioco dalla lista"""
        if self.current_game_index < len(self.games_list):
            game_name = self.games_list[self.current_game_index]
            logger.info(f"Gioco selezionato: {game_name}")
            # Cerca automaticamente le informazioni quando si seleziona un gioco
            self.search_game_info()
    
    def search_games(self):
        """Cerca giochi"""
        if self.search_text.strip():
            print(f"🔍 Ricerca: {self.search_text}")
            # Qui implementeresti la logica di ricerca
    
    def get_game_name_from_xml(self, rom_name):
        """Estrae il nome del gioco dal file XML della piattaforma"""
        try:
            if not hasattr(self, 'platform_paths') or not self.platform_paths.get('xml_path'):
                return rom_name
            
            xml_path = self.platform_paths['xml_path']
            if not os.path.exists(xml_path):
                print(f"⚠️ File XML non trovato: {xml_path}")
                return rom_name
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Cerca il gioco con il nome ROM specificato
            for game in root.findall('game'):
                if game.get('name') == rom_name:
                    description = game.find('description')
                    if description is not None:
                        return description.text
                    break
            
            return rom_name
        except Exception as e:
            print(f"❌ Errore lettura XML: {e}")
            return rom_name
    
    def download_rom(self):
        """Avvia il processo di download ROM con conferma"""
        if self.current_game_index < len(self.games_list):
            game_name = self.games_list[self.current_game_index]
            rom_name = game_name.split(' - ')[0].strip()  # Estrae il nome ROM (prima parte prima di " - ")
            
            # Ottieni il nome completo del gioco dal XML
            full_game_name = self.get_game_name_from_xml(rom_name)
            
            # Costruisci il percorso completo
            if hasattr(self, 'platform_paths') and self.platform_paths.get('roms_path'):
                roms_path = self.platform_paths['roms_path']
                full_rom_path = f"{roms_path}/{rom_name}.zip"
                
                # Costruisci l'URL della ROM usando la variabile <rom> dal XML
                rom_base_url = self.platform_paths.get('rom_url', '')
                # Lista delle estensioni da provare in ordine di preferenza
                rom_extensions = ['zip', '7z']
                rom_download_urls = [f"{rom_base_url}{rom_name}.{ext}" for ext in rom_extensions]
                
                # Verifica se la cartella di destinazione esiste
                folder_exists = os.path.exists(roms_path)
                
                # Salva le informazioni per la conferma
                self.download_info = {
                    'rom_name': rom_name,
                    'full_game_name': full_game_name,
                    'full_rom_path': full_rom_path,
                    'roms_path': roms_path,
                    'rom_download_urls': rom_download_urls,  # Lista di URL da provare
                    'rom_extensions': rom_extensions,  # Lista delle estensioni
                    'folder_exists': folder_exists
                }
                
                # Attiva la modalità di conferma
                self.download_confirmation_active = True
                
                logger.info(f"🔄 Download ROM: {full_game_name}")
                logger.info(f"📁 Percorso destinazione: {full_rom_path}")
                logger.info(f"🎮 Nome ROM: {rom_name} (proverà: {', '.join(rom_extensions)})")
                logger.info(f"🌐 URL download da provare: {len(rom_download_urls)} opzioni")
                for i, url in enumerate(rom_download_urls):
                    logger.info(f"   {i+1}. {url}")
                logger.info(f"📂 Cartella destinazione: {'✅ Presente' if folder_exists else '❌ Non presente'}")
                if folder_exists:
                    logger.info("✅ [Premi SPACE/Pulsante 1 per confermare o ESC/Pulsante 2 per annullare]")
                else:
                    logger.warning("⚠️ [Cartella non presente - Download non disponibile]")
            else:
                logger.error(f"❌ Percorso ROM non configurato per la piattaforma")
        else:
            logger.warning("❌ Nessun gioco selezionato per il download")
    
    def confirm_download(self):
        """Conferma e avvia il download della ROM"""
        if self.download_confirmation_active and self.download_info:
            # Verifica se la cartella di destinazione esiste
            if not self.download_info.get('folder_exists', False):
                logger.error(f"❌ Download annullato: cartella destinazione non presente")
                logger.error(f"📁 Cartella richiesta: {self.download_info['roms_path']}")
                self.download_confirmation_active = False
                self.download_info = {}
                self.download_state = None
                self.download_result_message = ""
                return
            
            logger.info(f"✅ Download confermato!")
            logger.info(f"🔄 Avvio download: {self.download_info['full_game_name']}")
            logger.info(f"📁 Destinazione: {self.download_info['full_rom_path']}")
            urls = self.download_info.get('rom_download_urls', [])
            logger.info(f"🌐 URL download da provare: {len(urls)} opzioni")
            for i, url in enumerate(urls):
                logger.info(f"   {i+1}. {url}")
            
            # Imposta stato "downloading"
            self.download_state = 'downloading'
            
            # Avvia il download effettivo
            success = self.download_rom_file()
            
            # Imposta stato finale
            if success:
                self.download_state = 'success'
                self.download_result_message = f"Download completato: {self.download_info['rom_name']}.zip"
                logger.info(f"🎉 Download completato con successo!")
            else:
                self.download_state = 'error'
                self.download_result_message = "Download fallito. Controlla il log per i dettagli."
                logger.error(f"💥 Download fallito!")
            
            # NON chiudere il modal qui - rimane aperto per mostrare il risultato
    
    def cancel_download(self):
        """Annulla il download della ROM"""
        if self.download_confirmation_active:
            logger.info("❌ Download annullato")
            self.download_confirmation_active = False
            self.download_info = {}
            self.download_state = None
            self.download_result_message = ""
    
    def download_rom_file(self):
        """Scarica effettivamente la ROM dal server con sistema di fallback per le estensioni"""
        rom_name = self.download_info['rom_name']
        rom_download_urls = self.download_info.get('rom_download_urls', [])
        rom_extensions = self.download_info.get('rom_extensions', ['zip'])
        
        logger.info(f"🔄 Avvio download ROM: {rom_name}")
        logger.info(f"📋 Estensioni da provare: {', '.join(rom_extensions)}")
        
        # Crea la directory di destinazione se non esiste
        dest_dir = os.path.dirname(self.download_info['full_rom_path'])
        os.makedirs(dest_dir, exist_ok=True)
        logger.info(f"📂 Directory creata: {dest_dir}")
        
        # Prova ogni estensione in sequenza
        for i, (url, extension) in enumerate(zip(rom_download_urls, rom_extensions)):
            full_rom_path = f"{self.download_info['roms_path']}/{rom_name}.{extension}"
            
            logger.info(f"🎯 Tentativo {i+1}/{len(rom_download_urls)}: {extension.upper()}")
            logger.info(f"🌐 URL: {url}")
            logger.info(f"📁 Destinazione: {full_rom_path}")
            
            try:
                # Effettua il download
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Ottieni la dimensione del file
                total_size = int(response.headers.get('content-length', 0))
                logger.info(f"📏 Dimensione file: {total_size // (1024*1024)}MB" if total_size > 0 else "📏 Dimensione file: Sconosciuta")
                
                # Scrivi il file
                downloaded = 0
                with open(full_rom_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # Log progresso ogni 1MB
                            if downloaded % (1024 * 1024) == 0:
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    logger.info(f"📥 Download: {downloaded // (1024*1024)}MB / {total_size // (1024*1024)}MB ({progress:.1f}%)")
                                else:
                                    logger.info(f"📥 Download: {downloaded // (1024*1024)}MB")
                
                # Verifica che il file sia stato scaricato
                if os.path.exists(full_rom_path):
                    file_size = os.path.getsize(full_rom_path)
                    logger.info(f"✅ Download completato: {rom_name}.{extension}")
                    logger.info(f"📏 Dimensione file scaricato: {file_size // (1024*1024)}MB")
                    logger.info(f"📁 File salvato in: {full_rom_path}")
                    return True
                else:
                    logger.error(f"❌ Errore: File non trovato dopo il download")
                    continue
                    
            except requests.exceptions.RequestException as e:
                logger.warning(f"⚠️ Download fallito per {extension.upper()}: {e}")
                if i < len(rom_download_urls) - 1:
                    logger.info(f"🔄 Provo con la prossima estensione...")
                continue
            except Exception as e:
                logger.warning(f"⚠️ Errore durante il download {extension.upper()}: {e}")
                if i < len(rom_download_urls) - 1:
                    logger.info(f"🔄 Provo con la prossima estensione...")
                continue
        
        # Se arriviamo qui, tutti i tentativi sono falliti
        logger.error(f"❌ Download fallito per tutte le estensioni: {', '.join(rom_extensions)}")
        return False
    
    def search_game_info(self):
        """Cerca informazioni del gioco selezionato"""
        if self.current_game_index < len(self.games_list):
            game_text = self.games_list[self.current_game_index]
            # Nuovo formato: "Nome_rom - Descrizione troncata (anno, produttore)"
            parts = game_text.split(' - ', maxsplit=1)
            if len(parts) >= 2:
                rom_name = parts[0].strip()
                description_part = parts[1].strip()
                # Estrai il nome completo dalla descrizione (prima parte)
                game_name = description_part
                
                print(f"🔍 Cerca info per: {game_name} ({rom_name})")
                
                # Inizializza con valori predefiniti
                self.game_info = {
                    'name': game_name,
                    'rom_name': rom_name,
                    'description': f"Caricamento informazioni per {game_name}...",
                    'year': "N/A",
                    'manufacturer': "N/A"
                }
                
                # URL per le informazioni del gioco (dinamico basato sulla piattaforma)
                if hasattr(self, 'platform_paths') and self.platform_paths['info_url']:
                    # Sostituisci {rom_name} con il nome ROM effettivo
                    url = self.platform_paths['info_url'].replace('{rom_name}', rom_name)
                else:
                    # Fallback al URL originale
                    url = f"adb.arcadeitalia.net/service_scraper.php?ajax=query_mame&game_name={rom_name}&lang=it"
                print(f"🔗 URL API: {url}")
                
                try:
                    # Aggiunge il protocollo per la richiesta HTTP
                    http_url = f"http://{url}"
                    print(f"🌐 URL completo API: {http_url}")
                    
                    # Effettua la richiesta HTTP
                    response = requests.get(http_url, timeout=10)
                    print(f"📊 Status Code API: {response.status_code}")
                    print(f"📏 Dimensione risposta: {len(response.content)} bytes")
                    
                    if response.status_code == 200:
                        # Analizza la risposta JSON
                        data = response.json()
                        
                        if data.get('result') and len(data['result']) > 0:
                            result = data['result'][0]
                            
                            # Estrai le informazioni (come nel codice originale)
                            description = result.get('history', "Nessuna descrizione disponibile")
                            title = result.get('title', game_name)
                            year = result.get('year', "N/A")
                            manufacturer = result.get('manufacturer', "N/A")
                            clone_of = result.get('cloneof', "N/A")
                            
                            # Formatta la descrizione con a capo appropriati
                            if description and description != "Nessuna descrizione disponibile":
                                # Aggiungi a capo ogni 80 caratteri per una migliore leggibilità
                                description = self.format_description(description)
                            clone_of = result.get('cloneof', "N/A")
                            
                            # Estrai URL delle immagini direttamente dal JSON
                            url_image_ingame = result.get('url_image_ingame', "")
                            url_image_cabinet = result.get('url_image_cabinet', "")
                            url_image_title = result.get('url_image_title', "")
                            url_image_marquee = result.get('url_image_marquee', "")
                            url_image_border = result.get('url_image_border', "")
                            
                            print("🔗 URL immagini dal JSON:")
                            print(f"  - ingame: {url_image_ingame}")
                            print(f"  - cabinet: {url_image_cabinet}")
                            print(f"  - title: {url_image_title}")
                            print(f"  - marquee: {url_image_marquee}")
                            print(f"  - border: {url_image_border}")
                            
                            # Aggiorna le informazioni del gioco
                            self.game_info = {
                                'name': title,
                                'rom_name': rom_name,
                                'description': description,
                                'year': year,
                                'manufacturer': manufacturer,
                                'clone_of': clone_of,
                                'url_image_ingame': url_image_ingame,
                                'url_image_cabinet': url_image_cabinet,
                                'url_image_title': url_image_title,
                                'url_image_marquee': url_image_marquee,
                                'url_image_border': url_image_border
                            }
                            
                            print("✅ Dati JSON caricati correttamente")
                        else:
                            print("⚠️ Nessun risultato trovato nell'API")
                    else:
                        print(f"⚠️ Errore API: HTTP {response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    print("⚠️ Errore di connessione durante il recupero delle informazioni")
                except requests.exceptions.Timeout:
                    print("⚠️ Timeout durante il recupero delle informazioni")
                except Exception as e:
                    print(f"⚠️ Errore nel recupero delle informazioni: {e}")
                
                # Prepara le righe della descrizione per lo scroll
                # Calcola la larghezza della sezione info dinamicamente
                screen_info = self.get_screen_info()
                screen_width = screen_info['width']
                section_width = (screen_width - 40) // 3  # Larghezza sezione info
                max_chars = self.get_description_max_chars(section_width)
                self.description_lines = self.wrap_text(self.game_info['description'], max_chars)
                self.description_scroll = 0  # Reset scroll
                
                # Carica le immagini
                self.load_game_images(rom_name)
                
                print("✅ Informazioni gioco caricate")
            else:
                print("⚠️ Formato gioco non valido")
    
    def clean_url(self, url):
        """Rimuove il protocollo dall'URL se presente"""
        if not url:
            return url
        # Rimuove http:// o https:// dall'inizio dell'URL
        if url.startswith('http://'):
            return url[7:]  # Rimuove 'http://'
        elif url.startswith('https://'):
            return url[8:]  # Rimuove 'https://'
        return url

    def get_max_visible_description_lines(self):
        """Calcola dinamicamente il numero massimo di righe visibili per la descrizione"""
        screen_info = self.get_screen_info()
        screen_height = screen_info['height']
        section_height = screen_height - 220  # Altezza sezione info - aggiornata per footer di 100px
        
        # Calcola l'altezza disponibile per la descrizione
        # Assumiamo che le informazioni base occupino circa 200px
        available_height = section_height - 200 - 40  # 40px di margine
        line_height = 20
        max_visible_lines = max(1, available_height // line_height)
        
        return max_visible_lines

    def get_description_max_chars(self, section_width):
        """Calcola dinamicamente il numero massimo di caratteri per riga della descrizione"""
        available_width = section_width - 30  # Margini sinistro e destro aumentati per sicurezza
        max_chars = available_width // 8  # Ridotto da 6 a 8 per evitare che il testo esca dallo schermo
        return max_chars

    def load_game_images(self, rom_name):
        """Carica le immagini del gioco dal server o usa placeholder se non disponibili"""
        try:
            print(f"🖼️ Caricamento immagini per: {rom_name}")
            
            # Inizializza senza placeholder colorati - mostreremo "IMAGE PREVIEW"
            self.game_images = {
                'titolo': None,   # Nessun placeholder colorato
                'ingame': None    # Nessun placeholder colorato
            }
            
            # Cartella cache dinamica basata sulla piattaforma
            if hasattr(self, 'platform_paths') and self.platform_paths['cache_path']:
                cache_folder = self.platform_paths['cache_path']
            else:
                cache_folder = os.path.join(os.getcwd(), "cache")
            
            # Crea la cartella cache se non esiste
            os.makedirs(cache_folder, exist_ok=True)
            
            # URL dinamici basati sulla piattaforma
            if hasattr(self, 'platform_paths'):
                image_types = {
                    'titolo': self.platform_paths['title_url'].replace('{rom_name}', rom_name),
                    'ingame': self.platform_paths['ingame_url'].replace('{rom_name}', rom_name)
                }
            else:
                # Fallback agli URL originali
                image_types = {
                    'titolo': f"adb.arcadeitalia.net/?mame={rom_name}&type=title&resize=0",
                    'ingame': f"adb.arcadeitalia.net/?mame={rom_name}&type=ingame&resize=0"
                }
            
            print("🔗 URL immagini:")
            for img_type, url in image_types.items():
                print(f"  - {img_type}: {url}")
            
            # Cartelle locali nella cache del progetto - solo titolo e ingame
            local_folders = {
                'titolo': os.path.join(cache_folder, rom_name, "titolo"),
                'ingame': os.path.join(cache_folder, rom_name, "ingame")
            }
            
            # Scarica e carica ogni tipo di immagine
            for img_type, url in image_types.items():
                try:
                    # Crea la cartella di destinazione se non esiste
                    local_folder = local_folders[img_type]
                    os.makedirs(local_folder, exist_ok=True)
                    
                    # Percorso file locale
                    local_file = os.path.join(local_folder, f"{rom_name}.png")
                    
                    # Controlla se il file esiste già localmente
                    if os.path.exists(local_file):
                        print(f"✅ Immagine {img_type} trovata localmente")
                        print(f"   📁 Percorso: {local_file}")
                        file_size = os.path.getsize(local_file)
                        print(f"   📏 Dimensione file: {file_size} bytes")
                        try:
                            # Carica l'immagine con Pygame
                            # Verifica il formato dell'immagine
                            with open(local_file, "rb") as f:
                                header = f.read(8)
                                # Verifica se è un file PNG valido (inizia con 89 50 4E 47 0D 0A 1A 0A)
                                if header.startswith(b'\x89PNG\r\n\x1a\n'):
                                    image = pygame.image.load(local_file)
                                else:
                                    print(f"⚠️ Formato immagine non valido per {img_type}")
                                    raise ValueError("Formato immagine non valido")
                            
                            # Mantieni l'immagine originale per una migliore qualità
                            # Non ridimensioniamo qui, lo faremo durante la visualizzazione
                            print(f"   📐 Dimensioni originali: {image.get_width()}x{image.get_height()}")
                            
                            # Salva l'immagine originale senza ridimensionamento
                            final_surface = image.copy()
                            
                            # Aggiorna il dizionario delle immagini
                            self.game_images[img_type] = final_surface
                            continue  # Passa alla prossima immagine
                        except Exception as e:
                            print(f"⚠️ Errore nel caricamento locale di {img_type}: {e}")
                    
                    # Se non esiste localmente, prova a scaricarla
                    print(f"🔄 Download immagine {img_type}...")
                    print(f"   📡 URL: {url}")
                    print(f"   💾 Destinazione: {local_file}")
                    print(f"   📁 Cartella: {local_folder}")
                    
                    # Aggiunge il protocollo per la richiesta HTTP
                    http_url = f"http://{url}" if not url.startswith(('http://', 'https://')) else url
                    print(f"   🌐 URL completo: {http_url}")
                    
                    response = requests.get(http_url, timeout=5)
                    print(f"   📊 Status Code: {response.status_code}")
                    print(f"   📏 Dimensione: {len(response.content)} bytes")
                    
                    # Verifica se la richiesta è andata a buon fine
                    if response.status_code == 200:
                        # Salva l'immagine localmente
                        print(f"   💾 Salvando in: {local_file}")
                        with open(local_file, "wb") as f:
                            f.write(response.content)
                        print(f"   ✅ File salvato con successo")
                        
                        try:
                            # Carica l'immagine con Pygame
                            print(f"   🖼️ Caricando immagine con Pygame...")
                            # Verifica il formato dell'immagine
                            with open(local_file, "rb") as f:
                                header = f.read(8)
                                # Verifica se è un file PNG valido (inizia con 89 50 4E 47 0D 0A 1A 0A)
                                if header.startswith(b'\x89PNG\r\n\x1a\n'):
                                    image = pygame.image.load(local_file)
                                    print(f"   ✅ PNG valido caricato")
                                else:
                                    print(f"⚠️ Formato immagine non valido per {img_type}")
                                    raise ValueError("Formato immagine non valido")
                            
                            # Mantieni l'immagine originale per una migliore qualità
                            # Non ridimensioniamo qui, lo faremo durante la visualizzazione
                            print(f"   📐 Dimensioni originali: {image.get_width()}x{image.get_height()}")
                            
                            # Salva l'immagine originale senza ridimensionamento
                            final_surface = image.copy()
                            
                            # Aggiorna il dizionario delle immagini
                            self.game_images[img_type] = final_surface
                            print(f"✅ Immagine {img_type} caricata")
                        except Exception as e:
                            print(f"⚠️ Errore nel caricamento di {img_type}: {e}")
                    else:
                        print(f"⚠️ Impossibile scaricare {img_type}: HTTP {response.status_code}")
                
                except requests.exceptions.ConnectionError:
                    print(f"⚠️ Errore di connessione per {img_type}")
                    # Mantieni il placeholder per questo tipo di immagine
                    # self.game_images[img_type] è già inizializzato con un placeholder
                except requests.exceptions.Timeout:
                    print(f"⚠️ Timeout per {img_type}")
                    # Mantieni il placeholder per questo tipo di immagine
                    # self.game_images[img_type] è già inizializzato con un placeholder
                except Exception as e:
                    print(f"⚠️ Errore generico per {img_type}: {e}")
                    # Mantieni il placeholder per questo tipo di immagine
                    # self.game_images[img_type] è già inizializzato con un placeholder
            
            print("✅ Processo di caricamento immagini completato")
            
        except Exception as e:
            print(f"❌ Errore caricamento immagini: {e}")
    
    def create_placeholder_image(self, size, color):
        """Crea un'immagine placeholder colorata di alta qualità"""
        try:
            # Crea una superficie più grande per migliore qualità
            surface = pygame.Surface(size, pygame.SRCALPHA)
            surface.fill(color)
            
            # Aggiungi un bordo più spesso
            pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 3)
            
            # Aggiungi testo per identificare il tipo con font più grande
            font_size = min(size[0] // 8, size[1] // 6, 32)
            font = pygame.font.Font(None, font_size)
            text = font.render("IMMAGINE", True, (255, 255, 255))
            text_rect = text.get_rect(center=surface.get_rect().center)
            surface.blit(text, text_rect)
            
            return surface
        except Exception as e:
            print(f"❌ Errore creazione placeholder: {e}")
            return None
    
    def wrap_text(self, text, max_chars):
        """Avvolge il testo in righe di lunghezza massima, preservando i veri a capo"""
        if not text:
            return []
        
        # Dividi il testo in righe basandosi sui caratteri \n
        original_lines = text.split('\n')
        wrapped_lines = []
        
        for line in original_lines:
            if not line.strip():
                # Riga vuota - mantienila come separatore
                wrapped_lines.append("")
                continue
            
            # Se la riga è già più corta del limite, mantienila così
            if len(line) <= max_chars:
                wrapped_lines.append(line)
                continue
            
            # Altrimenti, avvolgi la riga
            words = line.split()
            current_line = ""
            
            for word in words:
                if len(current_line + " " + word) <= max_chars:
                    if current_line:
                        current_line += " " + word
                    else:
                        current_line = word
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            
            if current_line:
                wrapped_lines.append(current_line)
        
        return wrapped_lines
    
    def format_description(self, description):
        """Formatta la descrizione preservando i veri a capo e migliorando la leggibilità"""
        if not description:
            return "Nessuna descrizione disponibile"
        
        # Normalizza i caratteri di a capo (Windows, Mac, Unix)
        description = description.replace('\r\n', '\n').replace('\r', '\n')
        
        # Dividi in paragrafi basandosi sui doppi a capo
        paragraphs = description.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                continue
                
            # Pulisci spazi multipli all'interno del paragrafo ma mantieni i singoli a capo
            lines = paragraph.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Normalizza spazi multipli in una singola riga
                cleaned_line = ' '.join(line.split())
                if cleaned_line.strip():  # Solo se la riga non è vuota
                    cleaned_lines.append(cleaned_line)
            
            if cleaned_lines:
                # Unisci le righe del paragrafo con a capo singoli
                formatted_paragraph = '\n'.join(cleaned_lines)
                formatted_paragraphs.append(formatted_paragraph)
        
        # Unisci i paragrafi con doppi a capo per creare spaziatura
        return '\n\n'.join(formatted_paragraphs)
    
    def toggle_edit_mode(self):
        """Attiva/disattiva modalità di scrittura"""
        if self.current_section_index == 1:  # Solo nel campo ricerca
            self.edit_mode = not self.edit_mode
            if self.edit_mode:
                print("📝 Modalità scrittura attivata")
            else:
                print("📝 Modalità scrittura disattivata")
    
    def execute_button_action(self):
        """Esegue azione del pulsante selezionato"""
        button_names = [
            "SALVA CABINET",
            "SALVA TITOLO", 
            "SALVA INGAME",
            "SALVA PLANCIA",
            "SALVA BORDER"
        ]
        
        if 0 <= self.selected_button < len(button_names):
            print(f"🔘 Eseguito: {button_names[self.selected_button]}")
            # Qui implementeresti le azioni specifiche dei pulsanti
    
    def toggle_fullscreen(self):
        """Attiva/disattiva fullscreen - mantiene sempre la risoluzione nativa"""
        try:
            # Ottieni le informazioni attuali
            current_flags = self.screen.get_flags()
            is_fullscreen = current_flags & pygame.FULLSCREEN
            
            if is_fullscreen:
                # Torna a finestra - usa la risoluzione nativa
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                print(f"🖥️ Passato a modalità finestra: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
            else:
                # Vai in fullscreen - usa la risoluzione nativa
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
                print(f"🖥️ Passato a modalità fullscreen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
            
            # Le dimensioni rimangono sempre le stesse
            print(f"📐 Risoluzione: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
            
        except Exception as e:
            print(f"❌ Errore fullscreen: {e}")
            # Ripristina modalità finestra in caso di errore
            try:
                self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                print("🔄 Ripristinato modalità finestra")
            except:
                pass
    
    def get_screen_info(self):
        """Ottiene informazioni sullo schermo - sempre risoluzione nativa"""
        try:
            return {
                'width': SCREEN_WIDTH,
                'height': SCREEN_HEIGHT,
                'fullscreen': pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
            }
        except Exception as e:
            print(f"❌ Errore info schermo: {e}")
            return {'width': SCREEN_WIDTH, 'height': SCREEN_HEIGHT, 'fullscreen': False}
    
    def draw(self):
        """Disegna l'interfaccia"""
        # Disegna lo sfondo se disponibile
        if self.background_image:
            self.screen.blit(self.background_image, (0, 0))
            # Aggiungi un overlay semi-trasparente per migliorare la leggibilità
            if self.background_overlay_alpha > 0:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(self.background_overlay_alpha)
                overlay.fill(self.colors['background'])
                self.screen.blit(overlay, (0, 0))
        else:
            # Fallback al colore di sfondo se l'immagine non è disponibile
            self.screen.fill(self.colors['background'])
        
        if self.current_screen == 'menu':
            # Disegna il menu delle piattaforme
            self.platform_menu.draw(self.screen, self.last_input_message, self.last_input_timer, self.input_debug_duration)
            # Aggiungi footer dinamico per il menu
            context_info = [
                "[MENU] Selezione Piattaforma",
                f"[JOY] {self.joystick_manager.joystick_name if self.joystick_manager.joystick_detected else 'Non rilevato'}"
            ]
            self.draw_dynamic_footer(SCREEN_WIDTH, SCREEN_HEIGHT, context_info)
        elif self.current_screen == 'config':
            # Disegna la schermata configurazione
            self.config_ui.draw(self.screen)
            # Aggiungi footer dinamico per la configurazione
            context_info = [
                "[CONFIG] Configurazione Pulsanti Joystick",
                f"[JOY] {self.joystick_manager.joystick_name if self.joystick_manager.joystick_detected else 'Non rilevato'}"
            ]
            self.draw_dynamic_footer(SCREEN_WIDTH, SCREEN_HEIGHT, context_info)
        else:
            # Disegna la schermata principale
            self.draw_main_screen()
            # Aggiungi footer dinamico per la schermata principale
            platform_name = self.selected_platform['name'] if self.selected_platform else 'Nessuna piattaforma'
            context_info = [
                f"[GAME] {platform_name}",
                f"[JOY] {self.joystick_manager.joystick_name if self.joystick_manager.joystick_detected else 'Non rilevato'}"
            ]
            self.draw_dynamic_footer(SCREEN_WIDTH, SCREEN_HEIGHT, context_info)
        
        # Aggiorna display
        pygame.display.flip()
    
    def draw_main_screen(self):
        """Disegna la schermata principale"""
        # Lo sfondo è già disegnato nel metodo draw principale
        
        # Ottieni le dimensioni dello schermo
        screen_info = self.get_screen_info()
        screen_width = screen_info['width']
        screen_height = screen_info['height']
        
        # Calcola le dimensioni e posizioni delle sezioni con margini
        section_width = (screen_width - 40) // 3  # Dividi lo schermo in 3 sezioni con margini
        
        # Posizioni delle sezioni
        left_section_x = 10
        center_section_x = left_section_x + section_width + 10
        right_section_x = center_section_x + section_width + 10
        
        section_y = 100
        section_height = screen_height - 220  # Ridotto ulteriormente da 180 a 220 per evitare sovrapposizione con footer
        
        # Disegna sezioni
        self.draw_games_list(left_section_x, section_y, section_width, section_height)
        self.draw_central_images(center_section_x, section_y, section_width, section_height)
        self.draw_info_section(right_section_x, section_y, section_width, section_height)
        # Rimuoviamo draw_status_bar() - ora usiamo il footer dinamico
        
        # Mostra messaggio di rilevamento joystick se attivo
        if self.joystick_detection_message and (time.time() - self.joystick_detection_timer) < self.joystick_detection_duration:
            # Sfondo semi-trasparente
            message_surface = self.font_large.render(self.joystick_detection_message, True, self.colors['accent'])
            message_rect = message_surface.get_rect(center=(screen_width//2, screen_height//2))
            
            # Sfondo con bordo
            bg_rect = message_rect.inflate(60, 30)
            bg_surface = pygame.Surface(bg_rect.size)
            bg_surface.set_alpha(220)
            bg_surface.fill(self.colors['surface'])
            self.screen.blit(bg_surface, bg_rect)
            
            # Bordo colorato
            pygame.draw.rect(self.screen, self.colors['accent'], bg_rect, 3)
            
            # Messaggio
            self.screen.blit(message_surface, message_rect)
        
        # Mostra messaggio di conferma download ROM se attivo
        if self.download_confirmation_active and self.download_info:
            self.draw_download_confirmation(screen_width, screen_height)
    
    def draw_download_confirmation(self, screen_width, screen_height):
        """Disegna il messaggio di conferma download ROM"""
        # Sfondo semi-trasparente scuro
        overlay = pygame.Surface((screen_width, screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Box di conferma
        box_width = 800
        box_height = 490  # Aumentato per contenere URL e stato della cartella
        box_x = (screen_width - box_width) // 2
        box_y = (screen_height - box_height) // 2
        
        # Sfondo box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(self.screen, self.colors['surface'], box_rect)
        pygame.draw.rect(self.screen, self.colors['accent'], box_rect, 4)
        
        # Titolo - cambia in base allo stato
        if self.download_state == 'downloading':
            title_text = self.font_large.render("DOWNLOAD IN CORSO...", True, self.colors['accent'])
        elif self.download_state == 'success':
            title_text = self.font_large.render("DOWNLOAD COMPLETATO", True, (100, 255, 100))
        elif self.download_state == 'error':
            title_text = self.font_large.render("DOWNLOAD FALLITO", True, (255, 100, 100))
        else:
            title_text = self.font_large.render("CONFERMA DOWNLOAD ROM", True, self.colors['accent'])
        
        title_rect = title_text.get_rect(center=(screen_width//2, box_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Informazioni download
        y_offset = box_y + 100
        
        # Nome gioco
        game_text = self.font_medium.render(f"Gioco: {self.download_info['full_game_name']}", True, self.colors['text'])
        self.screen.blit(game_text, (box_x + 20, y_offset))
        y_offset += 40
        
        # Nome ROM
        rom_text = self.font_medium.render(f"ROM: {self.download_info['rom_name']}.zip", True, self.colors['text'])
        self.screen.blit(rom_text, (box_x + 20, y_offset))
        y_offset += 40
        
        # Percorso destinazione
        path_text = self.font_medium.render(f"Destinazione: {self.download_info['full_rom_path']}", True, self.colors['text'])
        self.screen.blit(path_text, (box_x + 20, y_offset))
        y_offset += 40
        
        # URL download (mostra tutte le opzioni)
        urls = self.download_info.get('rom_download_urls', [])
        extensions = self.download_info.get('rom_extensions', [])
        url_text = self.font_medium.render(f"URL da provare ({len(urls)} opzioni):", True, self.colors['text'])
        self.screen.blit(url_text, (box_x + 20, y_offset))
        y_offset += 30
        
        for i, (url, ext) in enumerate(zip(urls, extensions)):
            url_line = self.font_small.render(f"  {i+1}. {ext.upper()}: {url}", True, self.colors['text_secondary'])
            self.screen.blit(url_line, (box_x + 20, y_offset))
            y_offset += 25
        
        # Stato cartella destinazione
        folder_exists = self.download_info.get('folder_exists', False)
        if folder_exists:
            folder_status = "✅ Cartella destinazione: PRESENTE"
            folder_color = self.colors['accent']
        else:
            folder_status = "❌ Cartella destinazione: NON PRESENTE"
            folder_color = (255, 100, 100)  # Rosso per errore
        
        folder_text = self.font_medium.render(folder_status, True, folder_color)
        self.screen.blit(folder_text, (box_x + 20, y_offset))
        y_offset += 60
        
        # Istruzioni - cambiano in base allo stato del download
        if self.download_state == 'downloading':
            instructions = self.font_medium.render("Attendere...", True, self.colors['accent2'])
        elif self.download_state in ['success', 'error']:
            # Mostra il messaggio di risultato
            msg = self.font_medium.render(self.download_result_message, True, self.colors['text'])
            self.screen.blit(msg, (box_x + 20, y_offset))
            y_offset += 50
            instructions = self.font_medium.render("Premi un tasto per chiudere", True, self.colors['accent2'])
        else:
            # Istruzioni normali conferma/annulla
            if folder_exists:
                instructions = self.font_medium.render("SPACE/Pulsante 1: Conferma | ESC/Pulsante 2: Annulla", True, self.colors['accent2'])
            else:
                instructions = self.font_medium.render("ESC/Pulsante 2: Annulla (Download non disponibile)", True, (255, 150, 150))
        
        instructions_rect = instructions.get_rect(center=(screen_width//2, y_offset))
        self.screen.blit(instructions, instructions_rect)
    
    def draw_games_list(self, x, y, width, height):
        """Disegna la lista dei giochi"""
        # Bordo sezione - sempre grigio dato che non si naviga più tra sezioni
        border_color = self.colors['surface']
        pygame.draw.rect(self.screen, border_color, (x-5, y-5, width+10, height+10), 3)
        
        # Titolo
        title_text = self.font_medium.render("LISTA GIOCHI", True, self.colors['text'])
        self.screen.blit(title_text, (x, y-40))
        
        # Indicatore di posizione
        total_games = len(self.games_list)
        position_text = f"{self.current_game_index+1}/{total_games}"
        pos_surface = self.font_small.render(position_text, True, self.colors['accent'])
        self.screen.blit(pos_surface, (x+width-80, y-40))
        
        # Barra di scorrimento
        scrollbar_height = max(20, height * (20 / total_games))
        scrollbar_pos = y + (height * (self.current_game_index / total_games))
        pygame.draw.rect(self.screen, self.colors['surface'], (x+width+5, y, 10, height))
        pygame.draw.rect(self.screen, self.colors['accent'], (x+width+5, scrollbar_pos, 10, scrollbar_height))
        
        # Lista giochi - mostra più giochi in base all'altezza disponibile
        # Calcola dinamicamente l'altezza degli elementi basata sulla dimensione del font
        font_height = self.font_medium.get_height()
        item_height = max(30, font_height + 8)  # Altezza font + 8px di padding
        visible_items = height // item_height  # Numero di elementi visibili
        half_visible = visible_items // 2
        
        start_index = max(0, self.current_game_index - half_visible)
        end_index = min(len(self.games_list), start_index + visible_items)
        
        for i, game in enumerate(self.games_list[start_index:end_index]):
            game_index = start_index + i
            game_y = y + (i * item_height)
            
            # Colore elemento
            if game_index == self.current_game_index:
                color = self.colors['selected']
                pygame.draw.rect(self.screen, color, (x, game_y-2, width, item_height-2), 2)
            else:
                color = self.colors['text']
            
            # Testo gioco - tronca se troppo lungo e centra verticalmente
            game_text = self.font_medium.render(game[:width//8], True, color)  # Limita il testo in base alla larghezza
            # Centra il testo verticalmente nell'elemento
            text_y = game_y + (item_height - game_text.get_height()) // 2
            self.screen.blit(game_text, (x+5, text_y))
            
        # Indicatore di scrolling veloce
        if hasattr(self.joystick_manager, 'dpad_pressed'):
            if self.joystick_manager.dpad_pressed['up'] or self.joystick_manager.dpad_pressed['down']:
                # Calcola il tempo di pressione
                direction = 'up' if self.joystick_manager.dpad_pressed['up'] else 'down'
                elapsed = time.time() - self.joystick_manager.dpad_press_time[direction]
                
                if elapsed > 0.5:  # Mostra solo dopo il delay iniziale
                    # Determina la velocità
                    if elapsed > 3.0:
                        speed_text = "VELOCITÀ: ●●●●●"
                    elif elapsed > 2.0:
                        speed_text = "VELOCITÀ: ●●●●○"
                    elif elapsed > 1.0:
                        speed_text = "VELOCITÀ: ●●●○○"
                    else:
                        speed_text = "VELOCITÀ: ●●○○○"
                    
                    # Mostra l'indicatore
                    speed_surface = self.font_small.render(speed_text, True, self.colors['accent'])
                    self.screen.blit(speed_surface, (x, y+height+15))
                    
        # Nessuna istruzione qui per evitare sovrapposizioni
    
    
    
    
    def draw_info_section(self, x, y, width, height):
        """Disegna la sezione informazioni gioco"""
        # Bordo sezione - sempre grigio dato che non si naviga più tra sezioni
        border_color = self.colors['surface']
        pygame.draw.rect(self.screen, border_color, (x-5, y-5, width+10, height+10), 3)
        
        # Titolo
        title_text = self.font_medium.render("INFORMAZIONI GIOCO", True, self.colors['text'])
        self.screen.blit(title_text, (x, y-40))
        
        # Area informazioni - rimuoviamo lo sfondo grigio carico
        # info_rect = pygame.Rect(x, y, width, height)
        # pygame.draw.rect(self.screen, self.colors['surface'], info_rect)
        
        # Informazioni gioco con migliore spaziatura
        if self.game_info['name']:
            current_y = y + 20
            line_height = 25  # Spaziatura tra le righe
            
            # Nome gioco
            name_text = self.font_small.render(f"Nome: {self.game_info['name']}", True, self.colors['text'])
            self.screen.blit(name_text, (x+10, current_y))
            current_y += line_height
            
            # ROM name
            rom_text = self.font_small.render(f"ROM: {self.game_info['rom_name']}", True, self.colors['text'])
            self.screen.blit(rom_text, (x+10, current_y))
            current_y += line_height
            
            # Anno
            year_text = self.font_small.render(f"Anno: {self.game_info['year']}", True, self.colors['text'])
            self.screen.blit(year_text, (x+10, current_y))
            current_y += line_height
            
            # Produttore
            manuf_text = self.font_small.render(f"Produttore: {self.game_info['manufacturer']}", True, self.colors['text'])
            self.screen.blit(manuf_text, (x+10, current_y))
            current_y += line_height
            
            # Clone of (se presente)
            if 'clone_of' in self.game_info and self.game_info['clone_of'] != "N/A":
                clone_text = self.font_small.render(f"Clone di: {self.game_info['clone_of']}", True, self.colors['text'])
                self.screen.blit(clone_text, (x+10, current_y))
                current_y += line_height
            
            # Descrizione con scroll
            if self.description_lines:
                # Titolo descrizione con spaziatura
                current_y += 10  # Spazio extra prima della descrizione
                desc_title = self.font_small.render("Descrizione:", True, self.colors['text'])
                self.screen.blit(desc_title, (x+10, current_y))
                current_y += line_height
                
                # Calcola dinamicamente quante righe possono essere visualizzate
                desc_start_y = current_y
                available_height = height - (desc_start_y - y) - 40  # 40px di margine per l'indicatore
                desc_line_height = 20
                max_visible_lines = max(1, available_height // desc_line_height)
                
                # Mostra le righe visibili basate sullo scroll
                start_line = self.description_scroll
                end_line = min(start_line + max_visible_lines, len(self.description_lines))
                
                # Righe descrizione - adatta in base alla larghezza disponibile
                max_chars = self.get_description_max_chars(width)
                
                # Rigenera le righe di descrizione se necessario
                if hasattr(self, 'last_width') and self.last_width != width:
                    self.description_lines = self.wrap_text(self.game_info['description'], max_chars)
                
                self.last_width = width
                
                for i, line in enumerate(self.description_lines[start_line:end_line]):
                    if line.strip():  # Solo se la riga non è vuota
                        desc_text = self.font_small.render(line, True, self.colors['text'])
                        self.screen.blit(desc_text, (x+10, desc_start_y + (i * desc_line_height)))
                    # Le righe vuote vengono saltate, creando spaziatura tra i paragrafi
                
                # Mostra indicatore di scroll se necessario
                if len(self.description_lines) > max_visible_lines:
                    scroll_indicator = f"📜 {self.description_scroll + 1}-{end_line} di {len(self.description_lines)}"
                    indicator_text = self.font_small.render(scroll_indicator, True, self.colors['accent'])
                    indicator_y = desc_start_y + (max_visible_lines * line_height) + 5
                    self.screen.blit(indicator_text, (x+10, indicator_y))
                    
                    # Rimuoviamo le istruzioni di navigazione duplicate (sono già nel footer)
        else:
            # Placeholder
            placeholder_text = "Seleziona un gioco e premi X o INVIO"
            placeholder_surface = self.font_small.render(placeholder_text, True, self.colors['text_secondary'])
            self.screen.blit(placeholder_surface, (x+10, y+20))
    
    
    def draw_central_images(self, x, y, width, height):
        """Disegna la sezione centrale con marquee e immagine gioco"""
        # Bordo sezione - sempre grigio dato che non si naviga più tra sezioni
        border_color = self.colors['surface']
        pygame.draw.rect(self.screen, border_color, (x-5, y-5, width+10, height+10), 3)
        
        # Titolo
        title_text = self.font_medium.render("IMMAGINI GIOCO", True, self.colors['text'])
        self.screen.blit(title_text, (x, y-40))
        
        # Calcola le dimensioni dei contenitori
        marquee_height = height // 3
        game_image_height = height - marquee_height - 20  # 20 pixel di spazio tra i contenitori
        
        # Contenitore per marquee - rimuoviamo lo sfondo grigio
        marquee_rect = pygame.Rect(x+10, y+10, width-20, marquee_height)
        # pygame.draw.rect(self.screen, self.colors['surface'], marquee_rect)
        
        # Rimuoviamo l'etichetta "TITOLO" per un aspetto più pulito
        # title_label = self.font_small.render("TITOLO", True, self.colors['text'])
        # self.screen.blit(title_label, (x+10, y-15))
        
        # Mostra titolo se disponibile
        if self.game_images['titolo'] is not None:
            # Calcola le dimensioni per adattare l'immagine mantenendo le proporzioni
            img = self.game_images['titolo']
            img_rect = img.get_rect()
            scale_factor = min((width-40) / img_rect.width, (marquee_height-20) / img_rect.height)
            new_width = int(img_rect.width * scale_factor)
            new_height = int(img_rect.height * scale_factor)
            
            # Ridimensiona l'immagine con qualità migliore
            # Assicurati che l'immagine abbia il formato corretto per smoothscale
            try:
                # Converti l'immagine al formato RGB o RGBA se necessario
                if img.get_flags() & pygame.SRCALPHA:
                    # Immagine con alpha channel
                    scaled_image = pygame.transform.smoothscale(img, (new_width, new_height))
                else:
                    # Immagine senza alpha, converti a RGB
                    rgb_img = img.convert()
                    scaled_image = pygame.transform.smoothscale(rgb_img, (new_width, new_height))
            except pygame.error:
                # Fallback a scale normale se smoothscale fallisce
                scaled_image = pygame.transform.scale(img, (new_width, new_height))
            
            # Posiziona l'immagine al centro del contenitore
            img_x = x + 10 + (width - 20 - new_width) // 2
            img_y = y + 10 + (marquee_height - new_height) // 2
            self.screen.blit(scaled_image, (img_x, img_y))
        else:
            # Mostra "IMAGE PREVIEW" quando non ci sono immagini
            preview_text = self.font_medium.render("IMAGE PREVIEW", True, self.colors['text_secondary'])
            text_rect = preview_text.get_rect(center=marquee_rect.center)
            self.screen.blit(preview_text, text_rect)
        
        # Contenitore per immagine gioco - rimuoviamo lo sfondo grigio
        game_image_rect = pygame.Rect(x+10, y+marquee_height+30, width-20, game_image_height)
        # pygame.draw.rect(self.screen, self.colors['surface'], game_image_rect)
        
        # Rimuoviamo l'etichetta "IMMAGINE GIOCO" per un aspetto più pulito
        # game_img_title = self.font_small.render("IMMAGINE GIOCO", True, self.colors['text'])
        # self.screen.blit(game_img_title, (x+10, y+marquee_height+10))
        
        # Mostra solo l'immagine ingame
        img = None
        img_type = ""
        
        if self.game_images['ingame'] is not None:
            img = self.game_images['ingame']
            img_type = "INGAME"
            
        # Se abbiamo un'immagine, mostriamola
        if img is not None:
            # Calcola le dimensioni per adattare l'immagine mantenendo le proporzioni
            img_rect = img.get_rect()
            scale_factor = min((width-40) / img_rect.width, (game_image_height-40) / img_rect.height)
            new_width = int(img_rect.width * scale_factor)
            new_height = int(img_rect.height * scale_factor)
            
            # Ridimensiona l'immagine con qualità migliore
            # Assicurati che l'immagine abbia il formato corretto per smoothscale
            try:
                # Converti l'immagine al formato RGB o RGBA se necessario
                if img.get_flags() & pygame.SRCALPHA:
                    # Immagine con alpha channel
                    scaled_image = pygame.transform.smoothscale(img, (new_width, new_height))
                else:
                    # Immagine senza alpha, converti a RGB
                    rgb_img = img.convert()
                    scaled_image = pygame.transform.smoothscale(rgb_img, (new_width, new_height))
            except pygame.error:
                # Fallback a scale normale se smoothscale fallisce
                scaled_image = pygame.transform.scale(img, (new_width, new_height))
            
            # Posiziona l'immagine al centro del contenitore
            img_x = x + 10 + (width - 20 - new_width) // 2
            img_y = y + marquee_height + 30 + (game_image_height - new_height) // 2
            self.screen.blit(scaled_image, (img_x, img_y))
            
            # Rimuoviamo l'etichetta del tipo di immagine per un aspetto più pulito
            # type_text = self.font_small.render(img_type, True, self.colors['accent'])
            # self.screen.blit(type_text, (x + width - 100, y + marquee_height + 10))
        else:
            # Mostra "IMAGE PREVIEW" quando non ci sono immagini
            preview_text = self.font_medium.render("IMAGE PREVIEW", True, self.colors['text_secondary'])
            text_rect = preview_text.get_rect(center=game_image_rect.center)
            self.screen.blit(preview_text, text_rect)
    
    def draw_status_bar(self):
        """Disegna la barra di stato"""
        # Ottieni le dimensioni attuali dello schermo
        screen_info = self.get_screen_info()
        screen_width = screen_info['width']
        screen_height = screen_info['height']
        
        # Posiziona la barra in basso - aumentata l'altezza da 50 a 80
        y = screen_height - 100
        
        # Sfondo barra - senza bordo
        pygame.draw.rect(self.screen, self.colors['surface'], (0, y, screen_width, 100))
        
        # Informazioni piattaforma e joystick - font ridotto per footer più pulito
        if self.selected_platform:
            platform_text = f"[PLAT] {self.selected_platform['name']}"
            platform_surface = self.font_small.render(platform_text, True, self.colors['accent2'])
            self.screen.blit(platform_surface, (20, y+5))
        
        if self.joystick_manager.joystick_detected:
            joy_text = f"[JOY] {self.joystick_manager.joystick_name}"
        else:
            joy_text = "[KEY] Solo tastiera"
        
        joy_surface = self.font_small.render(joy_text, True, self.colors['text'])  # Font ridotto per footer più pulito
        self.screen.blit(joy_surface, (20, y+30))
        
        # Informazioni sezione corrente - font grande
        # Informazioni applicazione
        # Nome applicazione rimosso per footer più pulito
        
        # Informazioni risoluzione e versione - font ancora più ridotto
        resolution_text = f"[SCR] {screen_width}x{screen_height}"
        resolution_surface = self.font_tiny.render(resolution_text, True, self.colors['text_secondary'])  # Font ancora più ridotto
        self.screen.blit(resolution_surface, (screen_width-250, y+5))
        
        # Versione programma - posizionata a destra
        version_text = f"[VER] {self.platform_manager.get_program_version()}"
        version_surface = self.font_tiny.render(version_text, True, self.colors['text_secondary'])
        self.screen.blit(version_surface, (screen_width-150, y+70))
        
        # Icone SVG al centro del footer (rimosso - ora usiamo footer dinamico)
        # self.draw_footer_icons(screen_width, y, 'main')
        
        # Debug input - a sinistra nel footer
        if self.last_input_message and time.time() - self.last_input_timer < self.input_debug_duration:
            debug_surface = self.font_small.render(self.last_input_message, True, self.colors['accent2'])
            debug_x = 20  # Posizione a sinistra
            debug_y = y + 70
            self.screen.blit(debug_surface, (debug_x, debug_y))
    
    def draw_dynamic_footer(self, screen_width, screen_height, context_info=None):
        """Disegna un footer dinamico per tutte le schermate"""
        footer_height = 100
        footer_y = screen_height - footer_height
        
        # Sfondo footer con trasparenza
        footer_surface = pygame.Surface((screen_width, footer_height))
        footer_surface.set_alpha(220)  # Trasparenza (0-255, 200 = circa 78% opaco)
        footer_surface.fill(self.colors['surface'])
        self.screen.blit(footer_surface, (0, footer_y))
        
        # Informazioni di contesto (sinistra)
        if context_info:
            y_offset = footer_y + 5
            for info in context_info:
                info_surface = self.font_medium.render(info, True, self.colors['accent2'])
                self.screen.blit(info_surface, (20, y_offset))
                y_offset += 25
        
        # Icone al centro (spostate a destra di una percentuale della larghezza schermo)
        # Calcola offset responsive: 5% della larghezza schermo (circa 100px su 1920px)
        responsive_offset = int(screen_width * 0.05)
        self.draw_footer_icons(screen_width, footer_y, self.current_screen, offset_x=responsive_offset)
        
        # Informazioni risoluzione e versione (destra)
        resolution_text = f"[SCR] {screen_width}x{screen_height}"
        resolution_surface = self.font_tiny.render(resolution_text, True, self.colors['text_secondary'])
        self.screen.blit(resolution_surface, (screen_width - 250, footer_y + 5))
        
        # Versione programma - posizionata a destra
        version_text = f"[VER] {self.platform_manager.get_program_version()}"
        version_surface = self.font_tiny.render(version_text, True, self.colors['text_secondary'])
        self.screen.blit(version_surface, (screen_width - 150, footer_y + 70))
        
        # Debug input (sinistra in basso)
        if hasattr(self, 'last_input_message') and self.last_input_message and time.time() - self.last_input_timer < self.input_debug_duration:
            debug_surface = self.font_small.render(self.last_input_message, True, self.colors['accent2'])
            self.screen.blit(debug_surface, (20, footer_y + 70))

    def draw_footer_icons(self, screen_width, footer_y, screen_type='main', offset_x=0):
        """Disegna le icone PNG nel footer"""
        if not self.footer_icons:
            return
        
        # Determina quali icone mostrare in base alla schermata
        if screen_type == 'menu':
            # Menu piattaforme: solo info, rom, start
            icon_order = ['info', 'rom', 'start']
        elif screen_type == 'config':
            # Schermata configurazione: info (conferma) e rom (indietro)
            icon_order = ['info', 'rom']
        else:
            # Schermata principale: tutte le icone incluso scroll
            icon_order = ['info', 'rom', 'download', 'scroll', 'start']
        
        # Calcola la posizione centrale per le icone (con offset)
        icon_spacing = 250  # Spazio tra le icone (aumentato per più spazio)
        total_width = len(icon_order) * icon_spacing
        start_x = (screen_width - total_width) // 2 + offset_x  # Applica l'offset
        
        # Posizione Y per le icone (centrate nel footer)
        icon_y = footer_y + 20
        x_offset = start_x
        
        for icon_type in icon_order:
            if icon_type in self.footer_icons:
                icon = self.footer_icons[icon_type]
                # Centra l'icona
                icon_x = x_offset - icon.get_width() // 2
                self.screen.blit(icon, (icon_x, icon_y))
                
                # Aggiungi etichetta testuale sotto l'icona
                if icon_type == 'info':
                    if screen_type == 'config':
                        label_text = "Conferma"
                        enter_text = "/Enter"
                        backspace_text = None
                        esc_text = None
                        space_text = None
                    else:
                        label_text = "Seleziona/Info"
                        enter_text = "/Enter"
                        backspace_text = None
                        esc_text = None
                        space_text = None
                elif icon_type == 'rom':
                    label_text = "Indietro"
                    enter_text = None
                    backspace_text = "/Backspace"
                    esc_text = None
                    space_text = None
                elif icon_type == 'download':
                    label_text = "Scarica Rom"
                    enter_text = None
                    backspace_text = None
                    esc_text = None
                    space_text = "/Space"
                elif icon_type == 'scroll':
                    label_text = "Scroll L1/R1"
                    enter_text = None
                    backspace_text = None
                    esc_text = None
                    space_text = None
                elif icon_type == 'start':
                    label_text = "Exit"
                    enter_text = None
                    backspace_text = None
                    esc_text = "/Esc"
                    space_text = None
                
                # Disegna etichetta principale sotto l'icona (centrata rispetto all'icona)
                label_surface = self.font_small.render(label_text, True, self.colors['text'])
                # Centra l'etichetta rispetto alla posizione dell'icona (non rispetto a x_offset)
                icon_center_x = x_offset  # x_offset è già la posizione centrale dell'icona
                label_x = icon_center_x - label_surface.get_width() // 2
                label_y = icon_y + icon.get_height() + 5
                self.screen.blit(label_surface, (label_x, label_y))
                
                # Disegna "/Enter" a destra del pulsante (solo per pulsante 1)
                if enter_text:
                    enter_surface = self.font_small.render(enter_text, True, self.colors['text_secondary'])
                    # Posiziona l'etichetta a destra del pulsante, centrata verticalmente
                    enter_x = icon_center_x + icon.get_width() // 2 + 10  # 10 pixel a destra del pulsante
                    enter_y = icon_y + icon.get_height() // 2 - enter_surface.get_height() // 2  # Centrato verticalmente
                    self.screen.blit(enter_surface, (enter_x, enter_y))
                
                # Disegna "/Backspace" a destra del pulsante (solo per pulsante 2)
                if backspace_text:
                    backspace_surface = self.font_small.render(backspace_text, True, self.colors['text_secondary'])
                    # Posiziona l'etichetta a destra del pulsante, centrata verticalmente
                    backspace_x = icon_center_x + icon.get_width() // 2 + 10  # 10 pixel a destra del pulsante
                    backspace_y = icon_y + icon.get_height() // 2 - backspace_surface.get_height() // 2  # Centrato verticalmente
                    self.screen.blit(backspace_surface, (backspace_x, backspace_y))
                
                # Disegna "/Esc" a destra del pulsante (solo per pulsante Start)
                if esc_text:
                    esc_surface = self.font_small.render(esc_text, True, self.colors['text_secondary'])
                    # Posiziona l'etichetta a destra del pulsante, centrata verticalmente
                    esc_x = icon_center_x + icon.get_width() // 2 + 10  # 10 pixel a destra del pulsante
                    esc_y = icon_y + icon.get_height() // 2 - esc_surface.get_height() // 2  # Centrato verticalmente
                    self.screen.blit(esc_surface, (esc_x, esc_y))
                
                # Disegna "/Space" a destra del pulsante (solo per pulsante 3)
                if space_text:
                    space_surface = self.font_small.render(space_text, True, self.colors['text_secondary'])
                    # Posiziona l'etichetta a destra del pulsante, centrata verticalmente
                    space_x = icon_center_x + icon.get_width() // 2 + 10  # 10 pixel a destra del pulsante
                    space_y = icon_y + icon.get_height() // 2 - space_surface.get_height() // 2  # Centrato verticalmente
                    self.screen.blit(space_surface, (space_x, space_y))
                
                x_offset += icon_spacing
    
    def run(self):
        """Loop principale dell'applicazione"""
        logger.info("LRscript - Retro Game Manager (Pygame)")
        
        if self.joystick_manager.joystick_detected:
            logger.info(f"JOYSTICK RILEVATO: {self.joystick_manager.joystick_name}")
        else:
            logger.info("Solo controlli tastiera disponibili")
        # Controlli disponibili (non mostrati nel terminale per pulizia)
        
        running = True
        while running:
            events = pygame.event.get()
            running = self.handle_input(events)
            
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Funzione principale"""
    try:
        app = ArcadeUI()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Applicazione chiusa dall'utente")
    except Exception as e:
        print(f"❌ Errore: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
