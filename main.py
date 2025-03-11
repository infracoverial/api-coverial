from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

class VehicleInfo(BaseModel):
    type_vehicule: str
    marque: str
    modele: str
    motorisation: str
    categorie: str
    kilometrage: int = Field(..., ge=0)
    annee_mise_en_circulation: int
    proprietaires: int
    historique_entretien: str
    etat: str
    puissance: int
    boite_vitesse: str
    transmission: str
    usage: Optional[str] = None
    sinistres: str
    cylindree: Optional[int] = None
    usage_moto: Optional[str] = None
    modification_echappement: Optional[str] = None
    modification_equipement_securite: Optional[str] = None
    historique_sinistres_moto: Optional[str] = None

plafonds_max = {
    "Citadine": (1500, 900, 120000, 14),
    "Berline compacte": (1500, 1000, 150000, 14),
    "SUV": (2000, 1200, 150000, 16),
    "Berline premium": (2200, 1300, 150000, 14),
    "Scooter": (1500, 900, 50000, 14),
    "Routière": (2000, 1300, 100000, 14),
    "Roadster": (1500, 900, 60000, 10),
    "Trail": (1800, 1100, 70000, 14),
    "Sportive": (2000, 1300, 30000, 10)
}

def determine_plafond(categorie, kilometrage, annee, historique_entretien):
    if categorie in plafonds_max:
        max_plafond, inter_plafond, km_seuil, age_seuil = plafonds_max[categorie]
        if kilometrage > km_seuil or historique_entretien.lower() == "partiel" or annee > age_seuil:
            return inter_plafond
        return max_plafond
    return None

@app.post("/calcul_plafond/")
def calcul_plafond(vehicle: VehicleInfo):
    plafond = determine_plafond(vehicle.categorie, vehicle.kilometrage, vehicle.annee_mise_en_circulation, vehicle.historique_entretien)
    return {"plafond": plafond}
