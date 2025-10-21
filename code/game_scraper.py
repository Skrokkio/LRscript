# -*- coding: utf-8 -*-

"""
LRscript - Game Scraper
=======================
Classe per il scraping dei giochi e download delle immagini.
"""

import os
import requests
import threading
import logging

logger = logging.getLogger('LRscript')

class GameScraper:
    """Classe per il scraping dei giochi - mantiene la logica originale"""
    
    def __init__(self):
        self.games_list = []
        self.current_game_index = 0
        self.search_text = ""
        
    def search_games(self, search_term):
        """Cerca giochi basandosi sul termine di ricerca"""
        if not search_term.strip():
            return []
        
        # Simula ricerca - qui implementeresti la logica reale
        # Per ora restituiamo una lista di esempio
        return [
            "10-yard fight (world, set 1)",
            "1942 (rev. B)",
            "1943: The Battle of Midway (rev. A)",
            "1944: The Loop Master (USA)",
            "Ace Driver: Victory Lap",
            "After Burner",
            "Alien vs Predator",
            "Area 51",
            "Asteroids",
            "Battlezone"
        ]
    
    def get_game_info(self, game_name):
        """Ottiene informazioni dettagliate su un gioco"""
        # Simula ottenimento info - qui implementeresti la logica reale
        return {
            'name': game_name,
            'cabinet': f"cabinet_{game_name.replace(' ', '_').lower()}.png",
            'title': f"title_{game_name.replace(' ', '_').lower()}.png",
            'ingame': f"ingame_{game_name.replace(' ', '_').lower()}.png",
            'marquee': f"marquee_{game_name.replace(' ', '_').lower()}.png",
            'border': f"border_{game_name.replace(' ', '_').lower()}.png"
        }

class ImageDownloader:
    """Classe per il download delle immagini - mantiene la logica originale"""
    
    def __init__(self):
        self.download_queue = []
        self.downloading = False
        
    def add_download(self, url, destination):
        """Aggiunge un download alla coda"""
        self.download_queue.append((url, destination))
        
    def start_downloads(self):
        """Avvia i download in background"""
        if not self.downloading and self.download_queue:
            self.downloading = True
            thread = threading.Thread(target=self._download_worker)
            thread.daemon = True
            thread.start()
    
    def _download_worker(self):
        """Worker thread per i download"""
        while self.download_queue:
            url, destination = self.download_queue.pop(0)
            try:
                # Testa la connessione prima del download
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    os.makedirs(os.path.dirname(destination), exist_ok=True)
                    with open(destination, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Scaricato: {os.path.basename(destination)}")
                else:
                    print(f"⚠️ Download fallito: {url} (Status: {response.status_code})")
            except requests.exceptions.ConnectionError:
                print(f"❌ Errore connessione: {url}")
            except requests.exceptions.Timeout:
                print(f"⏰ Timeout: {url}")
            except Exception as e:
                print(f"❌ Errore download {url}: {e}")
        
        self.downloading = False
