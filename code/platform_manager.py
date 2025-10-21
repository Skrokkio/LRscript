# -*- coding: utf-8 -*-

"""
LRscript - Platform Manager
===========================
Gestore per le piattaforme caricate dal file XML.
"""

import os
import xml.etree.ElementTree as ET
import logging
from io import StringIO

logger = logging.getLogger('LRscript')

class PlatformManager:
    """Gestore per le piattaforme caricate dal file XML"""
    
    def __init__(self, xml_file="platforms.xml"):
        self.xml_file = xml_file
        self.platforms = []
        self.load_platforms()
    
    def load_platforms(self):
        """Carica le piattaforme dal file XML"""
        try:
            if not os.path.exists(self.xml_file):
                logger.warning(f"File {self.xml_file} non trovato, creo piattaforme di default")
                self.create_default_platforms()
                return
            
            # Prova prima con il parser normale
            try:
                tree = ET.parse(self.xml_file)
                root = tree.getroot()
            except ET.ParseError as e:
                # Se fallisce, prova a leggere il file come testo e correggere i caratteri &
                logger.warning(f"Errore parsing XML: {e}, provo a correggere automaticamente")
                with open(self.xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Sostituisci temporaneamente i & con &amp; per il parsing
                corrected_content = content.replace('&', '&amp;')
                # Ma ripristina i &amp; che erano già corretti
                corrected_content = corrected_content.replace('&amp;amp;', '&amp;')
                
                # Parsa il contenuto corretto
                root = ET.fromstring(corrected_content)
            
            # Leggi la versione del programma
            version_element = root.find('version')
            self.program_version = version_element.text if version_element is not None else "0.0.0"
            logger.info(f"Versione programma: {self.program_version}")
            
            self.platforms = []
            for platform in root.findall('platform'):
                platform_data = {
                    'name': platform.find('name').text if platform.find('name') is not None else "Piattaforma Sconosciuta",
                    'path': platform.find('cache_path').text if platform.find('cache_path') is not None else "./cache/default",
                    'roms_path': platform.find('roms_path').text if platform.find('roms_path') is not None else "/userdata/roms/default",
                    'xml': platform.find('xml').text if platform.find('xml') is not None else "",
                    'ingame': platform.find('ingame').text if platform.find('ingame') is not None else "",
                    'title': platform.find('title').text if platform.find('title') is not None else "",
                    'info': platform.find('info').text if platform.find('info') is not None else "",
                    'rom': platform.find('rom').text if platform.find('rom') is not None else "",
                    'image': platform.find('image').text if platform.find('image') is not None else ""
                }
                self.platforms.append(platform_data)
            
            logger.info(f"Caricate {len(self.platforms)} piattaforme dal file XML")
            for i, platform in enumerate(self.platforms):
                logger.debug(f"Piattaforma {i+1}: {platform['name']}")
                
        except Exception as e:
            logger.error(f"Errore caricamento piattaforme: {e}")
            self.create_default_platforms()
    
    def create_default_platforms(self):
        """Crea piattaforme di default se il file XML non esiste o è corrotto"""
        # Imposta versione di default
        self.program_version = "0.0.0"
        logger.info(f"Versione programma (default): {self.program_version}")
        
        self.platforms = [
            {
                'name': 'MAME_2003-Plus',
                'path': './cache/MAME_2003-Plus',
                'roms_path': '/userdata/roms/mame078plus',
                'xml': './xml/mame2003-plus.xml',
                'ingame': 'adb.arcadeitalia.net/?mame={rom_name}&type=ingame&resize=0',
                'title': 'adb.arcadeitalia.net/?mame={rom_name}&type=title&resize=0',
                'info': 'adb.arcadeitalia.net/service_scraper.php?ajax=query_mame&game_name={rom_name}&lang=it',
                'rom': 'https://archive.org/download/MAME_2003-Plus_Reference/roms/',
                'image': ''
            }
        ]
        logger.info(f"Create {len(self.platforms)} piattaforme di default")
    
    def get_program_version(self):
        """Ottiene la versione del programma"""
        return getattr(self, 'program_version', '0.0.0')
    
    def get_platform(self, index):
        """Ottiene una piattaforma per indice"""
        if 0 <= index < len(self.platforms):
            return self.platforms[index]
        return None
    
    def get_platform_count(self):
        """Restituisce il numero di piattaforme"""
        return len(self.platforms)
    
    def save_platform_image(self, platform_name, image_filename):
        """Salva l'immagine personalizzata per una piattaforma nel file XML"""
        try:
            # Trova la piattaforma
            platform_index = None
            for i, platform in enumerate(self.platforms):
                if platform['name'] == platform_name:
                    platform_index = i
                    break
            
            if platform_index is None:
                logger.error(f"Piattaforma {platform_name} non trovata")
                return False
            
            # Aggiorna i dati in memoria
            self.platforms[platform_index]['image'] = image_filename
            
            # Salva nel file XML
            try:
                tree = ET.parse(self.xml_file)
                root = tree.getroot()
            except ET.ParseError as e:
                # Se fallisce, prova a leggere il file come testo e correggere i caratteri &
                logger.warning(f"Errore parsing XML per salvataggio: {e}, provo a correggere automaticamente")
                with open(self.xml_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Sostituisci temporaneamente i & con &amp; per il parsing
                corrected_content = content.replace('&', '&amp;')
                # Ma ripristina i &amp; che erano già corretti
                corrected_content = corrected_content.replace('&amp;amp;', '&amp;')
                
                # Parsa il contenuto corretto
                root = ET.fromstring(corrected_content)
                # Crea un nuovo tree per il salvataggio
                tree = ET.ElementTree(root)
            
            platforms = root.findall('platform')
            if platform_index < len(platforms):
                image_elem = platforms[platform_index].find('image')
                if image_elem is not None:
                    image_elem.text = image_filename
                else:
                    # Crea il nuovo elemento se non esiste
                    image_elem = ET.SubElement(platforms[platform_index], 'image')
                    image_elem.text = image_filename
                
                # Salva il file con formattazione corretta
                self._write_xml_with_formatting(tree, self.xml_file)
                logger.info(f"Immagine {image_filename} salvata per {platform_name}")
                return True
            else:
                logger.error(f"Indice piattaforma {platform_index} non valido")
                return False
                
        except Exception as e:
            logger.error(f"Errore salvataggio immagine per {platform_name}: {e}")
            return False

    def get_platform_image(self, platform_name):
        """Ottiene il nome del file immagine per una piattaforma"""
        for platform in self.platforms:
            if platform['name'] == platform_name:
                return platform.get('image', '')
        return ''
    
    def _write_xml_with_formatting(self, tree, filename):
        """Scrive il file XML con formattazione corretta"""
        try:
            # Ottieni la stringa XML formattata
            rough_string = ET.tostring(tree.getroot(), encoding='unicode')
            
            # Parsing per formattazione
            reparsed = ET.parse(StringIO(rough_string))
            
            # Scrivi con indentazione
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0"?>\n')
                self._indent_xml(reparsed.getroot(), 0, f)
        except Exception as e:
            logger.error(f"Errore formattazione XML: {e}")
            # Fallback: salva senza formattazione
            tree.write(filename, encoding='utf-8', xml_declaration=True)
    
    def _indent_xml(self, elem, level, file):
        """Aggiunge indentazione al file XML"""
        indent = "\t" * level
        if len(elem):
            file.write(f"{indent}<{elem.tag}>\n")
            for child in elem:
                self._indent_xml(child, level + 1, file)
            file.write(f"{indent}</{elem.tag}>\n")
        else:
            if elem.text and elem.text.strip():
                file.write(f"{indent}<{elem.tag}>{elem.text}</{elem.tag}>\n")
            else:
                file.write(f"{indent}<{elem.tag}></{elem.tag}>\n")
