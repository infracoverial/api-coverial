from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, conint
from datetime import datetime
from typing import Optional
import unicodedata
import re

app = FastAPI()

# Autoriser toutes les requêtes CORS pour le développement
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fonction pour normaliser le texte (supprimer accents, mettre en minuscule, remplacer espaces)
def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()  # Convertir en minuscule et supprimer espaces inutiles
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")  # Supprimer les accents
    text = re.sub(r"\s+", "_", text)  # Remplacer les espaces par _
    return text

# Modèle des données envoyées par le client
class VehicleInfo(BaseModel):
    marque: str = Field(..., description="Marque du véhicule")
    modele: str = Field(..., description="Modèle du véhicule")
    motorisation: str
    moteur: str
    categorie: str
    kilometrage: conint(ge=0)  # Kilométrage ne peut pas être négatif
    annee_mise_en_circulation: conint(ge=1900, le=datetime.now().year)  # Doit être une année valide
    proprietaires: conint(ge=1)  # Minimum 1 propriétaire
    historique_entretien: str
    etat: str
    puissance: conint(ge=0)
    boite_vitesse: str
    transmission: str
    usage: str
    sinistres: str

# Normalisation des coefficients
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

coeff_etat = {"tres_bon": 1.0, "quelques_defauts": 1.1, "nombreux_defauts": 1.2, "problemes_mecaniques": None}
coeff_historique_entretien = {"complet": 1.0, "partiel": 1.2, "inconnu": None}

def get_coefficient(coeff_dict, value):
    return coeff_dict.get(value, 1.0)

@app.post("/calculer_prix")
async def calculer_prix(vehicule: VehicleInfo):
    annee_actuelle = datetime.now().year
    age_vehicule = annee_actuelle - vehicule.annee_mise_en_circulation

    # Normalisation des données d'entrée
    vehicule.marque = normalize_text(vehicule.marque)
    vehicule.motorisation = normalize_text(vehicule.motorisation)
    vehicule.categorie = normalize_text(vehicule.categorie)
    vehicule.historique_entretien = normalize_text(vehicule.historique_entretien)
    vehicule.etat = normalize_text(vehicule.etat)

    coef_entretien = coeff_historique_entretien.get(vehicule.historique_entretien)
    coef_etat = coeff_etat.get(vehicule.etat)
    coef_annee = get_coefficient({(0, 3): 1.0, (4, 7): 1.1, (8, 12): 1.3, (13, 999): 1.5}, age_vehicule)

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