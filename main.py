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
from database_manager import DatabaseManager
from storage_manager import StorageManager
from ai import ClothingAI

# FastAPI App Setup
app = FastAPI(
    title="Wardroberry API",
    description="API für die Wardroberry Kleiderschrank-App",
    version="1.0.0"
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
def get_database_manager() -> DatabaseManager:
    """Dependency für DatabaseManager"""
    return DatabaseManager()

def get_storage_manager() -> StorageManager:
    """Dependency für StorageManager"""
    return StorageManager()

def get_clothing_ai() -> ClothingAI:
    """Dependency für ClothingAI"""
    return ClothingAI()

# ======================
# PYDANTIC MODELS
# ======================

# User Models
class UserCreate(BaseModel):
    user_id: str = Field(..., description="UUID des Nutzers aus Supabase Auth")
    email: str = Field(..., description="E-Mail-Adresse")
    first_name: Optional[str] = Field(None, description="Vorname")
    last_name: Optional[str] = Field(None, description="Nachname")

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    created_at: str
    updated_at: str

# Clothing Models
class ClothingCreate(BaseModel):
    user_id: str = Field(..., description="UUID des Nutzers")
    image_url: str = Field(..., description="URL zum Bild in Supabase Storage")
    category: str = Field(..., description="Kategorie des Kleidungsstücks")
    color: Optional[str] = Field(None, description="Hauptfarbe")
    style: Optional[str] = Field(None, description="Stil")
    season: Optional[str] = Field(None, description="Saison")

class ClothingCreateWithImage(BaseModel):
    user_id: str = Field(..., description="UUID des Nutzers")
    category: str = Field(..., description="Kategorie des Kleidungsstücks")
    color: Optional[str] = Field(None, description="Hauptfarbe")
    style: Optional[str] = Field(None, description="Stil")
    season: Optional[str] = Field(None, description="Saison")

class ClothingUpdate(BaseModel):
    category: Optional[str] = None
    color: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None

class ClothingResponse(BaseModel):
    id: str
    user_id: str
    image_url: str
    category: str
    color: Optional[str]
    style: Optional[str]
    season: Optional[str]
    created_at: str
    updated_at: str

# AI-Enhanced Response Models
class AIAnalysisResponse(BaseModel):
    category: str
    color: str
    style: str
    season: str
    material: str
    occasion: str
    confidence: float

class ClothingAIResponse(ClothingResponse):
    ai_analysis: AIAnalysisResponse

# File Upload Models
class ImageUploadResponse(BaseModel):
    image_url: str
    message: str

# Outfit Models
class OutfitCreate(BaseModel):
    user_id: str = Field(..., description="UUID des Nutzers")
    name: str = Field(..., description="Name des Outfits")
    clothing_ids: List[str] = Field(..., description="Liste der Kleidungsstück-UUIDs")
    description: Optional[str] = Field(None, description="Beschreibung")
    weather_condition: Optional[str] = Field(None, description="Wetterbedingung")
    occasion: Optional[str] = Field(None, description="Anlass")
    mood: Optional[str] = Field(None, description="Stimmung")

class OutfitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    weather_condition: Optional[str] = None
    occasion: Optional[str] = None
    mood: Optional[str] = None

class OutfitResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str]
    weather_condition: Optional[str]
    occasion: Optional[str]
    mood: Optional[str]
    created_at: str
    worn_at: Optional[str]
    items: Optional[List[ClothingResponse]] = None

# Statistics Model
class UserStatistics(BaseModel):
    total_clothes: int
    total_outfits: int
    worn_outfits: int
    unworn_outfits: int
    categories_distribution: Dict[str, int]

# ======================
# AI-POWERED CLOTHING ANALYSIS
# ======================

