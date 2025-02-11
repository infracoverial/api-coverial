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
def verify_api_key(authorization: str = Header(None), request: Request = None):
    """
    Vérifie la clé API dans le header Authorization: Bearer.
    """
    print(f"📌 Tous les headers reçus: {request.headers if request else 'Headers non disponibles'}")  # Debug

    received_key = None

    # Vérifie si la clé API est passée en `Authorization: Bearer`
    if authorization and authorization.startswith("Bearer "):
        received_key = authorization.split("Bearer ")[1].strip()

    print(f"🔍 Clé API reçue après parsing: '{received_key}'")  # Debug

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

coeff_motorisation = {"essence": 1.0, "diesel": 1.1, "gpl": 1.0, "hybride": 1.2}
coeff_categories = {"citadine": 1.0, "berline": 1.2, "suv": 1.3, "sportive": 1.6}

# Ajout des coefficients manquants
coeff_historique_entretien = {"complet": 1.0, "partiel": 1.2, "inconnu": None}
coeff_etat = {"tres_bon": 1.0, "quelques_defauts": 1.1, "nombreux_defauts": 1.2, "problemes_mecaniques": None}

@app.post("/calculer_prix")
async def calculer_prix(
    vehicule: VehicleInfo, 
    authorization: str = Header(None), 
    request: Request = None
):
    verify_api_key(authorization, request)  # Vérifie la clé API

    annee_actuelle = datetime.now().year
    age_vehicule = annee_actuelle - vehicule.annee_mise_en_circulation

    # Normalisation des données d'entrée
    vehicule.marque = normalize_text(vehicule.marque)
    vehicule.motorisation = normalize_text(vehicule.motorisation)
    vehicule.categorie = normalize_text(vehicule.categorie)
    vehicule.historique_entretien = normalize_text(vehicule.historique_entretien)
    vehicule.etat = normalize_text(vehicule.etat)

    coef_entretien = coeff_historique_entretien.get(vehicule.historique_entretien, 1.0)
    coef_etat = coeff_etat.get(vehicule.etat, 1.0)
    coef_annee = {0: 1.0, 4: 1.1, 8: 1.3, 13: 1.5}.get(age_vehicule, 1.5)

    if coef_entretien is None or coef_etat is None:
        raise HTTPException(status_code=400, detail="Véhicule non éligible à la garantie")

    prix_base = 120
    prix_final = prix_base
    prix_final *= coeff_marques.get(vehicule.marque, 1.1)
    prix_final *= coeff_motorisation.get(vehicule.motorisation, 1.0)
    prix_final *= coeff_categories.get(vehicule.categorie, 1.0)
    prix_final *= coef_annee
    prix_final *= coef_entretien

    return {"prix_final": round(prix_final, 2)}
