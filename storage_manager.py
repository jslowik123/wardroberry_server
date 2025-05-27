import os
import logging
from typing import Optional, BinaryIO
from uuid import uuid4
import mimetypes


class StorageManager:
    """
    Einfacher StorageManager für Wardroberry App - nur für Datei-Validierung
    Kein Upload mehr, nur Validierung der Bilddateien
    """
    
    def __init__(self):
        """
        Initialisiert den StorageManager (nur für Validierung)
        """
        self.logger = logging.getLogger(__name__)
        
    def validate_image_file(self, content_type: str, file_size: int) -> tuple[bool, str]:
        """
        Validiert eine Bilddatei
        
        Args:
            content_type: MIME-Type der Datei
            file_size: Größe der Datei in Bytes
            
        Returns:
            Tuple (is_valid, error_message)
        """
        # Erlaubte MIME-Types
        allowed_types = [
            'image/jpeg',
            'image/jpg', 
            'image/png',
            'image/webp',
            'image/gif'
        ]
        
        # Content-Type prüfen
        if content_type not in allowed_types:
            return False, f"Dateityp nicht erlaubt. Erlaubt: {', '.join(allowed_types)}"
        
        # Dateigröße prüfen (10MB Maximum)
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            return False, f"Datei zu groß. Maximum: {max_size // (1024*1024)}MB"
        
        # Minimale Dateigröße
        min_size = 1024  # 1KB
        if file_size < min_size:
            return False, "Datei zu klein"
        
        return True, ""
    
    def health_check(self) -> bool:
        """
        Überprüft die Storage-Verbindung (immer True da lokal)
        
        Returns:
            True da keine externe Abhängigkeit
        """
        return True 