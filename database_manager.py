import os
import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timezone
from supabase import create_client, Client
from postgrest.exceptions import APIError


class DatabaseManager:
    """
    DatabaseManager für Wardroberry App mit Supabase Backend
    
    Verwaltet alle Datenbankoperationen für:
    - users (Nutzerprofile)
    - clothes (Kleidungsstücke)
    - outfits (Outfits)
    - outfit_items (Outfit-Kleidung Verknüpfungen)
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialisiert den DatabaseManager
        
        Args:
            supabase_url: Supabase URL (falls nicht als ENV Variable gesetzt)
            supabase_key: Supabase Anon Key (falls nicht als ENV Variable gesetzt)
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase URL und Key müssen gesetzt sein")
        
        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.logger = logging.getLogger(__name__)

    # ======================
    # USERS MANAGEMENT
    # ======================
    
    def create_user_profile(self, user_id: str, email: str, 
                          first_name: str = None, last_name: str = None) -> Dict[str, Any]:
        """
        Erstellt ein Nutzerprofil nach der Registrierung
        
        Args:
            user_id: UUID des Nutzers aus Supabase Auth
            email: E-Mail-Adresse
            first_name: Vorname (optional)
            last_name: Nachname (optional)
            
        Returns:
            Dict mit den erstellten Nutzerdaten
        """
        try:
            data = {
                'id': user_id,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table('users').insert(data).execute()
            self.logger.info(f"Nutzerprofil erstellt: {user_id}")
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Erstellen des Nutzerprofils: {e}")
            raise
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Holt das Nutzerprofil
        
        Args:
            user_id: UUID des Nutzers
            
        Returns:
            Dict mit Nutzerdaten oder None
        """
        try:
            result = self.client.table('users').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden des Nutzerprofils: {e}")
            raise
    
    def update_user_profile(self, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Aktualisiert das Nutzerprofil
        
        Args:
            user_id: UUID des Nutzers
            **kwargs: Felder zum Aktualisieren (first_name, last_name, etc.)
            
        Returns:
            Dict mit aktualisierten Nutzerdaten
        """
        try:
            kwargs['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table('users').update(kwargs).eq('id', user_id).execute()
            self.logger.info(f"Nutzerprofil aktualisiert: {user_id}")
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Aktualisieren des Nutzerprofils: {e}")
            raise
    
    def delete_user_profile(self, user_id: str) -> bool:
        """
        Löscht das Nutzerprofil und alle verknüpften Daten (CASCADE)
        
        Args:
            user_id: UUID des Nutzers
            
        Returns:
            True wenn erfolgreich
        """
        try:
            self.client.table('users').delete().eq('id', user_id).execute()
            self.logger.info(f"Nutzerprofil gelöscht: {user_id}")
            return True
            
        except APIError as e:
            self.logger.error(f"Fehler beim Löschen des Nutzerprofils: {e}")
            raise

    # ======================
    # CLOTHES MANAGEMENT
    # ======================
    
    def add_clothing_item(self, user_id: str, image_url: str, category: str,
                         color: str = None, style: str = None, season: str = None) -> Dict[str, Any]:
        """
        Fügt ein Kleidungsstück hinzu
        
        Args:
            user_id: UUID des Nutzers
            image_url: URL zum Bild in Supabase Storage
            category: Kategorie (z.B. "Oberteil", "Hose", "Schuhe")
            color: Hauptfarbe (optional)
            style: Stil (optional)
            season: Saison (optional)
            
        Returns:
            Dict mit den Kleidungsdaten
        """
        try:
            data = {
                'user_id': user_id,
                'image_url': image_url,
                'category': category,
                'color': color,
                'style': style,
                'season': season,
                'created_at': datetime.now(timezone.utc).isoformat(),
                'updated_at': datetime.now(timezone.utc).isoformat()
            }
            
            result = self.client.table('clothes').insert(data).execute()
            self.logger.info(f"Kleidungsstück hinzugefügt: {result.data[0]['id'] if result.data else 'unknown'}")
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Hinzufügen des Kleidungsstücks: {e}")
            raise
    
    def get_user_clothes(self, user_id: str, category: str = None, 
                        season: str = None, style: str = None) -> List[Dict[str, Any]]:
        """
        Holt alle Kleidungsstücke eines Nutzers mit optionalen Filtern
        
        Args:
            user_id: UUID des Nutzers
            category: Filtert nach Kategorie (optional)
            season: Filtert nach Saison (optional)
            style: Filtert nach Stil (optional)
            
        Returns:
            Liste mit Kleidungsstücken
        """
        try:
            query = self.client.table('clothes').select('*').eq('user_id', user_id)
            
            if category:
                query = query.eq('category', category)
            if season:
                query = query.eq('season', season)
            if style:
                query = query.eq('style', style)
                
            result = query.order('created_at', desc=True).execute()
            return result.data or []
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden der Kleidungsstücke: {e}")
            raise
    
    def get_clothing_item(self, clothing_id: str) -> Optional[Dict[str, Any]]:
        """
        Holt ein einzelnes Kleidungsstück
        
        Args:
            clothing_id: UUID des Kleidungsstücks
            
        Returns:
            Dict mit Kleidungsdaten oder None
        """
        try:
            result = self.client.table('clothes').select('*').eq('id', clothing_id).execute()
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden des Kleidungsstücks: {e}")
            raise
    
    def update_clothing_item(self, clothing_id: str, **kwargs) -> Dict[str, Any]:
        """
        Aktualisiert ein Kleidungsstück
        
        Args:
            clothing_id: UUID des Kleidungsstücks
            **kwargs: Felder zum Aktualisieren
            
        Returns:
            Dict mit aktualisierten Daten
        """
        try:
            kwargs['updated_at'] = datetime.now(timezone.utc).isoformat()
            
            result = self.client.table('clothes').update(kwargs).eq('id', clothing_id).execute()
            self.logger.info(f"Kleidungsstück aktualisiert: {clothing_id}")
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Aktualisieren des Kleidungsstücks: {e}")
            raise
    
    def delete_clothing_item(self, clothing_id: str) -> bool:
        """
        Löscht ein Kleidungsstück
        
        Args:
            clothing_id: UUID des Kleidungsstücks
            
        Returns:
            True wenn erfolgreich
        """
        try:
            self.client.table('clothes').delete().eq('id', clothing_id).execute()
            self.logger.info(f"Kleidungsstück gelöscht: {clothing_id}")
            return True
            
        except APIError as e:
            self.logger.error(f"Fehler beim Löschen des Kleidungsstücks: {e}")
            raise

    # ======================
    # OUTFITS MANAGEMENT
    # ======================
    
    def create_outfit(self, user_id: str, name: str, clothing_ids: List[str],
                     description: str = None, weather_condition: str = None,
                     occasion: str = None, mood: str = None) -> Dict[str, Any]:
        """
        Erstellt ein neues Outfit mit Kleidungsstücken
        
        Args:
            user_id: UUID des Nutzers
            name: Name des Outfits
            clothing_ids: Liste der Kleidungsstück-UUIDs
            description: Beschreibung (optional)
            weather_condition: Wetterbedingung (optional)
            occasion: Anlass (optional)
            mood: Stimmung (optional)
            
        Returns:
            Dict mit Outfit-Daten
        """
        try:
            # Outfit erstellen
            outfit_data = {
                'user_id': user_id,
                'name': name,
                'description': description,
                'weather_condition': weather_condition,
                'occasion': occasion,
                'mood': mood,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            outfit_result = self.client.table('outfits').insert(outfit_data).execute()
            
            if not outfit_result.data:
                raise Exception("Outfit konnte nicht erstellt werden")
            
            outfit = outfit_result.data[0]
            outfit_id = outfit['id']
            
            # Kleidungsstücke zum Outfit hinzufügen
            if clothing_ids:
                self.add_items_to_outfit(outfit_id, clothing_ids)
            
            self.logger.info(f"Outfit erstellt: {outfit_id}")
            return outfit
            
        except APIError as e:
            self.logger.error(f"Fehler beim Erstellen des Outfits: {e}")
            raise
    
    def get_user_outfits(self, user_id: str, include_items: bool = True) -> List[Dict[str, Any]]:
        """
        Holt alle Outfits eines Nutzers
        
        Args:
            user_id: UUID des Nutzers
            include_items: Ob Kleidungsstücke mit geladen werden sollen
            
        Returns:
            Liste mit Outfits
        """
        try:
            result = self.client.table('outfits').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
            outfits = result.data or []
            
            if include_items:
                for outfit in outfits:
                    outfit['items'] = self.get_outfit_items(outfit['id'])
            
            return outfits
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden der Outfits: {e}")
            raise
    
    def get_outfit(self, outfit_id: str, include_items: bool = True) -> Optional[Dict[str, Any]]:
        """
        Holt ein einzelnes Outfit
        
        Args:
            outfit_id: UUID des Outfits
            include_items: Ob Kleidungsstücke mit geladen werden sollen
            
        Returns:
            Dict mit Outfit-Daten oder None
        """
        try:
            result = self.client.table('outfits').select('*').eq('id', outfit_id).execute()
            
            if not result.data:
                return None
            
            outfit = result.data[0]
            
            if include_items:
                outfit['items'] = self.get_outfit_items(outfit_id)
            
            return outfit
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden des Outfits: {e}")
            raise
    
    def update_outfit(self, outfit_id: str, **kwargs) -> Dict[str, Any]:
        """
        Aktualisiert ein Outfit
        
        Args:
            outfit_id: UUID des Outfits
            **kwargs: Felder zum Aktualisieren
            
        Returns:
            Dict mit aktualisierten Daten
        """
        try:
            result = self.client.table('outfits').update(kwargs).eq('id', outfit_id).execute()
            self.logger.info(f"Outfit aktualisiert: {outfit_id}")
            return result.data[0] if result.data else None
            
        except APIError as e:
            self.logger.error(f"Fehler beim Aktualisieren des Outfits: {e}")
            raise
    
    def mark_outfit_as_worn(self, outfit_id: str) -> Dict[str, Any]:
        """
        Markiert ein Outfit als getragen
        
        Args:
            outfit_id: UUID des Outfits
            
        Returns:
            Dict mit aktualisierten Daten
        """
        return self.update_outfit(outfit_id, worn_at=datetime.now(timezone.utc).isoformat())
    
    def delete_outfit(self, outfit_id: str) -> bool:
        """
        Löscht ein Outfit (CASCADE löscht auch outfit_items)
        
        Args:
            outfit_id: UUID des Outfits
            
        Returns:
            True wenn erfolgreich
        """
        try:
            self.client.table('outfits').delete().eq('id', outfit_id).execute()
            self.logger.info(f"Outfit gelöscht: {outfit_id}")
            return True
            
        except APIError as e:
            self.logger.error(f"Fehler beim Löschen des Outfits: {e}")
            raise

    # ======================
    # OUTFIT ITEMS MANAGEMENT
    # ======================
    
    def add_items_to_outfit(self, outfit_id: str, clothing_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Fügt Kleidungsstücke zu einem Outfit hinzu
        
        Args:
            outfit_id: UUID des Outfits
            clothing_ids: Liste der Kleidungsstück-UUIDs
            
        Returns:
            Liste mit erstellten outfit_items
        """
        try:
            items_data = []
            for clothing_id in clothing_ids:
                items_data.append({
                    'outfit_id': outfit_id,
                    'clothing_id': clothing_id,
                    'created_at': datetime.now(timezone.utc).isoformat()
                })
            
            result = self.client.table('outfit_items').insert(items_data).execute()
            self.logger.info(f"{len(clothing_ids)} Kleidungsstücke zu Outfit {outfit_id} hinzugefügt")
            return result.data or []
            
        except APIError as e:
            self.logger.error(f"Fehler beim Hinzufügen der Kleidungsstücke zum Outfit: {e}")
            raise
    
    def get_outfit_items(self, outfit_id: str) -> List[Dict[str, Any]]:
        """
        Holt alle Kleidungsstücke eines Outfits mit detaillierten Informationen
        
        Args:
            outfit_id: UUID des Outfits
            
        Returns:
            Liste mit Kleidungsstücken des Outfits
        """
        try:
            result = self.client.table('outfit_items').select(
                '*, clothes(*)'
            ).eq('outfit_id', outfit_id).execute()
            
            # Extrahiere nur die Kleidungsstück-Daten
            items = []
            for item in result.data or []:
                if item.get('clothes'):
                    items.append(item['clothes'])
            
            return items
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden der Outfit-Kleidungsstücke: {e}")
            raise
    
    def remove_item_from_outfit(self, outfit_id: str, clothing_id: str) -> bool:
        """
        Entfernt ein Kleidungsstück aus einem Outfit
        
        Args:
            outfit_id: UUID des Outfits
            clothing_id: UUID des Kleidungsstücks
            
        Returns:
            True wenn erfolgreich
        """
        try:
            self.client.table('outfit_items').delete().eq('outfit_id', outfit_id).eq('clothing_id', clothing_id).execute()
            self.logger.info(f"Kleidungsstück {clothing_id} aus Outfit {outfit_id} entfernt")
            return True
            
        except APIError as e:
            self.logger.error(f"Fehler beim Entfernen des Kleidungsstücks aus dem Outfit: {e}")
            raise
    
    def update_outfit_items(self, outfit_id: str, clothing_ids: List[str]) -> List[Dict[str, Any]]:
        """
        Ersetzt alle Kleidungsstücke eines Outfits
        
        Args:
            outfit_id: UUID des Outfits
            clothing_ids: Neue Liste der Kleidungsstück-UUIDs
            
        Returns:
            Liste mit neuen outfit_items
        """
        try:
            # Alle bestehenden Items löschen
            self.client.table('outfit_items').delete().eq('outfit_id', outfit_id).execute()
            
            # Neue Items hinzufügen
            if clothing_ids:
                return self.add_items_to_outfit(outfit_id, clothing_ids)
            
            return []
            
        except APIError as e:
            self.logger.error(f"Fehler beim Aktualisieren der Outfit-Kleidungsstücke: {e}")
            raise

    # ======================
    # ANALYTICS & STATISTICS
    # ======================
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """
        Holt Statistiken für einen Nutzer
        
        Args:
            user_id: UUID des Nutzers
            
        Returns:
            Dict mit verschiedenen Statistiken
        """
        try:
            # Anzahl Kleidungsstücke
            clothes_result = self.client.table('clothes').select('id', count='exact').eq('user_id', user_id).execute()
            clothes_count = clothes_result.count or 0
            
            # Anzahl Outfits
            outfits_result = self.client.table('outfits').select('id', count='exact').eq('user_id', user_id).execute()
            outfits_count = outfits_result.count or 0
            
            # Getragene Outfits
            worn_outfits_result = self.client.table('outfits').select('id', count='exact').eq('user_id', user_id).not_.is_('worn_at', 'null').execute()
            worn_outfits_count = worn_outfits_result.count or 0
            
            # Kategorien-Verteilung
            categories_result = self.client.table('clothes').select('category').eq('user_id', user_id).execute()
            categories = {}
            for item in categories_result.data or []:
                category = item['category']
                categories[category] = categories.get(category, 0) + 1
            
            return {
                'total_clothes': clothes_count,
                'total_outfits': outfits_count,
                'worn_outfits': worn_outfits_count,
                'categories_distribution': categories,
                'unworn_outfits': outfits_count - worn_outfits_count
            }
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden der Statistiken: {e}")
            raise

    # ======================
    # SEARCH & FILTERING
    # ======================
    
    def search_outfits(self, user_id: str, query: str = None, 
                      weather_condition: str = None, occasion: str = None,
                      mood: str = None) -> List[Dict[str, Any]]:
        """
        Sucht Outfits nach verschiedenen Kriterien
        
        Args:
            user_id: UUID des Nutzers
            query: Suchbegriff für Name/Beschreibung
            weather_condition: Filter nach Wetterbedingung
            occasion: Filter nach Anlass
            mood: Filter nach Stimmung
            
        Returns:
            Liste mit gefilterten Outfits
        """
        try:
            db_query = self.client.table('outfits').select('*').eq('user_id', user_id)
            
            if query:
                db_query = db_query.or_(f'name.ilike.%{query}%,description.ilike.%{query}%')
            
            if weather_condition:
                db_query = db_query.eq('weather_condition', weather_condition)
                
            if occasion:
                db_query = db_query.eq('occasion', occasion)
                
            if mood:
                db_query = db_query.eq('mood', mood)
            
            result = db_query.order('created_at', desc=True).execute()
            return result.data or []
            
        except APIError as e:
            self.logger.error(f"Fehler bei der Outfit-Suche: {e}")
            raise

    # ======================
    # UTILITY METHODS
    # ======================
    
    def health_check(self) -> bool:
        """
        Überprüft die Datenbankverbindung
        
        Returns:
            True wenn Verbindung funktioniert
        """
        try:
            # Einfache Query zum Testen der Verbindung
            self.client.table('users').select('id').limit(1).execute()
            return True
        except Exception as e:
            self.logger.error(f"Datenbankverbindung fehlgeschlagen: {e}")
            return False
    
    def get_clothing_categories(self, user_id: str) -> List[str]:
        """
        Holt alle verwendeten Kleidungskategorien eines Nutzers
        
        Args:
            user_id: UUID des Nutzers
            
        Returns:
            Liste mit eindeutigen Kategorien
        """
        try:
            result = self.client.table('clothes').select('category').eq('user_id', user_id).execute()
            categories = list(set(item['category'] for item in result.data or [] if item['category']))
            return sorted(categories)
            
        except APIError as e:
            self.logger.error(f"Fehler beim Laden der Kategorien: {e}")
            raise
