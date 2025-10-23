# -*- coding: utf-8 -*-

"""
LRscript - Joystick Manager
===========================
Gestore per l'input del joystick e configurazione pulsanti.
"""

import os
import json
import time
import pygame
import logging

logger = logging.getLogger('LRscript')

class JoystickConfig:
    """Gestisce la configurazione dei pulsanti del joystick"""
    
    def __init__(self):
        self.config_file = "./joystick_mapping.json"
        self.default_mapping = {
            'button_1': 0,    # A/Conferma
            'button_2': 2,    # X/Back
            'button_3': 1,    # B/Scarica Rom
            'l1': 4,          # L1/Scroll up
            'r1': 5,          # R1/Scroll down
            'start': 8,       # Start
            'select': 9       # Select
        }
        self.current_mapping = self.load_config()
        logger.info(f"Configurazione joystick caricata: {self.current_mapping}")
    
    def load_config(self):
        """Carica configurazione da file o crea default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    logger.info(f"Configurazione joystick caricata da {self.config_file}")
                    return config
            else:
                logger.info("File configurazione joystick non trovato, uso valori default")
                return self.default_mapping.copy()
        except Exception as e:
            logger.warning(f"Errore caricamento configurazione joystick: {e}, uso valori default")
            return self.default_mapping.copy()
    
    def save_config(self):
        """Salva configurazione su file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_mapping, f, indent=2, ensure_ascii=False)
            logger.info(f"Configurazione joystick salvata in {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Errore salvataggio configurazione joystick: {e}")
            return False
    
    def get_button_mapping(self, action):
        """Ottiene il numero del pulsante per un'azione"""
        return self.current_mapping.get(action, None)
    
    def set_button_mapping(self, action, button_number):
        """Imposta il numero del pulsante per un'azione"""
        if action in self.current_mapping:
            self.current_mapping[action] = button_number
            logger.info(f"Pulsante {action} impostato su {button_number}")
            # Salva automaticamente la configurazione
            self.save_config()
            return True
        return False
    
    def reset_to_default(self):
        """Ripristina configurazione default"""
        self.current_mapping = self.default_mapping.copy()
        logger.info("Configurazione joystick ripristinata ai valori default")

