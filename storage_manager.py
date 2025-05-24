import os
import logging
from typing import Optional, BinaryIO
from uuid import uuid4
from supabase import create_client, Client
import mimetypes


class StorageManager:
    """
    StorageManager für Wardroberry App - verwaltet File Uploads zu Supabase Storage
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialisiert den StorageManager
        
        Args:
            supabase_url: Supabase URL (falls nicht als ENV Variable gesetzt)
            supabase_key: Supabase Service Role Key für Storage-Operationen
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL und Service Role Key müssen gesetzt sein")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.logger = logging.getLogger(__name__)
        
        # Storage Bucket für Kleidungsbilder
        self.clothing_bucket = "clothing-images"
        
    def upload_clothing_image(self, user_id: str, file_content: bytes, 
                            filename: str, content_type: str = None) -> str:
        """
        Lädt ein Kleidungsbild in Supabase Storage hoch
        
        Args:
            user_id: UUID des Nutzers
            file_content: Binärdaten der Datei
            filename: Originaler Dateiname
            content_type: MIME-Type der Datei
            
        Returns:
            Public URL des hochgeladenen Bildes
        """
        try:
            # Generiere eindeutigen Dateinamen
            file_extension = self._get_file_extension(filename)
            unique_filename = f"{user_id}/{uuid4()}{file_extension}"
            
            # Content-Type automatisch erkennen falls nicht angegeben
            if not content_type:
                content_type = mimetypes.guess_type(filename)[0] or 'image/jpeg'
            
            # Upload zu Supabase Storage
            result = self.client.storage.from_(self.clothing_bucket).upload(
                path=unique_filename,
                file=file_content,
                file_options={
                    "content-type": content_type,
                    "cache-control": "3600"
                }
            )
            
            if result:
                # Generiere public URL
                public_url = self.client.storage.from_(self.clothing_bucket).get_public_url(unique_filename)
                self.logger.info(f"Bild hochgeladen: {unique_filename}")
                return public_url
            else:
                raise Exception("Upload fehlgeschlagen")
                
        except Exception as e:
            self.logger.error(f"Fehler beim Hochladen des Bildes: {e}")
            raise
    
    def delete_clothing_image(self, image_url: str) -> bool:
        """
        Löscht ein Kleidungsbild aus Supabase Storage
        
        Args:
            image_url: Public URL des zu löschenden Bildes
            
        Returns:
            True wenn erfolgreich gelöscht
        """
        try:
            # Extrahiere Pfad aus der URL
            path = self._extract_path_from_url(image_url)
            
            if not path:
                self.logger.warning(f"Konnte Pfad nicht aus URL extrahieren: {image_url}")
                return False
            
            # Lösche aus Storage
            result = self.client.storage.from_(self.clothing_bucket).remove([path])
            
            if result:
                self.logger.info(f"Bild gelöscht: {path}")
                return True
            else:
                self.logger.warning(f"Bild konnte nicht gelöscht werden: {path}")
                return False
                
        except Exception as e:
            self.logger.error(f"Fehler beim Löschen des Bildes: {e}")
            return False
    
    def get_image_info(self, image_url: str) -> Optional[dict]:
        """
        Holt Informationen zu einem Bild
        
        Args:
            image_url: Public URL des Bildes
            
        Returns:
            Dict mit Bildinformationen oder None
        """
        try:
            path = self._extract_path_from_url(image_url)
            if not path:
                return None
            
            # Hole Datei-Informationen
            info = self.client.storage.from_(self.clothing_bucket).info(path)
            return info
            
        except Exception as e:
            self.logger.error(f"Fehler beim Abrufen der Bildinformationen: {e}")
            return None
    
    def create_clothing_bucket_if_not_exists(self) -> bool:
        """
        Erstellt den clothing-images Bucket falls er nicht existiert
        
        Returns:
            True wenn Bucket existiert oder erstellt wurde
        """
        try:
            # Prüfe ob Bucket existiert
            buckets = self.client.storage.list_buckets()
            
            bucket_exists = any(bucket.name == self.clothing_bucket for bucket in buckets)
            
            if not bucket_exists:
                # Erstelle Bucket
                self.client.storage.create_bucket(
                    self.clothing_bucket,
                    options={
                        "public": True,  # Öffentlich zugänglich für Bilder
                        "file_size_limit": 10485760,  # 10MB Limit
                        "allowed_mime_types": ["image/jpeg", "image/png", "image/webp", "image/gif"]
                    }
                )
                self.logger.info(f"Bucket erstellt: {self.clothing_bucket}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Buckets: {e}")
            return False
    
    def _get_file_extension(self, filename: str) -> str:
        """
        Extrahiert die Dateiendung aus einem Dateinamen
        
        Args:
            filename: Dateiname
            
        Returns:
            Dateiendung mit Punkt (z.B. '.jpg')
        """
        if '.' in filename:
            return '.' + filename.rsplit('.', 1)[1].lower()
        return '.jpg'  # Fallback
    
    def _extract_path_from_url(self, url: str) -> Optional[str]:
        """
        Extrahiert den Storage-Pfad aus einer Public URL
        
        Args:
            url: Public URL des Bildes
            
        Returns:
            Storage-Pfad oder None
        """
        try:
            # Supabase Storage URL Format: 
            # https://[project_id].supabase.co/storage/v1/object/public/[bucket]/[path]
            if self.clothing_bucket in url:
                parts = url.split(f"{self.clothing_bucket}/")
                if len(parts) > 1:
                    return parts[1]
            return None
            
        except Exception as e:
            self.logger.error(f"Fehler beim Extrahieren des Pfades aus URL: {e}")
            return None
    
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
        Überprüft die Storage-Verbindung
        
        Returns:
            True wenn Storage erreichbar ist
        """
        try:
            # Teste Bucket-Zugriff
            self.client.storage.list_buckets()
            return True
        except Exception as e:
            self.logger.error(f"Storage Health Check fehlgeschlagen: {e}")
            return False 