# -*- coding: utf-8 -*-

"""
LRscript - Costanti e Configurazioni
====================================
Tutte le costanti, configurazioni e funzioni di utilità del progetto.
"""

import os
import pygame
import logging

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
    pygame.init()
    info = pygame.display.Info()
    return info.current_w, info.current_h

# Ottieni la risoluzione del monitor
SCREEN_WIDTH, SCREEN_HEIGHT = get_screen_resolution()

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

# Carica font personalizzato se disponibile
def load_custom_font():
    """Carica il font personalizzato se disponibile"""
    if FONT_NAME is None:
        return None
    
    font_path = f"./resources/fonts/{FONT_NAME}"
    if os.path.exists(font_path):
        try:
            return font_path
        except Exception as e:
            return None
    else:
        return None

# Font personalizzato
CUSTOM_FONT_PATH = load_custom_font()
