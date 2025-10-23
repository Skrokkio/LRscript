# -*- coding: utf-8 -*-

"""
LRscript - Config UI
====================
Interfaccia per configurazione pulsanti joystick.
"""

import time
import pygame
import logging

logger = logging.getLogger('LRscript')

class ConfigUI:
    """Interfaccia per configurazione pulsanti joystick"""
    
    def __init__(self, joystick_config, screen_width, screen_height, colors, fonts):
        self.config = joystick_config
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.colors = colors
        self.fonts = fonts
        
        self.buttons = ['button_1', 'button_2', 'button_3', 'l1', 'r1', 'start', 'select']
        self.button_labels = {
            'button_1': 'Pulsante 1 (Conferma)',
            'button_2': 'Pulsante 2 (Annulla)',
            'button_3': 'Pulsante 3 (Scarica Rom)',
            'l1': 'L1 (Scroll Su)',
            'r1': 'R1 (Scroll Giù)',
            'start': 'Start',
            'select': 'Select'
        }
        
        self.selected_index = 0
        self.capture_mode = False
        self.capturing_for = None
        
        # Variabili per conferma salvataggio
        self.save_confirmation_active = False
        self.save_confirmation_timer = 0
        self.save_confirmation_duration = 3.0  # Mostra per 3 secondi
    
    def draw(self, screen):
        """Disegna l'interfaccia di configurazione"""
        # Titolo
        title_text = self.fonts['large'].render("CONFIGURAZIONE PULSANTI JOYSTICK", True, self.colors['text'])
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Istruzioni
        if self.capture_mode:
            instructions = self.fonts['medium'].render("Premi il pulsante che vuoi assegnare...", True, self.colors['accent'])
        else:
            instructions = self.fonts['small'].render("Usa direzioni per navigare, INVIO per configurare, ESC per uscire", True, self.colors['text_secondary'])
        instructions_rect = instructions.get_rect(center=(self.screen_width // 2, 110))
        screen.blit(instructions, instructions_rect)
        
        # Lista pulsanti
        start_y = 150
        line_height = 50
        box_width = 400
        box_height = 40
        
        for i, button_key in enumerate(self.buttons):
            y = start_y + i * line_height
            
            # Colore del rettangolo
            if i == self.selected_index:
                color = self.colors['selected']
            else:
                color = self.colors['surface']
            
            # Disegna rettangolo
            x = (self.screen_width - box_width) // 2
            rect = pygame.Rect(x, y, box_width, box_height)
            pygame.draw.rect(screen, color, rect)
            
            # Testo pulsante
            label_text = self.fonts['medium'].render(self.button_labels[button_key], True, self.colors['text'])
            screen.blit(label_text, (x + 10, y + 10))
            
            # Valore pulsante
            button_value = self.config.get_button_mapping(button_key)
            value_text = self.fonts['medium'].render(f"[{button_value}]", True, self.colors['accent'])
            value_rect = value_text.get_rect()
            value_rect.right = x + box_width - 10
            value_rect.centery = y + box_height // 2
            screen.blit(value_text, value_rect)
        
        # Pulsanti di controllo
        control_y = start_y + len(self.buttons) * line_height + 30
        control_spacing = 150
        
        # SALVA
        save_x = (self.screen_width - control_spacing * 2) // 2
        save_rect = pygame.Rect(save_x, control_y, 120, 40)
        save_color = self.colors['accent'] if self.selected_index == len(self.buttons) else self.colors['surface']
        pygame.draw.rect(screen, save_color, save_rect)
        save_text = self.fonts['medium'].render("SALVA", True, self.colors['text'])
        save_text_rect = save_text.get_rect(center=save_rect.center)
        screen.blit(save_text, save_text_rect)
        
        # RESET DEFAULT
        reset_x = save_x + control_spacing
        reset_rect = pygame.Rect(reset_x, control_y, 120, 40)
        reset_color = self.colors['accent'] if self.selected_index == len(self.buttons) + 1 else self.colors['surface']
        pygame.draw.rect(screen, reset_color, reset_rect)
        reset_text = self.fonts['medium'].render("RESET", True, self.colors['text'])
        reset_text_rect = reset_text.get_rect(center=reset_rect.center)
        screen.blit(reset_text, reset_text_rect)
        
        # ESC
        esc_text = self.fonts['small'].render("ESC - Esci senza salvare", True, self.colors['text_secondary'])
        esc_rect = esc_text.get_rect(center=(self.screen_width // 2, control_y + 60))
        screen.blit(esc_text, esc_rect)
        
        # Mostra conferma salvataggio se attiva
        if self.save_confirmation_active and (time.time() - self.save_confirmation_timer) < self.save_confirmation_duration:
            self.draw_save_confirmation(screen)
    
    def draw_save_confirmation(self, screen):
        """Disegna la conferma di salvataggio"""
        # Sfondo semi-trasparente scuro
        overlay = pygame.Surface((self.screen_width, self.screen_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Box di conferma
        box_width = 500
        box_height = 200
        box_x = (self.screen_width - box_width) // 2
        box_y = (self.screen_height - box_height) // 2
        
        # Sfondo box
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        pygame.draw.rect(screen, self.colors['surface'], box_rect)
        pygame.draw.rect(screen, self.colors['accent'], box_rect, 4)
        
        # Titolo
        title_text = self.fonts['large'].render("CONFIGURAZIONE SALVATA", True, (100, 255, 100))
        title_rect = title_text.get_rect(center=(self.screen_width//2, box_y + 50))
        screen.blit(title_text, title_rect)
        
        # Messaggio
        message_text = self.fonts['medium'].render("Le impostazioni sono state salvate con successo!", True, self.colors['text'])
        message_rect = message_text.get_rect(center=(self.screen_width//2, box_y + 100))
        screen.blit(message_text, message_rect)
        
        # Istruzioni
        instructions_text = self.fonts['small'].render("La conferma scomparirà automaticamente...", True, self.colors['text_secondary'])
        instructions_rect = instructions_text.get_rect(center=(self.screen_width//2, box_y + 140))
        screen.blit(instructions_text, instructions_rect)
    
    def handle_input(self, action, button_number=None):
        """Gestisce input nella schermata configurazione"""
        if self.capture_mode:
            # Modalità cattura pulsante
            if button_number is not None:
                # Cattura il pulsante
                if self.capturing_for:
                    # Trova se il pulsante è già assegnato ad un'altra azione
                    conflicting_action = None
                    for other_action, other_button in self.config.current_mapping.items():
                        if other_action != self.capturing_for and other_button == button_number:
                            conflicting_action = other_action
                            break
                    
                    if conflicting_action:
                        logger.info(f"Pulsante {button_number} era assegnato a {conflicting_action}, ora riassegnato a {self.capturing_for}")
                    else:
                        logger.info(f"Pulsante {self.capturing_for} assegnato a {button_number}")
                    
                    self.config.set_button_mapping(self.capturing_for, button_number)
                
                self.capture_mode = False
                self.capturing_for = None
                return None  # Continua nella schermata config
        elif action == 'back':
            # Annulla cattura
            self.capture_mode = False
            self.capturing_for = None
            return None  # Continua nella schermata config
        else:
            # Navigazione normale
            if action == 'up':
                if self.selected_index > 0:
                    self.selected_index -= 1
            elif action == 'down':
                max_index = len(self.buttons) + 1  # +1 per i pulsanti di controllo
                if self.selected_index < max_index:
                    self.selected_index += 1
            elif action == 'confirm':
                # Se siamo in modalità cattura, annulla la cattura
                if self.capture_mode:
                    self.capture_mode = False
                    self.capturing_for = None
                    return None  # Continua nella schermata config
                
                logger.info(f"Conferma premuta, selected_index: {self.selected_index}, len(buttons): {len(self.buttons)}")
                if self.selected_index < len(self.buttons):
                    # Configura pulsante
                    button_key = self.buttons[self.selected_index]
                    self.capture_mode = True
                    self.capturing_for = button_key
                    logger.info(f"Iniziata configurazione per {button_key}")
                elif self.selected_index == len(self.buttons):
                    # SALVA
                    logger.info("Salvataggio configurazione")
                    self.save_and_exit()
                elif self.selected_index == len(self.buttons) + 1:
                    # RESET DEFAULT
                    logger.info("Reset configurazione")
                    self.reset_to_default()
            elif action == 'back':
                # ESC - esci senza salvare
                return 'exit'
        
        return None
    
    def save_and_exit(self):
        """Salva configurazione e mostra conferma"""
        if self.config.save_config():
            logger.info("Configurazione joystick salvata con successo")
            # Mostra conferma di salvataggio
            self.save_confirmation_active = True
            self.save_confirmation_timer = time.time()
            return None  # Non esce immediatamente
        else:
            logger.error("Errore nel salvataggio della configurazione")
            return None
    
    def reset_to_default(self):
        """Ripristina configurazione default"""
        self.config.reset_to_default()
        logger.info("Configurazione joystick ripristinata ai valori default")
