# 🚀 Wardroberry AI API - Nur KI-Analyse

## Hauptfunktion: Kleidung analysieren mit KI

### `/analyze-clothing` - Der einzige Endpoint den du brauchst!

**Was passiert automatisch:**
1. ✅ Bild wird validiert (Format, Größe)
2. 🤖 KI analysiert das Kleidungsstück (Kategorie, Farbe, Stil, etc.)
3. 📤 Du bekommst die komplette Analyse zurück

**Kein Upload, keine Datenbank, nur pure KI-Analyse!**

### Beispiel-Request

```bash
curl -X POST "http://localhost:8000/analyze-clothing" \
  -F "file=@mein_tshirt.jpg"
```

### Beispiel-Response

```json
{
  "category": "T-Shirt",
  "color": "blau",
  "style": "casual", 
  "season": "Sommer",
  "material": "Baumwolle",
  "occasion": "Freizeit",
  "confidence": 0.95
}
```

## Weitere Endpoints

### `/health` - API-Status prüfen

```bash
curl "http://localhost:8000/health"
```

### `/docs` - Automatische API-Dokumentation

Öffne im Browser: `http://localhost:8000/docs`

## Workflow für deine App

1. **Nutzer wählt Bild aus** → Frontend
2. **POST zu `/analyze-clothing`** mit nur `file`
3. **Warten auf Response** (kann 10-30 Sekunden dauern wegen KI)
4. **Erfolg!** → Du bekommst die komplette KI-Analyse

## Flutter Integration

```dart
// Nur das Bild senden
var request = http.MultipartRequest(
  'POST',
  Uri.parse('$baseUrl/analyze-clothing'),
);

// Bilddatei hinzufügen
request.files.add(
  await http.MultipartFile.fromPath('file', imageFile.path),
);

// Request senden
var response = await request.send();
var result = await http.Response.fromStream(response);

if (response.statusCode == 200) {
  Map<String, dynamic> analysis = json.decode(result.body);
  
  // Verwende die KI-Analyse
  String category = analysis['category'];
  String color = analysis['color'];
  String style = analysis['style'];
  // etc.
}
```

## Fehlerbehandlung

- **400**: Ungültiges Bild (zu groß, falsches Format)
- **500**: Server-Fehler (KI nicht verfügbar)

## Unterstützte Bildformate

- JPEG, PNG, WebP, GIF
- Max. 10MB
- Min. 1KB

## KI-Kategorien

Die KI erkennt automatisch:
- **Kategorien**: T-Shirt, Hose, Kleid, Jacke, Schuhe, etc.
- **Farben**: schwarz, weiß, blau, rot, bunt, gemustert, etc.
- **Stile**: casual, elegant, sportlich, business, vintage, etc.
- **Saisons**: Frühling, Sommer, Herbst, Winter, Ganzjährig
- **Material**: Baumwolle, Polyester, Leder, etc. (geschätzt)
- **Anlässe**: Alltag, Arbeit, Sport, Ausgehen, etc.
- **Confidence**: 0.0 - 1.0 (Vertrauenswert der Analyse)

## Entfernte Features

❌ **Nicht mehr verfügbar:**
- Supabase Storage Upload
- Datenbank-Speicherung
- User Management
- Outfit-Erstellung
- Statistiken

✅ **Jetzt verfügbar:**
- Nur KI-Analyse
- Schnell und einfach
- Keine Abhängigkeiten
- Perfekt für Frontend-Integration

## Das war's! 🎉

Mit nur einem API-Call bekommst du:
- ✅ Vollständige KI-Analyse
- ✅ Alle Kleidungseigenschaften
- ✅ Confidence-Wert
- ✅ Sofort verwendbar in deiner App

**Perfekt für:** Apps die ihre eigene Datenspeicherung haben und nur die KI-Analyse brauchen! 