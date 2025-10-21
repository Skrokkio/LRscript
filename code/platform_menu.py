# -*- coding: utf-8 -*-

"""
LRscript - Platform Menu
========================
Menu di selezione piattaforme con sistema di personalizzazione immagini.
"""

import os
import time
import pygame
import logging
from .constants import CUSTOM_FONT_PATH, FONT_SIZE_LARGE, FONT_SIZE_MEDIUM, FONT_SIZE_SMALL, FONT_SIZE_TINY

logger = logging.getLogger('LRscript')

class PlatformMenu:
    """Menu di selezione piattaforme con quadrati"""
    
    def __init__(self, platform_manager, screen_width, screen_height, colors):
        self.platform_manager = platform_manager
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.colors = colors

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
        
        # Stato menu - layout verticale con scrollbar
        self.selected_platform = 0
        self.scroll_offset = 0  # Offset per lo scroll verticale
        
        # Aggiungi quadrato configurazione in cima
        self.config_button = {
            'name': 'CONFIGURA JOYSTICK',
            'special': True  # Per distinguerlo dalle piattaforme
        }
        
        # Calcola dimensioni adattabili alla risoluzione
        scale_factor = screen_width / 1920.0
        self.platform_width = max(int(300 * scale_factor), 200)    # Larghezza rettangolo piattaforma (DIMEZZATA)
        
        # Calcola l'altezza basata sulla dimensione del font (RADDOPPIATA per pulsanti più belli)
        font_height = self.font_medium.get_height()
        self.platform_height = max(int(160 * scale_factor), font_height + 40)  # Altezza raddoppiata per pulsanti più belli
        
        self.platform_spacing = max(int(15 * scale_factor), 10)    # Spazio tra rettangoli
        
        # Carica il logo dell'applicazione
        self.logo_image = self.load_logo()
        
        # Carica l'icona per il pulsante configurazione
        self.config_icon = self.load_config_icon()
        
        # Carica le icone PNG per il footer
        self.footer_icons = self.load_footer_icons()
        
        # Calcola posizioni
        self.calculate_positions()
        
        # Sistema per personalizzazione immagini
        self.button_hold_time = 0.8  # Tempo per tenere premuto (secondi)
        self.confirm_press_time = 0  # Timestamp quando è stato premuto confirm
        self.confirm_held = False    # Flag se confirm è tenuto premuto
        self.show_image_menu = False # Flag per mostrare menu immagini
        self.selected_image_index = 0 # Indice immagine selezionata nel menu
        self.available_images = []   # Lista immagini disponibili
        
        # Carica le immagini disponibili
        self.load_available_images()
    
    def load_available_images(self):
        """Carica le immagini disponibili dalla cartella resources/logos"""
        self.available_images = []
        logos_path = "./resources/logos"
        
        # Crea la cartella se non esiste
        if not os.path.exists(logos_path):
            os.makedirs(logos_path)
            logger.info(f"Creata cartella logos: {logos_path}")
        
        # Carica tutte le immagini PNG dalla cartella
        try:
            for filename in os.listdir(logos_path):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_path = os.path.join(logos_path, filename)
                    try:
                        # Prova a caricare l'immagine per verificare che sia valida
                        test_image = pygame.image.load(image_path)
                        self.available_images.append({
                            'filename': filename,
                            'path': image_path,
                            'image': test_image
                        })
                        logger.debug(f"Immagine caricata: {filename}")
                    except Exception as e:
                        logger.warning(f"Errore caricamento immagine {filename}: {e}")
            
            logger.info(f"Caricate {len(self.available_images)} immagini da {logos_path}")
        except Exception as e:
            logger.error(f"Errore caricamento cartella logos: {e}")
    
    def calculate_positions(self):
        """Calcola le posizioni dei rettangoli delle piattaforme"""
        platform_count = self.platform_manager.get_platform_count()
        
        # Calcola area disponibile (centrata, con margini per titolo e footbar)
        available_width = self.screen_width - 100  # Margini laterali
        available_height = self.screen_height - 200  # 100px footbar + 100px per titolo e margini
        
        # Centra l'area
        self.start_x = (self.screen_width - available_width) // 2
        self.start_y = 150  # Inizia dopo il titolo
        
        # Calcola altezza totale necessaria
        total_items = platform_count + 1  # +1 per il pulsante configurazione
        self.total_height = total_items * (self.platform_height + self.platform_spacing)
        
        # Se l'altezza totale è maggiore dell'area disponibile, abilita lo scroll
        if self.total_height > available_height:
            self.scroll_enabled = True
        else:
            self.scroll_enabled = False
            self.scroll_offset = 0
    
    def load_logo(self):
        """Carica il logo dell'applicazione"""
        logo_path = "./resources/LRscript.png"
        if os.path.exists(logo_path):
            try:
                logo = pygame.image.load(logo_path)
                # Ridimensiona il logo per adattarlo alla risoluzione
                scale_factor = self.screen_width / 1920.0
                new_width = int(logo.get_width() * scale_factor)
                new_height = int(logo.get_height() * scale_factor)
                scaled_logo = pygame.transform.scale(logo, (new_width, new_height))
                logger.info(f"Logo caricato: {logo_path} -> {new_width}x{new_height}")
                return scaled_logo
            except Exception as e:
                logger.warning(f"Errore caricamento logo: {e}")
        else:
            logger.warning(f"File logo non trovato: {logo_path}")
        return None
    
    def load_config_icon(self):
        """Carica l'icona per il pulsante configurazione"""
        icon_path = "./resources/icons/system.png"
        if os.path.exists(icon_path):
            try:
                icon = pygame.image.load(icon_path)
                # Ridimensiona l'icona per adattarla al pulsante
                scale_factor = self.screen_width / 1920.0
                icon_size = int(64 * scale_factor)  # Dimensione base 64px
                scaled_icon = pygame.transform.scale(icon, (icon_size, icon_size))
                logger.info(f"Icona configurazione caricata: {icon_path} -> {icon_size}x{icon_size}")
                return scaled_icon
            except Exception as e:
                logger.warning(f"Errore caricamento icona configurazione: {e}")
        else:
            logger.warning(f"File icona configurazione non trovato: {icon_path}")
        return None
    
    def handle_input(self, action):
        """Gestisce l'input nel menu delle piattaforme"""
        if self.show_image_menu:
            # Se il menu immagini è aperto, gestisci l'input per quello
            return self.handle_image_menu_input(action)
        
        if action == 'up':
            if self.selected_platform > 0:
                self.selected_platform -= 1
                self.update_scroll()
        elif action == 'down':
            max_platforms = self.platform_manager.get_platform_count()
            if self.selected_platform < max_platforms:
                self.selected_platform += 1
                self.update_scroll()
        elif action == 'confirm':
            # Selezione normale
            if self.selected_platform == 0:
                return 'config'
            else:
                return self.platform_manager.get_platform(self.selected_platform - 1)
        elif action == 'confirm_hold':
            # Tenere premuto per aprire menu immagini
            if self.selected_platform > 0:  # Solo per piattaforme, non per configurazione
                self.open_image_menu()
        elif action == 'back':
            if self.show_image_menu:
                self.close_image_menu()
        
        return None

    def handle_image_menu_input(self, action):
        """Gestisce l'input nel menu di selezione immagini con navigazione in tutte le direzioni"""
        # Calcola il numero di colonne in base alla risoluzione (stesso calcolo del draw_image_menu)
        if self.screen_width >= 1200:
            images_per_row = 4
        elif self.screen_width >= 800:
            images_per_row = 3
        else:
            images_per_row = 2
        
        if action == 'up':
            # Vai alla riga sopra
            if self.selected_image_index >= images_per_row:
                self.selected_image_index -= images_per_row
        elif action == 'down':
            # Vai alla riga sotto
            if self.selected_image_index + images_per_row < len(self.available_images):
                self.selected_image_index += images_per_row
        elif action == 'left':
            # Vai alla colonna a sinistra
            if self.selected_image_index > 0:
                self.selected_image_index -= 1
        elif action == 'right':
            # Vai alla colonna a destra
            if self.selected_image_index < len(self.available_images) - 1:
                self.selected_image_index += 1
        elif action == 'confirm':
            # Applica l'immagine selezionata
            self.apply_selected_image()
        elif action == 'back':
            # Chiudi menu senza applicare
            self.close_image_menu()
        
        return None

    def open_image_menu(self):
        """Apre il menu di selezione immagini"""
        if self.selected_platform > 0 and len(self.available_images) > 0:
            self.show_image_menu = True
            self.selected_image_index = 0
            logger.info("Menu immagini aperto")

    def close_image_menu(self):
        """Chiude il menu di selezione immagini"""
        self.show_image_menu = False
        self.selected_image_index = 0
        logger.info("Menu immagini chiuso")

    def apply_selected_image(self):
        """Applica l'immagine selezionata alla piattaforma"""
        if (self.selected_platform > 0 and 
            self.selected_image_index < len(self.available_images)):
            
            platform = self.platform_manager.get_platform(self.selected_platform - 1)
            if platform:
                image_filename = self.available_images[self.selected_image_index]['filename']
                success = self.platform_manager.save_platform_image(platform['name'], image_filename)
                if success:
                    logger.info(f"Immagine {image_filename} applicata a {platform['name']}")
                else:
                    logger.error(f"Errore applicazione immagine a {platform['name']}")
        
        self.close_image_menu()

    def get_platform_image(self, platform_name):
        """Ottiene l'immagine personalizzata per una piattaforma"""
        image_filename = self.platform_manager.get_platform_image(platform_name)
        if image_filename:
            # Trova l'immagine nella lista delle immagini disponibili
            for img_info in self.available_images:
                if img_info['filename'] == image_filename:
                    return img_info['image']
        return None

    def update_scroll(self):
        """Aggiorna lo scroll per mantenere l'elemento selezionato visibile"""
        if not self.scroll_enabled:
            return
        
        # Calcola la posizione dell'elemento selezionato
        item_height = self.platform_height + self.platform_spacing
        selected_y = self.start_y + self.selected_platform * item_height - self.scroll_offset
        
        # Calcola l'area visibile
        available_height = self.screen_height - 200  # 100px footbar + 100px per titolo e margini
        
        # Se l'elemento è sopra l'area visibile, scrolla su
        if selected_y < self.start_y:
            self.scroll_offset = max(0, self.selected_platform * item_height)
        # Se l'elemento è sotto l'area visibile, scrolla giù
        elif selected_y + self.platform_height > self.start_y + available_height:
            self.scroll_offset = max(0, (self.selected_platform + 1) * item_height - available_height)

    def draw(self, screen, debug_message="", debug_timer=0, debug_duration=0):
        """Disegna il menu delle piattaforme"""
        # Se il menu immagini è aperto, disegna quello
        if self.show_image_menu:
            self.draw_image_menu(screen)
            return
        
        # Lo sfondo è già disegnato nel metodo draw principale
        
        # Titolo
        title_text = self.font_large.render("SELEZIONA PIATTAFORMA", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Logo e titolo app (destra in alto)
        self.draw_logo_and_title(screen)
        
        # Istruzioni
        instructions = self.font_small.render("Usa direzioni per navigare, INVIO per selezionare, Tieni premuto INVIO per personalizzare", True, self.colors['text_secondary'])
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, 110))
        screen.blit(instructions, instructions_rect)
        
        # Disegna i rettangoli delle piattaforme (incluso quadrato configurazione)
        platform_count = self.platform_manager.get_platform_count()
        available_height = self.screen_height - 200
        
        # Calcola quali elementi sono visibili (incluso quadrato config)
        start_index = max(0, int(self.scroll_offset // (self.platform_height + self.platform_spacing)))
        visible_items = available_height // (self.platform_height + self.platform_spacing) + 2
        end_index = min(platform_count + 1, start_index + visible_items)
        
        for i in range(start_index, end_index):
            # Calcola posizione (verticale)
            y = self.start_y + i * (self.platform_height + self.platform_spacing) - self.scroll_offset
            
            # Salta se fuori dall'area visibile
            if y < self.start_y or y > self.start_y + available_height:
                continue
            
            x = self.start_x
            
            # Colore del rettangolo - sempre sfondo normale
            color = self.colors['surface']
            
            # Disegna rettangolo con bordo di selezione se necessario
            rect = pygame.Rect(x, y, self.platform_width, self.platform_height)
            pygame.draw.rect(screen, color, rect)
            
            # Aggiungi bordo di selezione se questo è il pulsante selezionato
            if i == self.selected_platform:
                # Bordo più sottile e meno aggressivo
                pygame.draw.rect(screen, self.colors['accent'], rect, 3)
            
            # Testo - quadrato configurazione o piattaforma
            if i == 0:
                # Quadrato configurazione con icona
                if self.config_icon:
                    # Disegna l'icona nella parte superiore del pulsante
                    icon_x = x + (self.platform_width - self.config_icon.get_width()) // 2
                    icon_y = y + 15  # Margine superiore
                    screen.blit(self.config_icon, (icon_x, icon_y))
                
                # Testo posizionato in basso
                text = self.font_medium.render(self.config_button['name'], True, self.colors['text'])
                # Posiziona il testo in basso con un margine di 10 pixel dal bordo inferiore
                text_rect = text.get_rect(center=(x + self.platform_width // 2, y + self.platform_height - 10 - text.get_height() // 2))
                screen.blit(text, text_rect)
            else:
                # Piattaforma normale
                platform = self.platform_manager.get_platform(i - 1)
                if not platform:
                    continue
                
                # Disegna immagine personalizzata se disponibile - LAYOUT VERTICALE
                platform_image = self.get_platform_image(platform['name'])
                if platform_image:
                    # Calcola l'area per l'immagine (parte superiore del pulsante)
                    # L'immagine occupa il 70% dell'altezza, il testo il 30%
                    image_area_height = int(self.platform_height * 0.7)
                    text_area_height = self.platform_height - image_area_height
                    
                    # Ottieni dimensioni originali dell'immagine
                    original_width, original_height = platform_image.get_size()
                    aspect_ratio = original_width / original_height
                    
                    # Calcola dimensioni finali per l'area immagine
                    max_width = self.platform_width - 10  # Margine interno
                    max_height = image_area_height - 10   # Margine interno
                    
                    if aspect_ratio > 1:  # Immagine più larga che alta
                        final_width = max_width
                        final_height = int(final_width / aspect_ratio)
                        if final_height > max_height:
                            final_height = max_height
                            final_width = int(final_height * aspect_ratio)
                    else:  # Immagine più alta che larga o quadrata
                        final_height = max_height
                        final_width = int(final_height * aspect_ratio)
                        if final_width > max_width:
                            final_width = max_width
                            final_height = int(final_width / aspect_ratio)
                    
                    # Centra l'immagine nell'area superiore
                    image_x = x + (self.platform_width - final_width) // 2
                    image_y = y + (image_area_height - final_height) // 2
                    
                    # Ridimensiona e disegna l'immagine
                    scaled_image = pygame.transform.scale(platform_image, (final_width, final_height))
                    screen.blit(scaled_image, (image_x, image_y))
                    
                    # Il testo andrà nell'area inferiore
                    text_x = x + self.platform_width // 2
                    text_y = y + image_area_height + (text_area_height // 2)
                else:
                    # Senza immagine, il testo va al centro
                    text_x = x + self.platform_width // 2
                    text_y = y + self.platform_height // 2
                
                # Testo piattaforma - posizionamento intelligente
                platform_name = platform['name']
                text_surface = self.font_medium.render(platform_name, True, self.colors['text'])
                
                if platform_image:
                    # Con immagine: testo centrato nell'area inferiore
                    text_rect = text_surface.get_rect(center=(text_x, text_y))
                    
                    # Aggiungi sfondo semi-trasparente per il testo se necessario
                    if len(platform_name) > 8:  # Se il testo è lungo, aggiungi sfondo
                        bg_rect = text_rect.inflate(10, 5)
                        bg_surface = pygame.Surface(bg_rect.size)
                        bg_surface.set_alpha(180)
                        bg_surface.fill(self.colors['surface'])
                        screen.blit(bg_surface, bg_rect)
                else:
                    # Senza immagine: testo centrato nel pulsante
                    text_rect = text_surface.get_rect(center=(text_x, text_y))
                
                screen.blit(text_surface, text_rect)
        
        # Disegna scrollbar se necessaria
        if self.scroll_enabled:
            self.draw_scrollbar(screen)
        
        # Footbar rimossa - ora usiamo il footer dinamico unificato
        # self.draw_footbar(screen)
        
        # Debug input - a sinistra nel footer
        if debug_message and time.time() - debug_timer < debug_duration:
            debug_surface = self.font_small.render(debug_message, True, self.colors['accent2'])
            debug_x = 20  # Posizione a sinistra
            debug_y = self.screen_height - 30
            screen.blit(debug_surface, (debug_x, debug_y))

    def draw_scrollbar(self, screen):
        """Disegna la scrollbar verticale"""
        available_height = self.screen_height - 200
        scrollbar_width = 20
        scrollbar_x = self.start_x + self.platform_width + 10
        
        # Sfondo scrollbar
        scrollbar_bg = pygame.Rect(scrollbar_x, self.start_y, scrollbar_width, available_height)
        pygame.draw.rect(screen, self.colors['surface'], scrollbar_bg)
        pygame.draw.rect(screen, self.colors['border'], scrollbar_bg, 2)
        
        # Calcola la posizione e dimensione del thumb
        if self.total_height > available_height:
            thumb_height = max(20, int((available_height / self.total_height) * available_height))
            thumb_y = self.start_y + int((self.scroll_offset / (self.total_height - available_height)) * (available_height - thumb_height))
            
            # Thumb della scrollbar
            thumb_rect = pygame.Rect(scrollbar_x + 2, thumb_y, scrollbar_width - 4, thumb_height)
            pygame.draw.rect(screen, self.colors['accent'], thumb_rect)

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
        
        logger.info(f"Caricate {len(icons)} icone PNG per il footer del menu")
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

    def draw_footer_icons(self, screen):
        """Disegna le icone PNG nel footer del menu"""
        if not self.footer_icons:
            return
        
        footbar_height = 100
        footbar_y = self.screen_height - footbar_height
        
        # Calcola la posizione centrale per le icone
        icon_spacing = 250  # Spazio tra le icone (aumentato per più spazio)
        
        # Definisci l'ordine delle icone - solo per il menu piattaforme
        icon_order = ['info', 'rom', 'start']  # Solo info, rom, start per il menu
        
        # Calcola la larghezza totale considerando le icone effettive
        total_width = 0
        for i, icon_type in enumerate(icon_order):
            if icon_type in self.footer_icons:
                total_width += self.footer_icons[icon_type].get_width()
                if i < len(icon_order) - 1:  # Aggiungi spacing tranne per l'ultima icona
                    total_width += icon_spacing
        
        start_x = (self.screen_width - total_width) // 2
        
        # Posizione Y per le icone (centrate nel footer)
        icon_y = footbar_y + 20
        x_offset = start_x
        
        for icon_type in icon_order:
            if icon_type in self.footer_icons:
                icon = self.footer_icons[icon_type]
                # Posiziona l'icona
                screen.blit(icon, (x_offset, icon_y))
                # Avanza per la prossima icona
                x_offset += icon.get_width() + icon_spacing
                
                # Etichetta sotto l'icona
                if icon_type == 'info':
                    label_text = "Seleziona / Hold x Menù"
                    enter_text = "/Enter"
                    backspace_text = None
                    esc_text = None
                elif icon_type == 'rom':
                    label_text = "Indietro"
                    enter_text = None
                    backspace_text = "/Backspace"
                    esc_text = None
                elif icon_type == 'start':
                    label_text = "Exit"
                    enter_text = None
                    backspace_text = None
                    esc_text = "/Esc"
                else:
                    label_text = icon_type
                    enter_text = None
                    backspace_text = None
                    esc_text = None
                
                # Disegna etichetta principale sotto l'icona
                label_surface = self.font_small.render(label_text, True, self.colors['text_secondary'])
                icon_center_x = x_offset + icon.get_width() // 2  # Centro dell'icona corrente
                label_rect = label_surface.get_rect(center=(icon_center_x, icon_y + icon.get_height() + 15))
                screen.blit(label_surface, label_rect)
                
                # Disegna "/Enter" a destra del pulsante (solo per pulsante 1)
                if enter_text:
                    enter_surface = self.font_small.render(enter_text, True, self.colors['text_secondary'])
                    enter_x = icon_center_x + 10  # 10 pixel a destra del centro del pulsante
                    enter_y = icon_y + icon.get_height() // 2 - enter_surface.get_height() // 2  # Centrato verticalmente
                    screen.blit(enter_surface, (enter_x, enter_y))
                
                # Disegna "/Backspace" a destra del pulsante (solo per pulsante 2)
                if backspace_text:
                    backspace_surface = self.font_small.render(backspace_text, True, self.colors['text_secondary'])
                    backspace_x = icon_center_x + 10  # 10 pixel a destra del centro del pulsante
                    backspace_y = icon_y + icon.get_height() // 2 - backspace_surface.get_height() // 2  # Centrato verticalmente
                    screen.blit(backspace_surface, (backspace_x, backspace_y))
                
                # Disegna "/Esc" a destra del pulsante (solo per pulsante Start)
                if esc_text:
                    esc_surface = self.font_small.render(esc_text, True, self.colors['text_secondary'])
                    esc_x = icon_center_x + 10  # 10 pixel a destra del centro del pulsante
                    esc_y = icon_y + icon.get_height() // 2 - esc_surface.get_height() // 2  # Centrato verticalmente
                    screen.blit(esc_surface, (esc_x, esc_y))

    def draw_logo_and_title(self, screen):
        """Disegna il logo e il titolo dell'applicazione"""
        if self.logo_image:
            # Posiziona il logo in alto a destra
            logo_x = self.screen_width - self.logo_image.get_width() - 20
            logo_y = 20
            screen.blit(self.logo_image, (logo_x, logo_y))
            
            # Titolo dell'applicazione sotto il logo
            title_text = self.font_medium.render("LRscript", True, self.colors['accent'])
            title_rect = title_text.get_rect()
            title_rect.centerx = logo_x + self.logo_image.get_width() // 2
            title_rect.top = logo_y + self.logo_image.get_height() + 10
            screen.blit(title_text, title_rect)

    def draw_footbar(self, screen):
        """Disegna la footbar con informazioni e controlli"""
        footbar_height = 100
        footbar_y = self.screen_height - footbar_height
        
        # Sfondo footbar - senza bordo
        footbar_rect = pygame.Rect(0, footbar_y, self.screen_width, footbar_height)
        pygame.draw.rect(screen, self.colors['surface'], footbar_rect)
        
        # Informazioni piattaforma selezionata - stile simile alla schermata principale
        if self.selected_platform == 0:
            # Pulsante configurazione selezionato
            platform_text = f"[PLAT] {self.config_button['name']}"
            platform_surface = self.font_small.render(platform_text, True, self.colors['accent2'])
            screen.blit(platform_surface, (20, footbar_y + 5))
        elif self.platform_manager.get_platform_count() > 0:
            # Piattaforma normale selezionata (indice -1 perché il primo è configurazione)
            selected_platform = self.platform_manager.get_platform(self.selected_platform - 1)
            if selected_platform:
                platform_text = f"[PLAT] {selected_platform['name']}"
                platform_surface = self.font_small.render(platform_text, True, self.colors['accent2'])
                screen.blit(platform_surface, (20, footbar_y + 5))
        
        # Informazioni joystick - font ridotto per footer più pulito
        joystick_text = "[JOY] USB gamepad"  # Assumiamo joystick rilevato
        joystick_surface = self.font_small.render(joystick_text, True, self.colors['text'])
        screen.blit(joystick_surface, (20, footbar_y + 30))
        
        # Informazioni risoluzione e versione - font ancora più ridotto
        resolution_text = f"[SCR] {self.screen_width}x{self.screen_height}"
        resolution_surface = self.font_tiny.render(resolution_text, True, self.colors['text_secondary'])
        screen.blit(resolution_surface, (self.screen_width - 250, footbar_y + 5))
        
        version_text = f"[VER] {self.platform_manager.get_program_version()}"
        version_surface = self.font_small.render(version_text, True, self.colors['text_secondary'])
        screen.blit(version_surface, (self.screen_width - 150, footbar_y + 70))
        
        # Disegna le icone del footer
        self.draw_footer_icons(screen)

    def draw_image_menu(self, screen):
        """Disegna il menu di selezione immagini"""
        # Sfondo semi-trasparente
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Titolo
        title_text = self.font_large.render("SCEGLI IMMAGINE PULSANTE", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Istruzioni
        instructions = self.font_small.render("Usa SU/GIÙ/SINISTRA/DESTRA per navigare, INVIO per applicare, BACK per annullare", True, self.colors['text_secondary'])
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, 130))
        screen.blit(instructions, instructions_rect)
        
        # Calcola layout griglia per le immagini (ESATTE dimensioni dei pulsanti)
        # Adatta il numero di colonne in base alla risoluzione
        if self.screen_width >= 1200:
            images_per_row = 4
        elif self.screen_width >= 800:
            images_per_row = 3
        else:
            images_per_row = 2
            
        image_width = self.platform_width   # Stessa larghezza dei pulsanti
        image_height = self.platform_height # Stessa altezza dei pulsanti
        spacing = 20
        start_x = (self.screen_width - (images_per_row * image_width + (images_per_row - 1) * spacing)) // 2
        start_y = 200
        
        # Disegna le immagini in griglia
        for i, img_info in enumerate(self.available_images):
            row = i // images_per_row
            col = i % images_per_row
            
            x = start_x + col * (image_width + spacing)
            y = start_y + row * (image_height + spacing)
            
            # Colore del bordo
            if i == self.selected_image_index:
                border_color = self.colors['selected']
            else:
                border_color = self.colors['surface']
            
            # Disegna bordo (stesse dimensioni dei pulsanti)
            border_rect = pygame.Rect(x, y, image_width, image_height)
            pygame.draw.rect(screen, border_color, border_rect, 3)
            
            # Ridimensiona e disegna immagine (mantiene proporzioni)
            original_width, original_height = img_info['image'].get_size()
            aspect_ratio = original_width / original_height
            
            # Calcola dimensioni finali mantenendo le proporzioni
            if aspect_ratio > 1:  # Immagine più larga che alta
                final_width = image_width - 10  # Margine interno
                final_height = int(final_width / aspect_ratio)
                if final_height > image_height - 10:
                    final_height = image_height - 10
                    final_width = int(final_height * aspect_ratio)
            else:  # Immagine più alta che larga o quadrata
                final_height = image_height - 10  # Margine interno
                final_width = int(final_height * aspect_ratio)
                if final_width > image_width - 10:
                    final_width = image_width - 10
                    final_height = int(final_width / aspect_ratio)
            
            # Centra l'immagine nel rettangolo
            image_x = x + (image_width - final_width) // 2
            image_y = y + (image_height - final_height) // 2
            
            scaled_image = pygame.transform.scale(img_info['image'], (final_width, final_height))
            screen.blit(scaled_image, (image_x, image_y))
            
            # Nome file sotto l'immagine
            filename_text = self.font_small.render(img_info['filename'], True, self.colors['text'])
            filename_rect = filename_text.get_rect(center=(x + image_width // 2, y + image_height + 15))
            screen.blit(filename_text, filename_rect)
