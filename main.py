from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint
from datetime import datetime
import unicodedata
import re

app = FastAPI()

# Autoriser toutes les requêtes CORS pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # À restreindre en production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # Autoriser tous les headers
)

# Définir une clé API (à garder secrète et changer régulièrement)
API_KEY = "854596653658gzeyrggyds"  # Remplace par ta clé API sécurisée

# Fonction pour vérifier la clé API dans le header
def verify_api_key(api_key: str = Header(None), authorization: str = Header(None), request: Request = None):
    """
    Vérifie la clé API dans deux formats :
    1. Header direct: `api_key`
    2. Header avec `Authorization: Bearer`
    """
    # Log pour voir TOUS les headers reçus (utile pour le debug)
    print(f"📌 Tous les headers reçus: {request.headers if request else 'Headers non disponibles'}")

    received_key = None

    # Vérifie si la clé API est passée en `api_key`
    if api_key:
        received_key = api_key.strip()

    # Vérifie si la clé API est passée en `Authorization: Bearer`
    if authorization and authorization.startswith("Bearer "):
        received_key = authorization.split("Bearer ")[1].strip()

    print(f"🔍 Clé API reçue après parsing: '{received_key}'")

    if received_key is None:
        raise HTTPException(status_code=400, detail="Aucune clé API reçue")

    if received_key != API_KEY:
        raise HTTPException(status_code=403, detail="Clé API invalide")

# Fonction pour normaliser le texte
def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    text = re.sub(r"\s+", "_", text)
    return text

# Modèle des données envoyées par le client
class VehicleInfo(BaseModel):
    marque: str = Field(..., description="Marque du véhicule")
    modele: str = Field(..., description="Modèle du véhicule")
    motorisation: str
    categorie: str
    kilometrage: conint(ge=0)
    annee_mise_en_circulation: conint(ge=1900, le=datetime.now().year)
    proprietaires: conint(ge=1)
    historique_entretien: str
    etat: str
    puissance: conint(ge=0)
    boite_vitesse: str
    transmission: str
    usage: str
    sinistres: str

# Coefficients pour calcul du prix
coeff_marques = {normalize_text(m): v for m, v in {
    "Dacia": 1.1, "Renault": 1.1, "Peugeot": 1.1, "Citroën": 1.1, "Fiat": 1.1,
    "Volkswagen": 1.1, "Opel": 1.1, "Ford": 1.1, "Seat": 1.1, "Skoda": 1.1,
    "Toyota": 1.1, "Honda": 1.1, "Nissan": 1.2, "Hyundai": 1.2, "Kia": 1.2,
    "Mazda": 1.2, "Suzuki": 1.2, "Mini": 1.2, "Audi": 1.3, "Mercedes": 1.3,
    "BMW": 1.3, "Alfa Romeo": 1.3, "Volvo": 1.3, "Jaguar": 1.4, "Land Rover": 1.4,
    "Porsche": 1.5, "Maserati": 1.6, "Chevrolet": 1.1, "Chrysler": 1.2, "Dodge": 1.2,
    "Jeep": 1.3, "Subaru": 1.2, "Mitsubishi": 1.2, "Saab": 1.3, "Lancia": 1.3,
    "Alpine": 1.3, "SsangYong": 1.2, "Isuzu": 1.2
}.items()}

coeff_motorisation = {normalize_text(k): v for k, v in {"Essence": 1.0, "Diesel": 1.1, "GPL": 1.0, "Hybride": 1.2}.items()}
coeff_categories = {normalize_text(k): v for k, v in {
    "Citadine": 1.0, "Compacte": 1.1, "Berline": 1.2, "SUV Urbain": 1.15,
    "SUV": 1.3, "SUV 7 places": 1.35, "SUV Luxe": 1.5, "Break": 1.2,
    "Monospace": 1.2, "Grand Monospace": 1.3, "Ludospace": 1.1, "Tout-terrain": 1.4,
    "Pick-up": 1.3, "Coupé Sportif": 1.6, "Berline Sportive": 1.5, "SUV Sportif": 1.7,
    "Autre": 1.0
}.items()}

@app.post("/calculer_prix")
async def calculer_prix(
    vehicule: VehicleInfo, 
    api_key: str = Header(None), 
    authorization: str = Header(None), 
    request: Request = None
):
    verify_api_key(api_key, authorization, request)  # Vérifie la clé API

    return {"message": "Clé API valide, requête acceptée"}