@app.post("/analyze-clothing", response_model=AIAnalysisResponse)
async def analyze_clothing_image(
    file: UploadFile = File(..., description="Bilddatei zum Analysieren"),
    ai: ClothingAI = Depends(get_clothing_ai),
    storage: StorageManager = Depends(get_storage_manager)
):
    """
    Analysiert ein Kleidungsstück-Bild mit AI (ohne Speicherung)
    """
    try:
        # Datei-Validierung
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_message = storage.validate_image_file(file.content_type, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # AI-Analyse
        analysis = ai.analyze_clothing_image(file_content)
        
        return AIAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei der AI-Analyse: {e}")
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")

@app.post("/clothes-ai", response_model=ClothingAIResponse, status_code=status.HTTP_201_CREATED)
async def add_clothing_with_ai_analysis(
    user_id: str = Form(..., description="UUID des Nutzers"),
    file: UploadFile = File(..., description="Bilddatei"),
    override_category: Optional[str] = Form(None, description="Kategorie überschreiben"),
    override_color: Optional[str] = Form(None, description="Farbe überschreiben"),
    override_style: Optional[str] = Form(None, description="Stil überschreiben"),
    override_season: Optional[str] = Form(None, description="Saison überschreiben"),
    db: DatabaseManager = Depends(get_database_manager),
    storage: StorageManager = Depends(get_storage_manager),
    ai: ClothingAI = Depends(get_clothing_ai)
):
    """
    Intelligente Kleidungsstück-Erstellung mit AI-Analyse:
    1. Bild hochladen
    2. AI-Analyse durchführen
    3. Kleidungsstück in DB speichern
    4. Vollständige Informationen zurückgeben
    """
    try:
        # 1. Datei-Validierung
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_message = storage.validate_image_file(file.content_type, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # 2. AI-Analyse durchführen
        logger.info(f"Starte AI-Analyse für Nutzer: {user_id}")
        ai_analysis = ai.analyze_clothing_image(file_content)
        
        # 3. Bild hochladen
        image_url = storage.upload_clothing_image(
            user_id=user_id,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # 4. Override-Parameter anwenden (falls vom User gewünscht)
        final_category = override_category or ai_analysis["category"]
        final_color = override_color or ai_analysis["color"]
        final_style = override_style or ai_analysis["style"]
        final_season = override_season or ai_analysis["season"]
        
        # 5. Kleidungsstück in Datenbank erstellen
        clothing = db.add_clothing_item(
            user_id=user_id,
            image_url=image_url,
            category=final_category,
            color=final_color,
            style=final_style,
            season=final_season
        )
        
        if not clothing:
            # Falls DB-Erstellung fehlschlägt, Bild wieder löschen
            storage.delete_clothing_image(image_url)
            raise HTTPException(status_code=400, detail="Kleidungsstück konnte nicht erstellt werden")
        
        # 6. Response mit AI-Analyse-Details
        response = ClothingAIResponse(
            **clothing,
            ai_analysis=AIAnalysisResponse(**ai_analysis)
        )
        
        logger.info(f"Kleidungsstück mit AI-Analyse erstellt: {clothing['id']}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei der AI-gestützten Kleidungserstellung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/outfits-ai", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
async def create_outfit_with_ai_description(
    user_id: str = Form(..., description="UUID des Nutzers"),
    name: str = Form(..., description="Name des Outfits"),
    clothing_ids: str = Form(..., description="Komma-getrennte Liste der Kleidungsstück-UUIDs"),
    weather_condition: Optional[str] = Form(None, description="Wetterbedingung"),
    occasion: Optional[str] = Form(None, description="Anlass"),
    mood: Optional[str] = Form(None, description="Stimmung"),
    db: DatabaseManager = Depends(get_database_manager),
    ai: ClothingAI = Depends(get_clothing_ai)
):
    """
    Erstellt ein Outfit mit AI-generierter Beschreibung
    """
    try:
        # Clothing IDs parsen
        clothing_id_list = [id.strip() for id in clothing_ids.split(",") if id.strip()]
        
        if not clothing_id_list:
            raise HTTPException(status_code=400, detail="Mindestens ein Kleidungsstück muss angegeben werden")
        
        # AI-Beschreibung generieren
        ai_description = ""
        if weather_condition and occasion and mood:
            ai_description = ai.generate_outfit_description(
                user_id=user_id,
                weather_condition=weather_condition,
                occasion=occasion,
                mood=mood
            )
        
        # Outfit erstellen
        outfit = db.create_outfit(
            user_id=user_id,
            name=name,
            clothing_ids=clothing_id_list,
            description=ai_description,
            weather_condition=weather_condition,
            occasion=occasion,
            mood=mood
        )
        
        if not outfit:
            raise HTTPException(status_code=400, detail="Outfit konnte nicht erstellt werden")
        
        # Vollständige Outfit-Daten laden
        full_outfit = db.get_outfit(outfit['id'], include_items=True)
        
        logger.info(f"Outfit mit AI-Beschreibung erstellt: {outfit['id']}")
        return full_outfit
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler bei der AI-gestützten Outfit-Erstellung: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# IMAGE UPLOAD ENDPOINTS
# ======================

@app.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    user_id: str = Form(..., description="UUID des Nutzers"),
    file: UploadFile = File(..., description="Bilddatei"),
    storage: StorageManager = Depends(get_storage_manager)
):
    """
    Lädt ein Bild hoch und gibt die URL zurück
    """
    try:
        # Datei-Validierung
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_message = storage.validate_image_file(file.content_type, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Upload zu Supabase Storage
        image_url = storage.upload_clothing_image(
            user_id=user_id,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        return ImageUploadResponse(
            image_url=image_url,
            message="Bild erfolgreich hochgeladen"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Hochladen des Bildes: {e}")
        raise HTTPException(status_code=500, detail=f"Upload fehlgeschlagen: {str(e)}")

@app.post("/clothes-with-image", response_model=ClothingResponse, status_code=status.HTTP_201_CREATED)
async def add_clothing_item_with_image(
    user_id: str = Form(..., description="UUID des Nutzers"),
    category: str = Form(..., description="Kategorie des Kleidungsstücks"),
    color: Optional[str] = Form(None, description="Hauptfarbe"),
    style: Optional[str] = Form(None, description="Stil"),
    season: Optional[str] = Form(None, description="Saison"),
    file: UploadFile = File(..., description="Bilddatei"),
    db: DatabaseManager = Depends(get_database_manager),
    storage: StorageManager = Depends(get_storage_manager)
):
    """
    Erstellt ein Kleidungsstück mit Bild-Upload in einem Schritt
    """
    try:
        # Bild hochladen
        file_content = await file.read()
        file_size = len(file_content)
        
        is_valid, error_message = storage.validate_image_file(file.content_type, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        image_url = storage.upload_clothing_image(
            user_id=user_id,
            file_content=file_content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # Kleidungsstück in Datenbank erstellen
        clothing = db.add_clothing_item(
            user_id=user_id,
            image_url=image_url,
            category=category,
            color=color,
            style=style,
            season=season
        )
        
        if not clothing:
            # Falls DB-Erstellung fehlschlägt, Bild wieder löschen
            storage.delete_clothing_image(image_url)
            raise HTTPException(status_code=400, detail="Kleidungsstück konnte nicht erstellt werden")
        
        return clothing
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Kleidungsstücks mit Bild: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# USER ENDPOINTS
# ======================

@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user_profile(
    user_data: UserCreate,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Erstellt ein Nutzerprofil nach der Registrierung"""
    try:
        user = db.create_user_profile(
            user_id=user_data.user_id,
            email=user_data.email,
            first_name=user_data.first_name,
            last_name=user_data.last_name
        )
        if not user:
            raise HTTPException(status_code=400, detail="Nutzerprofil konnte nicht erstellt werden")
        return user
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Nutzerprofils: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt das Nutzerprofil"""
    try:
        user = db.get_user_profile(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Nutzerprofil nicht gefunden")
        return user
    except Exception as e:
        logger.error(f"Fehler beim Laden des Nutzerprofils: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user_profile(
    user_id: str,
    user_data: UserUpdate,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Aktualisiert das Nutzerprofil"""
    try:
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        user = db.update_user_profile(user_id, **update_data)
        if not user:
            raise HTTPException(status_code=404, detail="Nutzerprofil nicht gefunden")
        return user
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Nutzerprofils: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_profile(
    user_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Löscht das Nutzerprofil und alle verknüpften Daten"""
    try:
        success = db.delete_user_profile(user_id)
        if not success:
            raise HTTPException(status_code=404, detail="Nutzerprofil nicht gefunden")
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Nutzerprofils: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# CLOTHING ENDPOINTS
# ======================

@app.post("/clothes", response_model=ClothingResponse, status_code=status.HTTP_201_CREATED)
async def add_clothing_item(
    clothing_data: ClothingCreate,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Fügt ein Kleidungsstück hinzu (mit bereits vorhandener image_url)"""
    try:
        clothing = db.add_clothing_item(
            user_id=clothing_data.user_id,
            image_url=clothing_data.image_url,
            category=clothing_data.category,
            color=clothing_data.color,
            style=clothing_data.style,
            season=clothing_data.season
        )
        if not clothing:
            raise HTTPException(status_code=400, detail="Kleidungsstück konnte nicht erstellt werden")
        return clothing
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen des Kleidungsstücks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/clothes", response_model=List[ClothingResponse])
async def get_user_clothes(
    user_id: str,
    category: Optional[str] = None,
    season: Optional[str] = None,
    style: Optional[str] = None,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt alle Kleidungsstücke eines Nutzers mit optionalen Filtern"""
    try:
        clothes = db.get_user_clothes(
            user_id=user_id,
            category=category,
            season=season,
            style=style
        )
        return clothes
    except Exception as e:
        logger.error(f"Fehler beim Laden der Kleidungsstücke: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/clothes/{clothing_id}", response_model=ClothingResponse)
async def get_clothing_item(
    clothing_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt ein einzelnes Kleidungsstück"""
    try:
        clothing = db.get_clothing_item(clothing_id)
        if not clothing:
            raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
        return clothing
    except Exception as e:
        logger.error(f"Fehler beim Laden des Kleidungsstücks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/clothes/{clothing_id}", response_model=ClothingResponse)
async def update_clothing_item(
    clothing_id: str,
    clothing_data: ClothingUpdate,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Aktualisiert ein Kleidungsstück"""
    try:
        update_data = clothing_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        clothing = db.update_clothing_item(clothing_id, **update_data)
        if not clothing:
            raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
        return clothing
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Kleidungsstücks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clothes/{clothing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_clothing_item(
    clothing_id: str,
    db: DatabaseManager = Depends(get_database_manager),
    storage: StorageManager = Depends(get_storage_manager)
):
    """Löscht ein Kleidungsstück und das zugehörige Bild"""
    try:
        # Erst Kleidungsstück aus DB holen um image_url zu bekommen
        clothing = db.get_clothing_item(clothing_id)
        if not clothing:
            raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
        
        # Aus Datenbank löschen
        success = db.delete_clothing_item(clothing_id)
        if not success:
            raise HTTPException(status_code=404, detail="Kleidungsstück nicht gefunden")
        
        # Bild aus Storage löschen (im Hintergrund, Fehler nicht kritisch)
        try:
            storage.delete_clothing_image(clothing['image_url'])
        except Exception as storage_error:
            logger.warning(f"Konnte Bild nicht aus Storage löschen: {storage_error}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Kleidungsstücks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# OUTFIT ENDPOINTS
# ======================

@app.post("/outfits", response_model=OutfitResponse, status_code=status.HTTP_201_CREATED)
async def create_outfit(
    outfit_data: OutfitCreate,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Erstellt ein neues Outfit mit Kleidungsstücken"""
    try:
        outfit = db.create_outfit(
            user_id=outfit_data.user_id,
            name=outfit_data.name,
            clothing_ids=outfit_data.clothing_ids,
            description=outfit_data.description,
            weather_condition=outfit_data.weather_condition,
            occasion=outfit_data.occasion,
            mood=outfit_data.mood
        )
        if not outfit:
            raise HTTPException(status_code=400, detail="Outfit konnte nicht erstellt werden")
        
        # Laden mit Items für Response
        full_outfit = db.get_outfit(outfit['id'], include_items=True)
        return full_outfit
    except Exception as e:
        logger.error(f"Fehler beim Erstellen des Outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/outfits", response_model=List[OutfitResponse])
async def get_user_outfits(
    user_id: str,
    include_items: bool = True,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt alle Outfits eines Nutzers"""
    try:
        outfits = db.get_user_outfits(user_id, include_items=include_items)
        return outfits
    except Exception as e:
        logger.error(f"Fehler beim Laden der Outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/outfits/{outfit_id}", response_model=OutfitResponse)
async def get_outfit(
    outfit_id: str,
    include_items: bool = True,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt ein einzelnes Outfit"""
    try:
        outfit = db.get_outfit(outfit_id, include_items=include_items)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
        return outfit
    except Exception as e:
        logger.error(f"Fehler beim Laden des Outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/outfits/{outfit_id}", response_model=OutfitResponse)
async def update_outfit(
    outfit_id: str,
    outfit_data: OutfitUpdate,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Aktualisiert ein Outfit"""
    try:
        update_data = outfit_data.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="Keine Daten zum Aktualisieren")
        
        outfit = db.update_outfit(outfit_id, **update_data)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
        return outfit
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren des Outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/outfits/{outfit_id}/worn")
async def mark_outfit_as_worn(
    outfit_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Markiert ein Outfit als getragen"""
    try:
        outfit = db.mark_outfit_as_worn(outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
        return {"message": "Outfit als getragen markiert", "worn_at": outfit["worn_at"]}
    except Exception as e:
        logger.error(f"Fehler beim Markieren des Outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/outfits/{outfit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_outfit(
    outfit_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Löscht ein Outfit"""
    try:
        success = db.delete_outfit(outfit_id)
        if not success:
            raise HTTPException(status_code=404, detail="Outfit nicht gefunden")
    except Exception as e:
        logger.error(f"Fehler beim Löschen des Outfits: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# OUTFIT ITEMS ENDPOINTS
# ======================

@app.post("/outfits/{outfit_id}/items")
async def add_items_to_outfit(
    outfit_id: str,
    clothing_ids: List[str],
    db: DatabaseManager = Depends(get_database_manager)
):
    """Fügt Kleidungsstücke zu einem Outfit hinzu"""
    try:
        items = db.add_items_to_outfit(outfit_id, clothing_ids)
        return {"message": f"{len(clothing_ids)} Kleidungsstücke hinzugefügt", "items": items}
    except Exception as e:
        logger.error(f"Fehler beim Hinzufügen der Items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/outfits/{outfit_id}/items", response_model=List[ClothingResponse])
async def get_outfit_items(
    outfit_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt alle Kleidungsstücke eines Outfits"""
    try:
        items = db.get_outfit_items(outfit_id)
        return items
    except Exception as e:
        logger.error(f"Fehler beim Laden der Outfit-Items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/outfits/{outfit_id}/items/{clothing_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_item_from_outfit(
    outfit_id: str,
    clothing_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Entfernt ein Kleidungsstück aus einem Outfit"""
    try:
        success = db.remove_item_from_outfit(outfit_id, clothing_id)
        if not success:
            raise HTTPException(status_code=404, detail="Item nicht im Outfit gefunden")
    except Exception as e:
        logger.error(f"Fehler beim Entfernen des Items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/outfits/{outfit_id}/items")
async def update_outfit_items(
    outfit_id: str,
    clothing_ids: List[str],
    db: DatabaseManager = Depends(get_database_manager)
):
    """Ersetzt alle Kleidungsstücke eines Outfits"""
    try:
        items = db.update_outfit_items(outfit_id, clothing_ids)
        return {"message": "Outfit-Items aktualisiert", "items": items}
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Outfit-Items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# ANALYTICS & SEARCH ENDPOINTS
# ======================

@app.get("/users/{user_id}/statistics", response_model=UserStatistics)
async def get_user_statistics(
    user_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt Statistiken für einen Nutzer"""
    try:
        stats = db.get_user_statistics(user_id)
        return stats
    except Exception as e:
        logger.error(f"Fehler beim Laden der Statistiken: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/outfits/search", response_model=List[OutfitResponse])
async def search_outfits(
    user_id: str,
    query: Optional[str] = None,
    weather_condition: Optional[str] = None,
    occasion: Optional[str] = None,
    mood: Optional[str] = None,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Sucht Outfits nach verschiedenen Kriterien"""
    try:
        outfits = db.search_outfits(
            user_id=user_id,
            query=query,
            weather_condition=weather_condition,
            occasion=occasion,
            mood=mood
        )
        return outfits
    except Exception as e:
        logger.error(f"Fehler bei der Outfit-Suche: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}/clothes/categories", response_model=List[str])
async def get_clothing_categories(
    user_id: str,
    db: DatabaseManager = Depends(get_database_manager)
):
    """Holt alle verwendeten Kleidungskategorien eines Nutzers"""
    try:
        categories = db.get_clothing_categories(user_id)
        return categories
    except Exception as e:
        logger.error(f"Fehler beim Laden der Kategorien: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ======================
# HEALTH CHECK
# ======================

@app.get("/health")
async def health_check(
    db: DatabaseManager = Depends(get_database_manager),
    storage: StorageManager = Depends(get_storage_manager),
    ai: ClothingAI = Depends(get_clothing_ai)
):
    """Überprüft die API, Datenbank-, Storage- und AI-Verbindung"""
    try:
        db_healthy = db.health_check()
        storage_healthy = storage.health_check()
        ai_healthy = ai.health_check()
        
        overall_status = "healthy" if (db_healthy and storage_healthy and ai_healthy) else "unhealthy"
        
        return {
            "status": overall_status,
            "database": "connected" if db_healthy else "disconnected",
            "storage": "connected" if storage_healthy else "disconnected",
            "ai": "connected" if ai_healthy else "disconnected",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health Check Fehler: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
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
    logger.info("Wardroberry API gestartet")
    
    # Storage Bucket erstellen falls nicht vorhanden
    try:
        storage = StorageManager()
        storage.create_clothing_bucket_if_not_exists()
        logger.info("Storage Bucket überprüft/erstellt")
    except Exception as e:
        logger.warning(f"Storage Bucket Setup fehlgeschlagen: {e}")
    
    logger.info("Verfügbare Endpoints:")
    for route in app.routes:
        if hasattr(route, 'methods') and hasattr(route, 'path'):
            logger.info(f"  {', '.join(route.methods)} {route.path}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)