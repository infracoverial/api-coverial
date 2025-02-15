from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime

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
    usage: str
    sinistres: str


coeff_marques = {m.capitalize(): v for m, v in {
    "Dacia": 1.1, "Renault": 1.1, "Peugeot": 1.1, "Citroën": 1.1, "Fiat": 1.1,
    "Volkswagen": 1.1, "Opel": 1.1, "Ford": 1.1, "Seat": 1.1, "Skoda": 1.1,
    "Toyota": 1.1, "Honda": 1.1, "Nissan": 1.2, "Hyundai": 1.2, "Kia": 1.2,
    "Mazda": 1.2, "Suzuki": 1.2, "Mini": 1.2, "Audi": 1.3, "Mercedes": 1.3,
    "BMW": 1.3, "Alfa Romeo": 1.3, "Volvo": 1.3, "Jaguar": 1.4, "Land Rover": 1.4,
    "Porsche": 1.5, "Maserati": 1.6, "Chevrolet": 1.1, "Chrysler": 1.2, "Dodge": 1.2,
    "Jeep": 1.3, "Subaru": 1.2, "Mitsubishi": 1.2, "Saab": 1.3, "Lancia": 1.3,
    "Alpine": 1.3, "SsangYong": 1.2, "Isuzu": 1.2
}.items()}

coeff_motorisation = {"Essence": 1.0, "Diesel": 1.1, "GPL": 1.0, "Hybride": 1.2}
coeff_categories = {
    "Citadine": 1.0,
    "Berline compacte": 1.1,
    "Berline familiale": 1.2,
    "SUV compact": 1.3,
    "SUV familial": 1.4,
    "Break": 1.2,
    "Monospace": 1.3,
    "Utilitaire léger": 1.2,
    "Coupé / Cabriolet": 1.5,
    "4x4 / Tout-terrain": 1.6
}
coeff_usage = {"Personnel": 1.0, "Taxi": 1.3, "VTC": 1.6}
coeff_sinistres = {"Aucun": 1.0, "Carrosserie": 1.2, "Carrosserie + Mécanique": 1.5}
coeff_puissance = {(0, 130): 1.0, (131, 220): 1.2, (221, 300): 1.4, (301, 9999): 1.5}
coeff_etat = {"tres_bon": 1.0, "quelques_defauts": 1.1, "nombreux_defauts": 1.2, "problemes_mecaniques": None}
coeff_historique_entretien = {"complet": 1.0, "partiel": 1.2, "inconnu": None}
coeff_annee = {(0, 3): 1.0, (4, 7): 1.1, (8, 12): 1.3, (13, 999): 1.5}
coeff_kilometrage = {
    (0, 50000): 1.0,
    (50001, 100000): 1.1,
    (100001, 150000): 1.3,
    (150001, 9999999): 1.5
}

def get_coefficient(coeff_map, valeur):
    for (borne_min, borne_max), coef in coeff_map.items():
        if borne_min <= valeur <= borne_max:
            return coef
    return 1.0

@app.post("/calculer_prix")
async def calculer_prix(vehicule: VehicleInfo):
    print(f"🔍 Requête reçue : {vehicule.dict()}")

    annee_actuelle = datetime.now().year
    if vehicule.annee_mise_en_circulation > annee_actuelle:
        reponse = {
            "prix_final": None,
            "eligibilite": "no",
            "motif": "Année de mise en circulation invalide"
        }
        print(f"❌ Réponse envoyée : {reponse}")
        return reponse

    age_vehicule = annee_actuelle - vehicule.annee_mise_en_circulation

    coef_entretien = coeff_historique_entretien.get(vehicule.historique_entretien)
    if coef_entretien is None:
        return {"prix_final": None, "eligibilite": "no", "motif": "Véhicule non éligible : Historique d’entretien inconnu"}

    coef_etat = coeff_etat.get(vehicule.etat)
    if coef_etat is None:
        return {"prix_final": None, "eligibilite": "no", "motif": "Véhicule non éligible : État avec problèmes mécaniques"}

    coef_annee = get_coefficient(coeff_annee, age_vehicule)
    coef_puissance = get_coefficient(coeff_puissance, vehicule.puissance)
    coef_kilometrage = get_coefficient(coeff_kilometrage, vehicule.kilometrage)

    prix_base = 120
    prix_final = prix_base
    prix_final *= coeff_marques.get(vehicule.marque.capitalize(), 1.1)
    prix_final *= coeff_motorisation.get(vehicule.motorisation, 1.0)
    prix_final *= coeff_categories.get(vehicule.categorie, 1.0)
    prix_final *= coeff_usage.get(vehicule.usage, 1.0)
    prix_final *= coeff_sinistres.get(vehicule.sinistres, 1.0)
    prix_final *= coef_puissance
    prix_final *= coef_annee
    prix_final *= coef_entretien
    prix_final *= coef_etat
    prix_final *= coef_kilometrage

    reponse = {"prix_final": round(prix_final, 2), "eligibilite": "yes"}
    print(f"✅ Réponse envoyée : {reponse}")
    return reponse
