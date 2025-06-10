# Wardroberry Backend Setup - Asynchronous Processing

## 🚀 Quick Start

Die Wardroberry API bietet einen asynchronen Workflow für Kleidungsstück-Verarbeitung:

1. **Upload** → Sofortige Bestätigung mit ID
2. **Background Processing** → Extraktion + AI-Analyse
3. **Status Polling** → Frontend kann Fortschritt verfolgen

## 📋 Setup Checklist

### 1. Environment Variables

Stellen Sie sicher, dass diese Variablen in Ihrer `.env` Datei gesetzt sind:

```env
# Supabase
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Redis Queue
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
MAX_RETRIES=3
```

### 2. Database Migration

Führen Sie das SQL-Script aus:

```bash
# Kopieren Sie den Inhalt von database_migration.sql
# Fügen Sie ihn in die Supabase SQL-Konsole ein
```

### 3. Storage Buckets

Erstellen Sie in Supabase diese Storage Buckets:

- `clothing-images-original` - Für ursprüngliche Uploads
- `clothing-images-processed` - Für extrahierte/verarbeitete Bilder

### 4. RLS Policies

Setzen Sie Row Level Security Policies für die Buckets:

```sql
-- Policy für original images
CREATE POLICY "Users can upload their own images" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'clothing-images-original' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view their own images" ON storage.objects
FOR SELECT USING (bucket_id = 'clothing-images-original' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Policy für processed images  
CREATE POLICY "Users can upload processed images" ON storage.objects
FOR INSERT WITH CHECK (bucket_id = 'clothing-images-processed' AND auth.uid()::text = (storage.foldername(name))[1]);

CREATE POLICY "Users can view processed images" ON storage.objects
FOR SELECT USING (bucket_id = 'clothing-images-processed' AND auth.uid()::text = (storage.foldername(name))[1]);
```

## 🔧 Installation

### Option 1: Lokal mit Redis

```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. Redis starten (mit Docker)
docker-compose up redis -d

# 3. Worker starten (separates Terminal)
python worker.py

# 4. API Server starten
python main.py
```

### Option 2: Docker Compose (Alles zusammen)

```bash
# Komplettes System starten
docker-compose --profile full up -d

# Logs anschauen
docker-compose logs -f worker
docker-compose logs -f api
```

### Option 3: Nur Redis + Worker

```bash
# Redis und Worker starten
docker-compose up redis worker -d

# API lokal starten
python main.py
```

## 📡 API Endpoints

### Upload Workflow

#### 1. Upload Kleidungsstück
```http
POST /upload-clothing
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data

file: <image_file>
```

**Response:**
```json
{
  "id": "clothing-uuid",
  "status": "pending",
  "message": "Kleidungsstück empfangen! Verarbeitung läuft im Hintergrund.",
  "created_at": "2024-01-01T12:00:00Z"
}
```

#### 2. Status abfragen
```http
GET /clothing/{clothing_id}/status
Authorization: Bearer <jwt_token>
```

**Response (Processing):**
```json
{
  "id": "clothing-uuid",
  "status": "processing",
  "category": "Wird analysiert...",
  "updated_at": "2024-01-01T12:00:30Z"
}
```

**Response (Completed):**
```json
{
  "id": "clothing-uuid",
  "status": "completed",
  "category": "T-Shirt",
  "color": "blau",
  "style": "casual",
  "season": "Sommer",
  "material": "Baumwolle",
  "occasion": "Freizeit",
  "confidence": 0.95,
  "image_url": "https://...",
  "extracted_image_url": "https://...",
  "updated_at": "2024-01-01T12:01:00Z"
}
```

#### 3. Queue-Statistiken
```http
GET /queue/stats
```

#### 4. Health Check
```http
GET /health
```

## 💻 Frontend Integration

### Upload Flow

```javascript
// 1. Upload Kleidungsstück
const uploadResponse = await fetch('/upload-clothing', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const { id } = await uploadResponse.json();

// 2. Status-Polling
const pollStatus = async () => {
  const response = await fetch(`/clothing/${id}/status`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const status = await response.json();
  
  if (status.status === 'completed') {
    // Verarbeitung abgeschlossen
    showCompletedClothing(status);
  } else if (status.status === 'failed') {
    // Fehler aufgetreten
    showError(status.processing_error);
  } else {
    // Noch in Bearbeitung - weiter pollen
    setTimeout(pollStatus, 2000);
  }
};

pollStatus();
```

## 🔍 Status Codes

- `pending` - Wartet auf Verarbeitung
- `processing` - Wird gerade verarbeitet
- `completed` - Erfolgreich abgeschlossen
- `failed` - Fehler aufgetreten

## 🚨 Troubleshooting

### Häufige Probleme

1. **401 Unauthorized**
   - JWT-Token fehlt oder ungültig
   - Prüfen Sie den Authorization Header

2. **Storage Errors**
   - Buckets nicht erstellt
   - RLS Policies fehlen

3. **Database Errors**
   - Migration nicht ausgeführt
   - Supabase-Verbindung fehlt

4. **Queue Errors**
   - Redis nicht gestartet
   - Worker nicht aktiv

### Logs

Aktivieren Sie Debug-Logging:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Monitoring

```http
GET /health
```

Überprüft Storage, Database, Queue und gibt Queue-Statistiken zurück.

```http
GET /queue/stats
```

Zeigt aktuelle Queue-Statistiken (Anzahl wartender Jobs).

## 🛠️ Development

```bash
# Server mit Auto-Reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# API Dokumentation
# http://localhost:8000/docs
``` 