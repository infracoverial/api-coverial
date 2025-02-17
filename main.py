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

# Les coefficients inchangés...

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
        return {
            "prix_3_mois": None,
            "prix_6_mois": None,
            "eligibilite": "no",
            "motif": "Année de mise en circulation invalide"
        }

    age_vehicule = annee_actuelle - vehicule.annee_mise_en_circulation

    coef_entretien = coeff_historique_entretien.get(vehicule.historique_entretien)
    if coef_entretien is None:
        return {"prix_3_mois": None, "prix_6_mois": None, "eligibilite": "no", "motif": "Véhicule non éligible : Historique d’entretien inconnu"}

    coef_etat = coeff_etat.get(vehicule.etat)
    if coef_etat is None:
        return {"prix_3_mois": None, "prix_6_mois": None, "eligibilite": "no", "motif": "Véhicule non éligible : État avec problèmes mécaniques"}

    coef_annee = get_coefficient(coeff_annee, age_vehicule)
    coef_puissance = get_coefficient(coeff_puissance, vehicule.puissance)
    coef_kilometrage = get_coefficient(coeff_kilometrage, vehicule.kilometrage)

    prix_base = 120
    prix_final_3_mois = prix_base
    prix_final_3_mois *= coeff_marques.get(vehicule.marque.capitalize(), 1.1)
    prix_final_3_mois *= coeff_motorisation.get(vehicule.motorisation, 1.0)
    prix_final_3_mois *= coeff_categories.get(vehicule.categorie, 1.0)
    prix_final_3_mois *= coeff_usage.get(vehicule.usage, 1.0)
    prix_final_3_mois *= coeff_sinistres.get(vehicule.sinistres, 1.0)
    prix_final_3_mois *= coef_puissance
    prix_final_3_mois *= coef_annee
    prix_final_3_mois *= coef_entretien
    prix_final_3_mois *= coef_etat
    prix_final_3_mois *= coef_kilometrage

    # Prix 6 mois : majoration de 60% du prix 3 mois
    prix_final_6_mois = prix_final_3_mois * 1.6

    # Critères d’éligibilité pour 6 mois
    eligible_6_mois = (
        age_vehicule <= 8 and
        vehicule.kilometrage <= 150000 and
        vehicule.etat in ["Très bon", "Quelques défauts"] and
        vehicule.historique_entretien in ["Complet", "Partiel"]
    )

    if prix_final_3_mois < 100:  # Exemple de seuil de non éligibilité (optionnel)
        return {"prix_3_mois": None, "prix_6_mois": None, "eligibilite": "no", "motif": "Prix trop bas, véhicule non assurable"}

    if eligible_6_mois:
        reponse = {
            "prix_3_mois": round(prix_final_3_mois, 2),
            "prix_6_mois": round(prix_final_6_mois, 2),
            "eligibilite": "yes_3_6_mois"
        }
    else:
        reponse = {
            "prix_3_mois": round(prix_final_3_mois, 2),
            "prix_6_mois": None,
            "eligibilite": "yes_3_mois_seulement"
        }

    print(f"✅ Réponse envoyée : {reponse}")
    return reponse
