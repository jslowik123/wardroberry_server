# 🧪 Wardroberry API Test-Guide

## 🚀 Quick Start

### 1. RLS-Policies für Tests einrichten
```sql
-- In der Supabase SQL-Konsole ausführen:
-- Kopiere den Inhalt von 'supabase_test_policies.sql' und führe ihn aus
```

### 2. API Server starten
```bash
# Terminal 1: API starten
python main.py
```

### 3. Test-Dependencies installieren
```bash
# Terminal 2: Test-Abhängigkeiten installieren
pip install -r test_requirements.txt
```

### 4. Test-Skript ausführen
```bash
# Kompletten Test-Durchlauf starten
python test_api.py
```

## 🛡️ **RLS-Setup für Tests**

### **Warum RLS-Policies für Tests?**
- ✅ **Sicherheit**: Keine Umgehung von Row Level Security
- ✅ **Isoliert**: Test-User können nur ihre eigenen Daten sehen
- ✅ **Produktionsnah**: Tests laufen unter realen Bedingungen

### **Test-User Konfiguration:**
- **Test User ID**: `550e8400-e29b-41d4-a716-446655440001`
- **Test Email**: `test-user@wardroberry-test.com`
- **Email Pattern**: `%@wardroberry-test.%` oder `%@test.wardroberry.%`

### **Policies Setup:**
1. Öffne deine **Supabase Konsole** → **SQL Editor**
2. Kopiere den Inhalt von `supabase_test_policies.sql`
3. Führe das SQL aus
4. Policies sind aktiviert ✅

## 📋 Was wird getestet?

Das Test-Skript führt folgende Tests automatisch durch:

### ✅ **Health Check**
- API-Status überprüfen
- Datenbank-Verbindung testen
- Storage-Verbindung testen
- AI-API-Verbindung testen

### 🛡️ **RLS-Setup Check**
- Test-User-Konfiguration prüfen
- Policy-Hinweise anzeigen

### 👤 **User Management**
- Test-Nutzer erstellen (mit Test-Email-Pattern)

### 📸 **Bild-Upload & AI-Analyse**
- Test-Bild erstellen (oder vorhandenes verwenden)
- **AI-Analyse** (ohne Speicherung)
- **AI-gestützter Upload** (Hauptfunktion):
  - Bild validieren
  - AI-Analyse durchführen
  - Bild in Supabase Storage speichern
  - Kleidungsstück in Datenbank erstellen

### 👕 **Kleidungsstück-Management**
- Kleidungsstücke abrufen
- Filter testen

### 👔 **Outfit-Management**
- AI-gestützte Outfit-Erstellung
- Outfit-Beschreibung generieren

### 📊 **Analytics**
- Nutzer-Statistiken abrufen

## 🖼️ Test-Bilder

### Automatische Test-Bild-Erstellung
Das Skript erstellt automatisch ein einfaches Test-Bild, wenn PIL installiert ist.

### Eigene Test-Bilder verwenden
1. Erstelle Ordner `test_images/`
2. Lege beliebige Bilder hinein (`.jpg`, `.jpeg`, `.png`)
3. Das Skript verwendet automatisch das erste gefundene Bild

## 🔧 Konfiguration

### Environment Variables
Stelle sicher, dass deine `.env` Datei folgende Variablen enthält:
```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_ROLE_KEY=...  # Nicht für RLS-Umgehung, sondern für Storage
```

### Test-Parameter anpassen
In `test_api.py` kannst du anpassen:
```python
class WardroberryAPITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url           # API URL
        self.test_user_id = "550e8400-e29b-41d4-a716-446655440001"  # Test User ID
        self.test_email = "test-user@wardroberry-test.com"  # Test Email (Policy-Pattern)
```

## 📊 Beispiel-Output

