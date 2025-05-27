from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from dotenv import load_dotenv
import base64
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from storage_manager import StorageManager
from ai import ClothingAI

# FastAPI App Setup
app = FastAPI(
    title="Wardroberry AI API",
    description="KI-Analyse API für Kleidungsstücke - Nur Bildanalyse ohne Speicherung",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In Produktion spezifische Origins verwenden
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dependencies
def get_storage_manager() -> StorageManager:
    """Dependency für StorageManager (nur Validierung)"""
    return StorageManager()

def get_clothing_ai() -> ClothingAI:
    """Dependency für ClothingAI"""
    return ClothingAI()

# ======================
# PYDANTIC MODELS
# ======================

# AI-Enhanced Response Models
class AIAnalysisResponse(BaseModel):
    category: str
    color: str
    style: str
    season: str
    material: str
    occasion: str
    confidence: float

# ======================
# HAUPTFUNKTION: NUR KI-ANALYSE
# ======================

@app.post("/analyze-clothing", response_model=AIAnalysisResponse)
async def analyze_clothing_image(
    file: UploadFile = File(..., description="Bilddatei des Kleidungsstücks"),
    ai: ClothingAI = Depends(get_clothing_ai),
    storage: StorageManager = Depends(get_storage_manager)
):
    """
    🚀 **HAUPTFUNKTION**: Bild analysieren → KI-Ergebnis zurückgeben
    
    **Einfacher Workflow:**
    1. ✅ Bild validieren (Größe, Format)
    2. 🤖 KI-Analyse durchführen (Kategorie, Farbe, Stil, Saison, Material, Anlass)
    3. 📤 Analyseergebnis zurückgeben
    
    **Eingabe:** Nur `file` erforderlich
    
    **Ausgabe:** Vollständige KI-Analyse mit:
    - Kategorie (T-Shirt, Hose, etc.)
    - Farbe (blau, rot, etc.)
    - Stil (casual, elegant, etc.)
    - Saison (Sommer, Winter, etc.)
    - Material (Baumwolle, Polyester, etc.)
    - Anlass (Alltag, Arbeit, etc.)
    - Confidence (0.0 - 1.0)
    
    **Beispiel-Request:**
    ```
    POST /analyze-clothing
    Content-Type: multipart/form-data
    
    file: [Bilddatei]
    ```
    
    **Beispiel-Response:**
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
    """
    try:
        # 1. Datei-Validierung
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_message = storage.validate_image_file(file.content_type, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        logger.info(f"🤖 Starte KI-Analyse für Bild: {file.filename}")
        
        # 2. KI-Analyse durchführen
        ai_analysis = ai.analyze_clothing_image(file_content)
        
        logger.info(f"✅ KI-Analyse abgeschlossen")
        logger.info(f"🎯 Erkannt: {ai_analysis['category']} ({ai_analysis['color']}, {ai_analysis['style']})")
        
        return AIAnalysisResponse(**ai_analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler bei der KI-Analyse: {e}")
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")

# ======================
# HEALTH CHECK
# ======================

@app.get("/health")
async def health_check(
    storage: StorageManager = Depends(get_storage_manager),
    ai: ClothingAI = Depends(get_clothing_ai)
):
    """Überprüft die API und KI-Verbindung"""
    try:
        storage_healthy = storage.health_check()
        ai_healthy = ai.health_check()
        
        overall_status = "healthy" if (storage_healthy and ai_healthy) else "unhealthy"
        
        return {
            "status": overall_status,
            "storage": "connected" if storage_healthy else "disconnected",
            "ai": "connected" if ai_healthy else "disconnected",
            "timestamp": datetime.now().isoformat(),
            "message": "KI-Analyse Service bereit" if overall_status == "healthy" else "Service nicht verfügbar"
        }
    except Exception as e:
        logger.error(f"Health Check Fehler: {e}")
        return {
            "status": "unhealthy",
            "storage": "error",
            "ai": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ======================
# STARTUP EVENT
# ======================

@app.on_event("startup")
async def startup_event():
    """Startup Event für Initialisierung"""
    logger.info("🚀 Wardroberry AI API gestartet")
    logger.info("📋 Verfügbare Endpoints:")
    logger.info("  POST /analyze-clothing - Hauptfunktion: KI-Analyse")
    logger.info("  GET  /health - Health Check")
    logger.info("  GET  /docs - API Dokumentation")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)