from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
import traceback

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

# (Tes coefficients ici...)

def get_coefficient(coeff_map, valeur):
    for (borne_min, borne_max), coef in coeff_map.items():
        if borne_min <= valeur <= borne_max:
            return coef
    return 1.0


@app.post("/calculer_prix")
async def calculer_prix(vehicule: VehicleInfo):
    try:
        annee_actuelle = datetime.now().year
        age_vehicule = annee_actuelle - vehicule.annee_mise_en_circulation

        coef_entretien = coeff_historique_entretien.get(vehicule.historique_entretien)
        if coef_entretien is None:
            return {"prix_3_mois": None, "prix_6_mois": None, "eligibilite": "no", "motif": f"Historique inconnu : {vehicule.historique_entretien}"}

        coef_etat = coeff_etat.get(vehicule.etat)
        if coef_etat is None:
            return {"prix_3_mois": None, "prix_6_mois": None, "eligibilite": "no", "motif": f"État inconnu : {vehicule.etat}"}

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

        prix_final_6_mois = prix_final_3_mois * 1.6

        eligible_6_mois = (
            age_vehicule <= 8 and
            vehicule.kilometrage <= 100000 and
            vehicule.etat in ["Très bon", "Quelques défauts"] and
            vehicule.historique_entretien in ["Complet", "Partiel"]
        )

        if prix_final_3_mois < 100:
            return {"prix_3_mois": None, "prix_6_mois": None, "eligibilite": "no", "motif": "Prix trop bas"}

        if eligible_6_mois:
            return {
                "prix_3_mois": round(prix_final_3_mois, 2),
                "prix_6_mois": round(prix_final_6_mois, 2),
                "eligibilite": "yes_3_6_mois"
            }
        else:
            return {
                "prix_3_mois": round(prix_final_3_mois, 2),
                "prix_6_mois": None,
                "eligibilite": "yes_3_mois_seulement"
            }

    except Exception as e:
        print("🚨 ERREUR :")
        traceback.print_exc()
        return {"erreur": str(e)}