class JoystickManager:
    """Gestore joystick nativo Pygame"""
    
    def __init__(self):
        self.joystick = None
        self.joystick_detected = False
        self.joystick_name = ""
        self.last_input_time = 0
        self.input_delay = 0.2
        self.dpad_pressed = {'up': False, 'down': False, 'left': False, 'right': False}
        self.dpad_press_time = {'up': 0, 'down': 0, 'left': 0, 'right': 0}
        self.fast_scroll_delay = 0.5
        self.fast_scroll_interval = 0.1
        self.last_fast_scroll_time = 0
        
        # Tracking per L1/R1 scrolling veloce continuo - SISTEMA SEMPLIFICATO
        self.l1_pressed = False
        self.r1_pressed = False
        self.l1_press_time = 0
        self.r1_press_time = 0
        self.last_l1_r1_scroll_time = 0
        
        # Tracking per Start (uscita applicazione)
        self.buttons_pressed = set()  # Insieme dei pulsanti attualmente premuti
        self.select_start_timeout = 0.5  # Timeout per il pulsante Start
        self.select_start_triggered = False  # Flag per evitare trigger multipli
        self.select_start_trigger_time = 0  # Timestamp dell'ultimo trigger
        
        # Tracking per pulsante di conferma (tenere premuto)
        self.confirm_press_time = 0  # Timestamp quando è stato premuto confirm
        self.confirm_held = False    # Flag se confirm è tenuto premuto
        self.confirm_hold_time = 0.8  # Tempo per tenere premuto (secondi)
        
        # Configurazione pulsanti
        self.config = JoystickConfig()
        
        self.detect_joystick()
    
    def detect_joystick(self):
        """Rileva e inizializza il joystick, escludendo dispositivi mouse"""
        # Lista di nomi di dispositivi da escludere (mouse e altri dispositivi non-joystick)
        excluded_devices = [
            'mouse', 'Mouse', 'MOUSE',
            'trackball', 'Trackball', 'TRACKBALL',
            'touchpad', 'TouchPad', 'TOUCHPAD',
            'touchscreen', 'TouchScreen', 'TOUCHSCREEN',
            'keyboard', 'Keyboard', 'KEYBOARD',
            'tablet', 'Tablet', 'TABLET',
            'pen', 'Pen', 'PEN',
            'stylus', 'Stylus', 'STYLUS'
        ]
        
        # Lista di nomi di dispositivi joystick/controller preferiti
        preferred_devices = [
            'dragonrise', 'DragonRise', 'DRAGONRISE',
            'arcade', 'Arcade', 'ARCADE',
            'gamepad', 'GamePad', 'GAMEPAD',
            'joystick', 'Joystick', 'JOYSTICK',
            'controller', 'Controller', 'CONTROLLER',
            'xbox', 'Xbox', 'XBOX',
            'playstation', 'PlayStation', 'PLAYSTATION',
            'nintendo', 'Nintendo', 'NINTENDO',
            'logitech', 'Logitech', 'LOGITECH',
            'thrustmaster', 'ThrustMaster', 'THRUSTMASTER',
            'saitek', 'Saitek', 'SAITEK'
        ]
        
        joystick_count = pygame.joystick.get_count()
        logger.info(f"Dispositivi di input rilevati: {joystick_count}")
        
        if joystick_count > 0:
            # Cerca il miglior joystick disponibile
            best_joystick = None
            best_joystick_name = ""
            best_joystick_index = -1
            
            for i in range(joystick_count):
                try:
                    temp_joystick = pygame.joystick.Joystick(i)
                    temp_joystick.init()
                    device_name = temp_joystick.get_name()
                    
                    logger.debug(f"Dispositivo {i}: {device_name}")
                    
                    # Controlla se il dispositivo è da escludere
                    is_excluded = any(excluded in device_name for excluded in excluded_devices)
                    if is_excluded:
                        logger.debug(f"Escluso (dispositivo non-joystick): {device_name}")
                        temp_joystick.quit()
                        continue
                    
                    # Controlla se è un dispositivo preferito
                    is_preferred = any(preferred in device_name for preferred in preferred_devices)
                    
                    # Verifica che abbia le caratteristiche di un joystick
                    has_buttons = temp_joystick.get_numbuttons() > 0
                    has_axes = temp_joystick.get_numaxes() > 0
                    
                    logger.debug(f"Pulsanti: {temp_joystick.get_numbuttons()}, Assi: {temp_joystick.get_numaxes()}, Hat: {temp_joystick.get_numhats()}")
                    
                    # Se ha pulsanti e assi, è probabilmente un joystick valido
                    if has_buttons and has_axes:
                        # Priorità: 1) Dispositivo preferito con indice più basso, 2) Qualsiasi dispositivo con indice più basso
                        should_select = False
                        if best_joystick is None:
                            # Nessun joystick selezionato ancora
                            should_select = True
                        elif is_preferred and not any(preferred in best_joystick_name for preferred in preferred_devices):
                            # Questo è preferito, quello attuale no
                            should_select = True
                        elif (is_preferred and any(preferred in best_joystick_name for preferred in preferred_devices)) or \
                             (not is_preferred and not any(preferred in best_joystick_name for preferred in preferred_devices)):
                            # Stessa categoria di preferenza, scegli quello con indice più basso
                            if i < best_joystick_index:
                                should_select = True
                        
                        if should_select:
                            if best_joystick is not None:
                                best_joystick.quit()
                            best_joystick = temp_joystick
                            best_joystick_name = device_name
                            best_joystick_index = i
                            logger.debug(f"Selezionato come joystick principale: {device_name} (indice {i})")
                        else:
                            temp_joystick.quit()
                    else:
                        logger.debug(f"Escluso (mancano pulsanti o assi): {device_name}")
                        temp_joystick.quit()
                        
                except Exception as e:
                    logger.warning(f"Errore inizializzazione dispositivo {i}: {e}")
                    continue
            
            # Se abbiamo trovato un joystick valido, usalo
            if best_joystick is not None:
                self.joystick = best_joystick
                self.joystick_detected = True
                self.joystick_name = best_joystick_name
                logger.info(f"Joystick selezionato: {self.joystick_name} (indice {best_joystick_index})")
                logger.info(f"Player {best_joystick_index} del cabinato sarà utilizzato per i controlli")
                logger.debug(f"Pulsanti: {self.joystick.get_numbuttons()}, Assi: {self.joystick.get_numaxes()}, Hat: {self.joystick.get_numhats()}")
                return True
            else:
                self.joystick_detected = False
                self.joystick_name = ""
                logger.info("Nessun joystick valido rilevato (solo dispositivi non-joystick trovati)")
                return False
        else:
            self.joystick_detected = False
            self.joystick_name = ""
            logger.info("Nessun dispositivo di input rilevato")
            return False
    
    def handle_events(self, events):
        """Gestisce gli eventi del joystick"""
        current_time = time.time()
        
        # Controlla timeout automatico per Start
        if (self.select_start_triggered and 
            current_time - self.select_start_trigger_time > self.select_start_timeout):
            self.select_start_triggered = False
        
        for event in events:
            if event.type == pygame.JOYBUTTONDOWN:
                self._handle_button_press(event.button, current_time)
            elif event.type == pygame.JOYBUTTONUP:
                self._handle_button_release(event.button, current_time)
            elif event.type == pygame.JOYHATMOTION:
                self._handle_hat_motion(event.value, current_time)
            elif event.type == pygame.JOYAXISMOTION:
                self._handle_axis_motion(event.axis, event.value, current_time)
    
    def _handle_button_press(self, button, current_time, in_config_screen=False):
        """Gestisce la pressione di un pulsante"""
        if current_time - self.last_input_time < self.input_delay:
            return
        
        # Aggiungi il pulsante all'insieme dei pulsanti premuti
        self.buttons_pressed.add(button)
        
        # Usa la configurazione per i pulsanti
        config = self.config.current_mapping
        
        # Controlla se Start è premuto per uscire (semplificato)
        # Solo se non è già stato triggerato recentemente e NON siamo in schermata config
        if (button == config['start'] and 
            not self.select_start_triggered and 
            current_time - self.last_input_time > self.input_delay and
            not in_config_screen):
            
            logger.info("Start premuto - Uscita applicazione")
            self.select_start_triggered = True
            self.select_start_trigger_time = current_time
            return 'quit_app'
        
        # Gestisci i singoli pulsanti usando la configurazione
        if button == config['button_1']:  # Pulsante 1 (Conferma)
            # Inizia il tracking del tempo di pressione
            self.confirm_press_time = current_time
            self.confirm_held = False
            # Non restituire 'confirm' immediatamente, aspetta il rilascio
            return None
        elif button == config['button_2']:  # Pulsante 2 (Back)
            return 'back'
        elif button == config['button_3']:  # Pulsante 3 (Scarica Rom)
            return 'download_rom'
        elif button == config['l1']:  # L1 - Scorrimento veloce su
            self.l1_pressed = True
            self.l1_press_time = current_time
            return 'scroll_up'
        elif button == config['r1']:  # R1 - Scorrimento veloce giù
            self.r1_pressed = True
            self.r1_press_time = current_time
            return 'scroll_down'
        elif button == config['start']:  # Start
            return None  # Start gestito per uscita applicazione
        elif button == config['select']:  # Select
            return None  # Select non utilizzato attualmente
        
        self.last_input_time = current_time
        return None
    
    def _handle_button_release(self, button, current_time):
        """Gestisce il rilascio di un pulsante"""
        # Rimuovi il pulsante dall'insieme dei pulsanti premuti
        self.buttons_pressed.discard(button)
        
        # Usa la configurazione per i pulsanti
        config = self.config.current_mapping
        
        # Se Start è stato rilasciato, resetta il flag
        if config['start'] not in self.buttons_pressed:
            self.select_start_triggered = False
        
        # Gestisci rilascio del pulsante di conferma
        if button == config['button_1']:
            # Se è stato tenuto premuto abbastanza a lungo, invia segnale hold
            if (self.confirm_press_time > 0 and 
                current_time - self.confirm_press_time >= self.confirm_hold_time and 
                not self.confirm_held):
                self.confirm_held = True
                self.confirm_press_time = 0  # Reset per evitare trigger multipli
                return 'confirm_hold'
            # Se non è stato tenuto abbastanza a lungo, invia confirm normale
            elif self.confirm_press_time > 0:
                self.confirm_press_time = 0
                self.confirm_held = False
                return 'confirm'
            else:
                self.confirm_press_time = 0
                self.confirm_held = False
        
        # Gestisci rilascio L1/R1 per scrolling veloce
        if button == config['l1']:
            self.l1_pressed = False
            self.l1_press_time = 0
            print("🔄 L1 rilasciato - scrolling fermato")
        elif button == config['r1']:
            self.r1_pressed = False
            self.r1_press_time = 0
            print("🔄 R1 rilasciato - scrolling fermato")
    
    def _handle_hat_motion(self, value, current_time):
        """Gestisce il movimento del D-pad (hat)"""
        if current_time - self.last_input_time < self.input_delay:
            return
        
        x, y = value
        
        if x == -1:  # Sinistra
            self.dpad_pressed['left'] = True
            self.dpad_press_time['left'] = current_time
            self.last_input_time = current_time
            # Reset L1/R1 quando si usa D-pad
            self.l1_pressed = False
            self.r1_pressed = False
            return 'left'
        elif x == 1:  # Destra
            self.dpad_pressed['right'] = True
            self.dpad_press_time['right'] = current_time
            self.last_input_time = current_time
            # Reset L1/R1 quando si usa D-pad
            self.l1_pressed = False
            self.r1_pressed = False
            return 'right'
        elif y == -1:  # Su
            self.dpad_pressed['up'] = True
            self.dpad_press_time['up'] = current_time
            self.last_input_time = current_time
            # Reset L1/R1 quando si usa D-pad
            self.l1_pressed = False
            self.r1_pressed = False
            return 'up'
        elif y == 1:  # Giù
            self.dpad_pressed['down'] = True
            self.dpad_press_time['down'] = current_time
            self.last_input_time = current_time
            # Reset L1/R1 quando si usa D-pad
            self.l1_pressed = False
            self.r1_pressed = False
            return 'down'
        else:  # Rilasciato
            self.dpad_pressed = {'up': False, 'down': False, 'left': False, 'right': False}
            return 'dpad_release'
    
    def _handle_axis_motion(self, axis, value, current_time):
        """Gestisce il movimento degli assi analogici"""
        if current_time - self.last_input_time < self.input_delay:
            return
        
        # Gestisce D-pad come assi (per alcuni controller)
        if axis == 0:  # X axis
            if value < -0.5:  # Sinistra
                return 'left'
            elif value > 0.5:  # Destra
                return 'right'
        elif axis == 1:  # Y axis
            if value < -0.5:  # Su
                return 'up'
            elif value > 0.5:  # Giù
                return 'down'
        
        return None
    
    def recheck_joystick(self):
        """Rileva nuovamente il joystick (utile se viene collegato dopo l'avvio)"""
        if not self.joystick_detected:
            print("🔄 Ricontrollo dispositivi joystick...")
            return self.detect_joystick()
        return True
    
    def check_fast_scroll(self):
        """Controlla se è necessario attivare lo scorrimento veloce"""
        current_time = time.time()
        
        if self.dpad_pressed['up']:
            time_pressed = current_time - self.dpad_press_time['up']
            if time_pressed > self.fast_scroll_delay:
                # Adatta l'intervallo di scrolling in base al tempo di pressione
                if time_pressed > 3.0:
                    interval = 0.01  # Molto veloce dopo 3 secondi (100Hz)
                    print("⏫⏫⏫ Scrolling ULTRA veloce ⏫⏫⏫") if time_pressed % 1 < 0.02 else None
                elif time_pressed > 2.0:
                    interval = 0.03  # Più veloce dopo 2 secondi (33Hz)
                    print("⏫⏫ Scrolling molto veloce ⏫⏫") if time_pressed % 1 < 0.05 else None
                elif time_pressed > 1.0:
                    interval = 0.05  # Veloce dopo 1 secondo (20Hz)
                    print("⏫ Scrolling veloce ⏫") if time_pressed % 1 < 0.1 else None
                else:
                    interval = self.fast_scroll_interval  # Normale (10Hz)
                
                if current_time - self.last_fast_scroll_time > interval:
                    self.last_fast_scroll_time = current_time
                    return 'fast_scroll_up'
        
        elif self.dpad_pressed['down']:
            time_pressed = current_time - self.dpad_press_time['down']
            if time_pressed > self.fast_scroll_delay:
                # Adatta l'intervallo di scrolling in base al tempo di pressione
                if time_pressed > 3.0:
                    interval = 0.01  # Molto veloce dopo 3 secondi (100Hz)
                    print("⏬⏬⏬ Scrolling ULTRA veloce ⏬⏬⏬") if time_pressed % 1 < 0.02 else None
                elif time_pressed > 2.0:
                    interval = 0.03  # Più veloce dopo 2 secondi (33Hz)
                    print("⏬⏬ Scrolling molto veloce ⏬⏬") if time_pressed % 1 < 0.05 else None
                elif time_pressed > 1.0:
                    interval = 0.05  # Veloce dopo 1 secondo (20Hz)
                    print("⏬ Scrolling veloce ⏬") if time_pressed % 1 < 0.1 else None
                else:
                    interval = self.fast_scroll_interval  # Normale (10Hz)
                
                if current_time - self.last_fast_scroll_time > interval:
                    self.last_fast_scroll_time = current_time
                    return 'fast_scroll_down'
        
        return None
    
    def check_l1_r1_fast_scroll(self):
        """Controlla se è necessario attivare lo scorrimento veloce continuo con L1/R1 - SISTEMA SEMPLIFICATO"""
        current_time = time.time()
        
        # Verifica lo stato attuale dei pulsanti dal joystick
        if self.joystick:
            config = self.config.current_mapping
            # Controlla che i pulsanti siano mappati correttamente
            l1_button = config.get('l1', -1)
            r1_button = config.get('r1', -1)
            
            # Solo se i pulsanti sono mappati correttamente (non -1)
            if l1_button >= 0 and r1_button >= 0:
                l1_currently_pressed = self.joystick.get_button(l1_button)
                r1_currently_pressed = self.joystick.get_button(r1_button)
            else:
                # Se i pulsanti non sono mappati, considera come non premuti
                l1_currently_pressed = False
                r1_currently_pressed = False
            
            # Se L1 non è più premuto fisicamente, resetta il tracking
            if self.l1_pressed and not l1_currently_pressed:
                self.l1_pressed = False
                self.l1_press_time = 0
                print("🔄 L1 rilevato come rilasciato - scrolling fermato")
            
            # Se R1 non è più premuto fisicamente, resetta il tracking
            if self.r1_pressed and not r1_currently_pressed:
                self.r1_pressed = False
                self.r1_press_time = 0
                print("🔄 R1 rilevato come rilasciato - scrolling fermato")
        
        # Solo se i pulsanti sono effettivamente premuti
        if self.l1_pressed and self.l1_press_time > 0:
            time_pressed = current_time - self.l1_press_time
            if time_pressed > 0.3:  # Dopo 0.3 secondi inizia lo scroll continuo
                # Velocità incrementale: più tieni premuto, più veloce diventa
                if time_pressed > 3.0:
                    interval = 0.0167  # Ultra veloce dopo 3 secondi (60Hz = 300 righe/sec)
                elif time_pressed > 2.0:
                    interval = 0.08  # Veloce dopo 2 secondi (12.5Hz)
                elif time_pressed > 1.0:
                    interval = 0.12  # Medio dopo 1 secondo (8.3Hz)
                else:
                    interval = 0.18  # Lento dopo 0.3 secondi (5.6Hz)
                
                if current_time - self.last_l1_r1_scroll_time > interval:
                    self.last_l1_r1_scroll_time = current_time
                    return 'l1_fast_scroll_up'
        
        elif self.r1_pressed and self.r1_press_time > 0:
            time_pressed = current_time - self.r1_press_time
            if time_pressed > 0.3:  # Dopo 0.3 secondi inizia lo scroll continuo
                # Velocità incrementale: più tieni premuto, più veloce diventa
                if time_pressed > 3.0:
                    interval = 0.012  # Ultra veloce dopo 3 secondi (80Hz = 400 righe/sec)
                elif time_pressed > 2.0:
                    interval = 0.08  # Veloce dopo 2 secondi (12.5Hz)
                elif time_pressed > 1.0:
                    interval = 0.12  # Medio dopo 1 secondo (8.3Hz)
                else:
                    interval = 0.18  # Lento dopo 0.3 secondi (5.6Hz)
                
                if current_time - self.last_l1_r1_scroll_time > interval:
                    self.last_l1_r1_scroll_time = current_time
                    return 'r1_fast_scroll_down'
        
        return None
