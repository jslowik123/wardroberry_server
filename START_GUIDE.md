# 🚀 Wardroberry Daily Startup Guide

## Vor dem ersten Start (einmalig):

### 1. Docker Desktop starten
- Docker Desktop App öffnen und warten bis grüner Status
- Oder im Terminal: `open /Applications/Docker.app`

### 2. Environment Setup
```bash
# In Ihrem Projekt-Ordner
cd /Users/jasperslowik/Cursor/wardroberry_server
source .venv/bin/activate  # Virtual Environment aktivieren
```

---

## 🎯 Täglicher Start (Empfohlene Methode):

### Schritt 1: Redis starten
```bash
docker compose up -d redis
```
✅ **Ergebnis**: Redis läuft im Hintergrund

### Schritt 2: API starten (Terminal 1)
```bash
python main.py
```
✅ **Ergebnis**: API läuft auf http://localhost:8000

### Schritt 3: Worker starten (Terminal 2 - neues Terminal öffnen)
```bash
cd /Users/jasperslowik/Cursor/wardroberry_server
source .venv/bin/activate
python worker.py
```
✅ **Ergebnis**: Worker verarbeitet Jobs aus Redis Queue

---

## 🔍 System Status überprüfen:

### Laufende Container anzeigen:
```bash
docker ps
```

### API testen:
```bash
curl http://localhost:8000/health
```
Antwort sollte sein: `{"status": "healthy", "message": "API is running"}`

### Queue Status:
```bash
curl http://localhost:8000/queue/stats
```

---

## 🛑 System stoppen:

### Redis stoppen:
```bash
docker compose down
```

### API/Worker stoppen:
- `Ctrl+C` in den jeweiligen Terminals

---

## 🔄 Alternative: Alles mit Docker

### Alles starten:
```bash
docker compose --profile full up -d
```

### Logs anschauen:
```bash
# Alle Services
docker compose logs -f

# Nur API
docker compose logs -f api

# Nur Worker  
docker compose logs -f worker
```

### Alles stoppen:
```bash
docker compose --profile full down
```

---

## 🆘 Troubleshooting:

### Redis läuft nicht?
```bash
docker compose restart redis
```

### Container neu bauen (nach Code-Änderungen):
```bash
docker compose build
docker compose --profile full up -d
```

### Alle Container und Volumes löschen (Neustart):
```bash
docker compose down -v
docker system prune -f
```

---

## 📱 Quick Commands für jeden Tag:

```bash
# 1. Docker Desktop starten (falls nicht läuft)
open /Applications/Docker.app

# 2. Zum Projekt navigieren + venv aktivieren
cd /Users/jasperslowik/Cursor/wardroberry_server && source .venv/bin/activate

# 3. Redis starten
docker compose up -d redis

# 4. API starten (in diesem Terminal)
python main.py

# 5. Worker starten (neues Terminal)
# Terminal 2: cd /Users/jasperslowik/Cursor/wardroberry_server && source .venv/bin/activate && python worker.py
```

**🎯 Das war's! Ihr Wardroberry-System läuft jetzt!** 