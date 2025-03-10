from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, root_validator
from datetime import datetime
from typing import Optional
from enum import Enum
from coefficients import coeff_marques, coeff_motorisation, coeff_categories

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Enum pour la transmission des automobiles
class TransmissionAuto(str, Enum):
    TRACTION = "Traction"
    PROPULSION = "Propulsion"
    QUATRE_X_QUATRE = "4x4"

# Enum pour la transmission des motos
class TransmissionMoto(str, Enum):
    CHAINE = "Chaîne"
    CARDAN = "Cardan"
    COUROIE = "Courroie"

# Enum pour l'historique d'entretien
class HistoriqueEntretien(str, Enum):
    COMPLET = "Complet"
    PARTIEL = "Partiel"
    INCONNU = "Inconnu"

# Enum pour les sinistres voiture
class SinistresVoiture(str, Enum):
    AUCUN = "Aucun"
    CARROSSERIE = "Carrosserie"
    CARROSSERIE_MECANIQUE = "Carrosserie + Mécanique"

# Enum pour l'usage moto
class UsageMoto(str, Enum):
    QUOTIDIEN = "Quotidien"
    BALADE = "Balade"
    MIXTE = "Mixte"
    CIRCUIT = "Circuit"

class VehicleInfo(BaseModel):
    type_vehicule: str  # "voiture" ou "moto"
    marque: str
    modele: str
    motorisation: str  # Pour les motos, toujours "Essence"
    categorie: str  # Pour voitures, une catégorie parmi la liste définie
    kilometrage: int = Field(..., ge=0)
    annee_mise_en_circulation: int
    proprietaires: int
    historique_entretien: HistoriqueEntretien
    etat: str  # Ex: "Très bon", "Quelques défauts", etc.
    puissance: int
    boite_vitesse: str
    transmission: Optional[str] = None  # Transmission spécifique au type de véhicule
    usage: Optional[str] = None  # Rendre ce champ optionnel
    sinistres: SinistresVoiture
    # Champs spécifiques aux motos
    cylindree: Optional[int] = None
    usage_moto: Optional[UsageMoto] = None
    modification_echappement: Optional[str] = None  # "Oui" ou "Non"
    modification_equipement_securite: Optional[str] = None  # "Oui" ou "Non"
    historique_sinistres_moto: Optional[str] = None  # "Chute à l'arrêt", etc.

    @root_validator(pre=True)
    def validate_transmission(cls, values):
        type_vehicule = values.get("type_vehicule")
        transmission = values.get("transmission")

        if type_vehicule == "voiture" and transmission and transmission not in TransmissionAuto._value2member_map_:
            raise ValueError(f"Transmission invalide pour une voiture : {transmission}")

        if type_vehicule == "moto" and transmission and transmission not in TransmissionMoto._value2member_map_:
            raise ValueError(f"Transmission invalide pour une moto : {transmission}")

        return values