```
🧪 Wardroberry API Test-Suite
==================================================
🚀 Wardroberry API Tester gestartet
📍 API URL: http://localhost:8000
👤 Test User ID: 550e8400-e29b-41d4-a716-446655440001
--------------------------------------------------

🏥 Health Check...
✅ API Status: healthy
💾 Database: connected
📁 Storage: connected
🤖 AI: connected

👤 Erstelle Test-Nutzer...
✅ Nutzer erstellt: test-user@wardroberry-test.com

📸 Bereite Test-Bild vor...
✅ Test-Bild erstellt: test_images/test_shirt.jpg

🤖 Teste AI-Analyse (ohne Speicherung)...
✅ AI-Analyse erfolgreich:
   📂 Kategorie: T-Shirt
   🎨 Farbe: blau
   ✨ Stil: casual
   🌤️ Saison: Ganzjährig
   🧵 Material: Baumwolle
   🎯 Anlass: Alltag
   📊 Confidence: 0.85

🚀 Teste AI-gestützten Kleidungs-Upload...
⏳ Upload läuft... (kann 10-30 Sekunden dauern)
✅ Kleidungsstück erfolgreich erstellt:
   🆔 ID: 12345678-1234-1234-1234-123456789abc
   🖼️ Bild URL: https://storage.supabase.co/object/public/clothing...
   📂 Kategorie: T-Shirt
   🎨 Farbe: blau
   ✨ Stil: casual
   🌤️ Saison: Ganzjährig

🤖 AI-Analyse Details:
   📂 AI Kategorie: T-Shirt
   🎨 AI Farbe: blau
   🧵 AI Material: Baumwolle
   📊 AI Confidence: 0.85

👔 Teste AI-Outfit-Erstellung...
✅ Outfit erfolgreich erstellt:
   🆔 ID: 87654321-4321-4321-4321-210987654321
   📝 Name: Test Outfit
   🌤️ Wetter: mild
   🎯 Anlass: Arbeit
   💭 Beschreibung: Ein professionelles Outfit für den Arbeitsalltag...
   👕 Items: 1

📊 Teste Nutzer-Statistiken...
✅ Statistiken:
   👕 Kleidungsstücke: 1
   👔 Outfits: 1
   ✅ Getragene Outfits: 0
   📂 Kategorien: ['T-Shirt']

==================================================
🎉 Test-Durchlauf abgeschlossen!
==================================================
✅ Kleidungsstück erstellt: 12345678-1234-1234-1234-123456789abc
🖼️ Bild gespeichert: https://storage.supabase.co/...
🤖 AI erkannte: T-Shirt (blau)
```

## 🔧 Einzelne Tests ausführen

Du kannst auch einzelne Funktionen testen:

```python
from test_api import WardroberryAPITester

tester = WardroberryAPITester()

# Nur Health Check
tester.check_health()

# Nur AI-Analyse
image_path = Path("mein_bild.jpg")
analysis = tester.test_image_analysis_only(image_path)
```

## 🐛 Troubleshooting

### API läuft nicht
```bash
# Prüfe ob API läuft
curl http://localhost:8000/health
```

### OpenAI API Fehler
- Prüfe `OPENAI_API_KEY` in `.env`
- Prüfe OpenAI Account-Guthaben

### Supabase Fehler
- Prüfe Supabase-Credentials in `.env`
- Prüfe Supabase-Projekt-Status

### Bildprobleme
- Lege eigene Test-Bilder in `test_images/` Ordner
- Unterstützte Formate: `.jpg`, `.jpeg`, `.png`

## 📚 API Dokumentation

Nach dem Start der API sind verfügbar:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🎯 Wichtigste Endpoints für Frontend

### Bild-Upload mit AI-Analyse (Empfohlen)
```bash
POST /clothes-ai
- user_id (form)
- file (file)
- override_* (optional form fields)
```

### Nur AI-Analyse (Preview)
```bash
POST /analyze-clothing
- file (file)
```

### Outfit mit AI-Beschreibung
```bash
POST /outfits-ai
- user_id, name, clothing_ids, weather_condition, occasion, mood (form)
``` 