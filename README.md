# Wardroberry Backend

Asynchroner Upload und Verarbeitung von Kleidungsstücken mit KI-basierter Extraktion und Analyse.

## 🚀 Features

- **Upload Endpoint**: Sofortiger Upload mit Bestätigung
- **Asynchrone Verarbeitung**: Background-Extraktion und AI-Analyse  
- **Status Tracking**: Real-time Status-Updates via Polling
- **Redis Queue**: Robuste Job-Verarbeitung mit Retry-Logik
- **Storage Integration**: Supabase Storage für Originale und verarbeitete Bilder
- **RLS Security**: Row Level Security für Multi-User Support

## 📁 Struktur

```
├── main.py              # FastAPI Server
├── worker.py            # Asynchroner Worker
├── queue_manager.py     # Redis Queue Management  
├── storage_manager.py   # Supabase Storage Integration
├── database_manager.py  # Database Operations
├── ai.py               # KI-Extraktion und Analyse
├── docker-compose.yml  # Redis Setup
└── SETUP.md           # Detaillierte Setup-Anleitung
```

## 🔧 Quick Start

```bash
# 1. Redis starten
docker-compose up redis -d

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Worker starten (separates Terminal)
python worker.py

# 4. API starten
python main.py
```

## 📡 API Endpoints

- `POST /upload-clothing` - Kleidungsstück hochladen
- `GET /clothing/{id}/status` - Status abfragen
- `GET /queue/stats` - Queue-Statistiken
- `GET /health` - Health Check

## 🔄 Workflow

1. **Upload** → Sofortige Bestätigung mit ID
2. **Queue** → Job wird zur Redis-Queue hinzugefügt
3. **Worker** → Asynchrone Verarbeitung (Extraktion + Analyse)
4. **Polling** → Frontend fragt Status ab bis `completed`

## 📋 Setup

Siehe `SETUP.md` für detaillierte Anweisungen zu:
- Environment Variables
- Database Migration  
- Storage Buckets
- RLS Policies

## 🛠️ Development

```bash
# API mit Auto-Reload
uvicorn main:app --reload

# Worker mit Debug-Logs
python worker.py

# API Dokumentation
http://localhost:8000/docs
``` 