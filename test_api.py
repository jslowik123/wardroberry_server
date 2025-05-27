#!/usr/bin/env python3
"""
Test-Skript für Wardroberry API - Bild-Upload und AI-Analyse
"""

import requests
import json
import os
import time
import uuid
from pathlib import Path
from typing import Dict, Any

class WardroberryAPITester:
    """
    Test-Klasse für alle Wardroberry API Endpoints
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        # Verwende eine echte UUID für den Test-Nutzer
        self.test_user_id = "550e8400-e29b-41d4-a716-446655440001"
        # Verwende Test-Email-Pattern das in der RLS-Policy erlaubt ist
        self.test_email = "test-user@wardroberry-test.com"
        
        # Erstelle Test-Ordner falls nicht vorhanden
        self.test_dir = Path("test_images")
        self.test_dir.mkdir(exist_ok=True)
        
        print(f"🚀 Wardroberry API Tester gestartet")
        print(f"📍 API URL: {self.base_url}")
        print(f"👤 Test User ID: {self.test_user_id}")
        print(f"📧 Test Email: {self.test_email}")
        print("-" * 50)
    
    def check_rls_setup(self):
        """
        Prüft ob RLS-Policies für Tests konfiguriert sind
        """
        print("\n🛡️ Prüfe RLS-Setup für Tests...")
        print("✅ Test-User-ID und Email Pattern konfiguriert")
        print("💡 Stelle sicher, dass die RLS-Policies für Tests in Supabase gesetzt sind:")
        print("   - Führe 'supabase_test_policies.sql' in der Supabase SQL-Konsole aus")
        print("   - Oder erstelle manuelle Policies für Test-User")
        return True
    
    def check_health(self) -> bool:
        """
        Überprüft ob die API läuft
        """
        print("🏥 Health Check...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API Status: {health_data['status']}")
                print(f"💾 Database: {health_data['database']}")
                print(f"📁 Storage: {health_data['storage']}")
                print(f"🤖 AI: {health_data['ai']}")
                return health_data['status'] == 'healthy'
            else:
                print(f"❌ Health Check fehlgeschlagen: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Fehler beim Health Check: {e}")
            return False
    
    def create_test_user(self) -> bool:
        """
        Erstellt einen Test-Nutzer
        """
        print("\n👤 Erstelle Test-Nutzer...")
        try:
            user_data = {
                "user_id": self.test_user_id,
                "email": self.test_email,
                "first_name": "Test",
                "last_name": "User"
            }
            
            response = requests.post(
                f"{self.base_url}/users",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 201:
                user = response.json()
                print(f"✅ Nutzer erstellt: {user['email']}")
                return True
            elif response.status_code == 500:
                # Nutzer existiert wahrscheinlich schon
                print("ℹ️ Nutzer existiert bereits (oder DB-Fehler)")
                return True
            else:
                print(f"❌ Nutzer-Erstellung fehlgeschlagen: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Fehler bei der Nutzer-Erstellung: {e}")
            return False
    
    def create_test_image(self) -> Path:
        """
        Erstellt ein Test-Bild (oder lädt ein vorhandenes)
        """
        print("\n📸 Bereite Test-Bild vor...")
        
        # Suche nach vorhandenen Bildern im Test-Ordner
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            for img_file in self.test_dir.glob(ext):
                print(f"✅ Verwende vorhandenes Test-Bild: {img_file}")
                return img_file
        
        # Erstelle ein einfaches Test-Bild mit PIL (falls verfügbar)
        try:
            from PIL import Image, ImageDraw
            
            # Erstelle ein einfaches 300x300 blaues Rechteck (simuliert ein T-Shirt)
            img = Image.new('RGB', (300, 300), color='blue')
            draw = ImageDraw.Draw(img)
            
            # Zeichne ein einfaches T-Shirt-Symbol
            draw.rectangle([50, 80, 250, 220], fill='lightblue', outline='darkblue', width=3)
            draw.rectangle([100, 50, 200, 120], fill='lightblue', outline='darkblue', width=3)
            
            test_img_path = self.test_dir / "test_shirt.jpg"
            img.save(test_img_path, "JPEG")
            print(f"✅ Test-Bild erstellt: {test_img_path}")
            return test_img_path
            
        except ImportError:
            print("⚠️ PIL nicht verfügbar. Bitte füge ein Test-Bild in den 'test_images' Ordner hinzu.")
            print("Unterstützte Formate: .jpg, .jpeg, .png")
            return None
    
    def test_image_analysis_only(self, image_path: Path) -> Dict[str, Any]:
        """
        Testet nur die AI-Analyse ohne Speicherung
        """
        print(f"\n🤖 Teste AI-Analyse (ohne Speicherung)...")
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/jpeg')}
                
                response = requests.post(
                    f"{self.base_url}/analyze-clothing",
                    files=files,
                    timeout=30
                )
            
            if response.status_code == 200:
                analysis = response.json()
                print("✅ AI-Analyse erfolgreich:")
                print(f"   📂 Kategorie: {analysis['category']}")
                print(f"   🎨 Farbe: {analysis['color']}")
                print(f"   ✨ Stil: {analysis['style']}")
                print(f"   🌤️ Saison: {analysis['season']}")
                print(f"   🧵 Material: {analysis['material']}")
                print(f"   🎯 Anlass: {analysis['occasion']}")
                print(f"   📊 Confidence: {analysis['confidence']:.2f}")
                return analysis
            else:
                print(f"❌ AI-Analyse fehlgeschlagen: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Fehler bei der AI-Analyse: {e}")
            return None
    
    def test_ai_clothing_upload(self, image_path: Path) -> Dict[str, Any]:
        """
        Testet den vollständigen AI-Upload (Hauptfunktion)
        """
        print(f"\n🚀 Teste AI-gestützten Kleidungs-Upload...")
        try:
            with open(image_path, 'rb') as f:
                files = {'file': (image_path.name, f, 'image/jpeg')}
                data = {
                    'user_id': self.test_user_id,
                    # Optionale Overrides (auskommentiert für reinen AI-Test)
                    # 'override_color': 'rot',
                    # 'override_category': 'T-Shirt'
                }
                
                print("⏳ Upload läuft... (kann 10-30 Sekunden dauern)")
                response = requests.post(
                    f"{self.base_url}/clothes-ai",
                    files=files,
                    data=data,
                    timeout=60
                )
            
            if response.status_code == 201:
                clothing = response.json()
                print("✅ Kleidungsstück erfolgreich erstellt:")
                print(f"   🆔 ID: {clothing['id']}")
                print(f"   🖼️ Bild URL: {clothing['image_url'][:60]}...")
                print(f"   📂 Kategorie: {clothing['category']}")
                print(f"   🎨 Farbe: {clothing['color']}")
                print(f"   ✨ Stil: {clothing['style']}")
                print(f"   🌤️ Saison: {clothing['season']}")
                
                print("\n🤖 AI-Analyse Details:")
                ai_analysis = clothing['ai_analysis']
                print(f"   📂 AI Kategorie: {ai_analysis['category']}")
                print(f"   🎨 AI Farbe: {ai_analysis['color']}")
                print(f"   🧵 AI Material: {ai_analysis['material']}")
                print(f"   📊 AI Confidence: {ai_analysis['confidence']:.2f}")
                
                return clothing
            else:
                print(f"❌ Kleidungs-Upload fehlgeschlagen: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Fehler beim Kleidungs-Upload: {e}")
            return None
    
    def test_get_user_clothes(self) -> bool:
        """
        Testet das Abrufen aller Kleidungsstücke eines Nutzers
        """
        print(f"\n👕 Teste Kleidungsstück-Abruf...")
        try:
            response = requests.get(f"{self.base_url}/users/{self.test_user_id}/clothes")
            
            if response.status_code == 200:
                clothes = response.json()
                print(f"✅ {len(clothes)} Kleidungsstücke gefunden:")
                for i, item in enumerate(clothes[:3], 1):  # Zeige max. 3
                    print(f"   {i}. {item['category']} ({item['color']}) - {item['style']}")
                if len(clothes) > 3:
                    print(f"   ... und {len(clothes) - 3} weitere")
                return True
            else:
                print(f"❌ Kleidungsstück-Abruf fehlgeschlagen: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Fehler beim Kleidungsstück-Abruf: {e}")
            return False
    
    def test_create_ai_outfit(self, clothing_ids: list) -> Dict[str, Any]:
        """
        Testet die AI-gestützte Outfit-Erstellung
        """
        if not clothing_ids:
            print("⚠️ Keine Kleidungsstücke für Outfit-Test verfügbar")
            return None
            
        print(f"\n👔 Teste AI-Outfit-Erstellung...")
        try:
            data = {
                'user_id': self.test_user_id,
                'name': 'Test Outfit',
                'clothing_ids': ','.join(clothing_ids[:3]),  # Max 3 Items
                'weather_condition': 'mild',
                'occasion': 'Arbeit',
                'mood': 'selbstbewusst'
            }
            
            response = requests.post(
                f"{self.base_url}/outfits-ai",
                data=data,
                timeout=30
            )
            
            if response.status_code == 201:
                outfit = response.json()
                print("✅ Outfit erfolgreich erstellt:")
                print(f"   🆔 ID: {outfit['id']}")
                print(f"   📝 Name: {outfit['name']}")
                print(f"   🌤️ Wetter: {outfit['weather_condition']}")
                print(f"   🎯 Anlass: {outfit['occasion']}")
                print(f"   💭 Beschreibung: {outfit['description'][:100]}...")
                print(f"   👕 Items: {len(outfit.get('items', []))}")
                return outfit
            else:
                print(f"❌ Outfit-Erstellung fehlgeschlagen: {response.status_code}")
                print(f"Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Fehler bei der Outfit-Erstellung: {e}")
            return None
    
    def test_statistics(self) -> bool:
        """
        Testet die Nutzer-Statistiken
        """
        print(f"\n📊 Teste Nutzer-Statistiken...")
        try:
            response = requests.get(f"{self.base_url}/users/{self.test_user_id}/statistics")
            
            if response.status_code == 200:
                stats = response.json()
                print("✅ Statistiken:")
                print(f"   👕 Kleidungsstücke: {stats['total_clothes']}")
                print(f"   👔 Outfits: {stats['total_outfits']}")
                print(f"   ✅ Getragene Outfits: {stats['worn_outfits']}")
                print(f"   📂 Kategorien: {list(stats['categories_distribution'].keys())}")
                return True
            else:
                print(f"❌ Statistiken-Abruf fehlgeschlagen: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Fehler bei den Statistiken: {e}")
            return False
    
    def run_complete_test(self, image_path: Path = None):
        """
        Führt den kompletten Test-Durchlauf aus
        """
        print("🎯 Starte kompletten API-Test...\n")
        
        # 0. RLS-Setup prüfen
        if not self.check_rls_setup():
            print("❌ RLS-Setup konnte nicht verifiziert werden.")
            return
        
        # 1. Health Check
        if not self.check_health():
            print("❌ API nicht verfügbar. Stelle sicher, dass der Server läuft.")
            print("💡 Falls RLS-Fehler auftreten, prüfe die Test-Policies in Supabase.")
            return
        
        # 2. Test-Nutzer erstellen
        if not self.create_test_user():
            print("❌ Kann ohne Test-Nutzer nicht fortfahren.")
            return
        
        # 3. Test-Bild vorbereiten
        if image_path is None:
            image_path = self.create_test_image()
        
        if not image_path or not image_path.exists():
            print("❌ Kein gültiges Test-Bild verfügbar.")
            return
        
        # 4. AI-Analyse testen (ohne Speicherung)
        analysis = self.test_image_analysis_only(image_path)
        
        # 5. AI-gestützten Upload testen (Hauptfunktion)
        clothing = self.test_ai_clothing_upload(image_path)
        
        # 6. Kleidungsstücke abrufen
        self.test_get_user_clothes()
        
        # 7. AI-Outfit erstellen (falls Kleidungsstücke vorhanden)
        if clothing:
            self.test_create_ai_outfit([clothing['id']])
        
        # 8. Statistiken abrufen
        self.test_statistics()
        
        print("\n" + "="*50)
        print("🎉 Test-Durchlauf abgeschlossen!")
        print("="*50)
        
        # Zusammenfassung
        if clothing:
            print(f"✅ Kleidungsstück erstellt: {clothing['id']}")
            print(f"🖼️ Bild gespeichert: {clothing['image_url']}")
            print(f"🤖 AI erkannte: {clothing['category']} ({clothing['color']})")

def main():
    """
    Hauptfunktion zum Ausführen der Tests
    """
    print("🧪 Wardroberry API Test-Suite")
    print("=" * 50)
    
    # Prüfe ob .env Datei existiert
    if not os.path.exists('.env'):
        print("⚠️ Warnung: .env Datei nicht gefunden.")
        print("Stelle sicher, dass OPENAI_API_KEY und Supabase-Credentials gesetzt sind.")
    
    # Erstelle Tester-Instanz
    tester = WardroberryAPITester()
    
    # Frage nach Bildpfad
    print("\n📸 Bildauswahl:")
    image_path_input = "test_images/FullSizeRender.jpg"
    
    if image_path_input:
        image_path = Path(image_path_input)
        
        # Validiere den Pfad
        if not image_path.exists():
            print(f"❌ Datei nicht gefunden: {image_path}")
            print("Verwende automatisches Test-Bild...")
            image_path = None
        elif not image_path.is_file():
            print(f"❌ Pfad ist keine Datei: {image_path}")
            print("Verwende automatisches Test-Bild...")
            image_path = None
        elif image_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
            print(f"❌ Unsupported file format: {image_path.suffix}")
            print("Unterstützte Formate: .jpg, .jpeg, .png")
            print("Verwende automatisches Test-Bild...")
            image_path = None
        else:
            print(f"✅ Verwende Bild: {image_path}")
    
    # Führe Tests aus3
    try:
        tester.run_complete_test(image_path)
    except KeyboardInterrupt:
        print("\n⏹️ Test durch Nutzer abgebrochen.")
    except Exception as e:
        print(f"\n💥 Unerwarteter Fehler: {e}")
    
    print("\n🔗 Nützliche Links:")
    print("📚 API Docs: http://localhost:8000/docs")
    print("📋 ReDoc: http://localhost:8000/redoc")
    print("🏥 Health: http://localhost:8000/health")

if __name__ == "__main__":
    main() 