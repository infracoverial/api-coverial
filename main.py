from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from datetime import datetime
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

# Modèle de données avec les champs communs et les champs spécifiques aux motos rendus optionnels
class VehicleInfo(BaseModel):
    type_vehicule: str  # "voiture" ou "moto"
    marque: str
    modele: str
    motorisation: str  # Pour les motos, toujours "Essence"
    categorie: str     # Pour voitures, une catégorie parmi la liste définie
    kilometrage: int = Field(..., ge=0)
    annee_mise_en_circulation: int
    proprietaires: int
    historique_entretien: str  # Pour voitures : "Complet", "Partiel", "Inconnu"
                               # Pour motos : "complet", "partiel", "innexistant"
    etat: str                # Pour voitures (ex: "Très bon", "Quelques défauts", etc.)
    puissance: int
    boite_vitesse: str
    transmission: str
    usage: str               # Pour voitures (ex: "Personnel", "Taxi", "VTC")
    sinistres: str           # Pour voitures (ex: "Aucun", "Carrosserie", "Carrosserie + Mécanique")
    # Champs spécifiques aux motos (optionnels)
    cylindree: Optional[int] = None
    usage_moto: Optional[str] = None           # "quotidien", "balade", "mixte" ou "circuit"
    modification_echappement: Optional[str] = None  # "Oui" ou "Non"
    modification_equipement_securite: Optional[str] = None  # "Oui" ou "Non"
    historique_sinistres_moto: Optional[str] = None  # "Chute à l'arret", "Chutes en roulant", "Accident", "Aucun"

# -------------------------------
# Coefficients pour les voitures
# -------------------------------
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
    "Monospace": 1.2,
    "Berline": 1.2,
    "SUV": 1.3,
    "Utilitaire": 1.1,
    "Break": 1.2,
    "Coupé cabriolet": 1.4,
    "Coupé": 1.3,
    "Berline premium": 1.5,
    "Citadine premium": 1.4,
    "SUV premium": 1.6,
    "Break premium": 1.5,
    "Break compact": 1.15,
    "SUV compact": 1.25,
    "Berline luxe": 1.7,
    "SUV luxe": 1.8,
    "Micro-citadine": 0.9
}

coeff_usage = {"Personnel": 1.0, "Taxi": 1.3, "VTC": 1.6}
coeff_sinistres = {"Aucun": 1.0, "Carrosserie": 1.2, "Carrosserie + Mécanique": 1.5}
coeff_puissance = {(0, 130): 1.0, (131, 220): 1.2, (221, 300): 1.4, (301, 9999): 1.5}
coeff_etat = {"Très bon": 1.0, "Quelques défauts": 1.1, "Nombreux défauts": 1.2, "Problèmes mécaniques": None}
coeff_historique_entretien = {"Complet": 1.0, "Partiel": 1.2, "Inconnu": None}
coeff_annee = {(0, 3): 1.0, (4, 7): 1.1, (8, 12): 1.3, (13, 999): 1.5}
coeff_kilometrage = {
    (0, 50000): 1.0,
    (50001, 100000): 1.1,
    (100001, 150000): 1.3,
    (150001, 170000): 1.5,
    (170001, 9999999): 1.5  # Kilométrage > 170000 force la garantie à 3 mois
}

# ---------------------------------
# Coefficients spécifiques aux motos
# ---------------------------------
coeff_marques_moto = {
    "Aprilia": 1.3,
    "BMW": 1.5,
    "Ducati": 1.5,
    "Harley-Davidson": 1.4,
    "Honda": 1.1,
    "Kawasaki": 1.2,
    "KTM": 1.3,
    "Piaggio": 1.0,
    "Triumph": 1.4,
    "Vespa": 1.2
}

coeff_categories_moto = {
    "Roadster": 1.0,
    "Sportive": 1.2,
    "Supermotard": 1.1,
    "Trail": 1.1,
    "Sport-Touring": 1.2,
    "Touring": 1.0,
    "Trail Sportif": 1.3,
    "Roadster Néorétro": 1.1,
    "Cruiser": 1.0,
    "Power Cruiser": 1.2,
    "Électrique": 1.3,
    "Custom": 1.2,
    "Scooter": 0.9,
    "Scooter/Trail": 1.0,
    "Trail Routier": 1.1,
    "Motocross": 1.2,
    "Enduro": 1.1,
    "Supermoto": 1.2,
    "Scooter urbain": 0.9,
    "Scooter à grandes roues": 0.95,
    "Scooter GT à grandes roues": 1.0,
    "Maxi-scooter": 1.0,
    "Maxi-scooter compact": 1.0,
    "Scooter à trois roues": 1.0,
    "Scooter sportif": 1.1,
    "Scooter urbain compact": 0.95,
    "Scooter léger": 0.9,
    "Scooter classique": 1.0,
    "Classique": 1.0,
    "Café Racer": 1.2,
    "Scrambler": 1.1,
    "Adventure": 1.1,
    "Adventure/Touring": 1.2,
    "Scooter GT": 1.1,
    "Scooter urbain sportif": 1.2,
    "Scooter premium": 1.3,
    "Scooter électrique": 1.3
}

coeff_cylindree = {
    (0, 50): 0.9,
    (51, 125): 1.0,
    (126, 500): 1.1,
    (501, 650): 1.2,
    (651, 900): 1.4,
    (901, 1100): 1.4,
    (1101, 2000): 1.2
}

coeff_usage_moto = {
    "quotidien": 1.0,
    "balade": 0.95,
    "mixte": 1.0,
    "circuit": 1.3
}

coeff_modif_echappement = {
    "Oui": 1.2,
    "Non": 1.0
}
coeff_modif_equip = {
    "Oui": 1.1,
    "Non": 1.0
}

coeff_sinistres_moto = {
    "Aucun": 1.0,
    "Chute à l'arret": 1.1,
    "Chutes en roulant": 1.2,
    "Accident": 1.3
}

coeff_entretien_moto = {
    "complet": 1.0,
    "partiel": 1.2,
    "innexistant": 1.5
}

def get_coefficient(coeff_map, valeur):
    for (borne_min, borne_max), coef in coeff_map.items():
        if borne_min <= valeur <= borne_max:
            return coef
    return 1.0

# -------------------------------
# Calcul du tarif pour les voitures
# -------------------------------
def calculer_prix_voiture(vehicule: VehicleInfo):
    annee_actuelle = datetime.now().year
    if vehicule.annee_mise_en_circulation > annee_actuelle:
        return {"eligibilite": "no", "motif": "Année de mise en circulation invalide"}
    
    age_vehicule = annee_actuelle - vehicule.annee_mise_en_circulation

    coef_histo = coeff_historique_entretien.get(vehicule.historique_entretien)
    if coef_histo is None:
        return {"eligibilite": "no", "motif": "Véhicule non éligible : Historique d’entretien inconnu"}
    
    coef_etat_val = coeff_etat.get(vehicule.etat)
    if coef_etat_val is None:
        return {"eligibilite": "no", "motif": "Véhicule non éligible : État avec problèmes mécaniques"}
    
    coef_age = get_coefficient(coeff_annee, age_vehicule)
    coef_puissance_val = get_coefficient(coeff_puissance, vehicule.puissance)
    coef_km = get_coefficient(coeff_kilometrage, vehicule.kilometrage)
    
    prix_base = 120
    prix_final = prix_base
    prix_final *= coeff_marques.get(vehicule.marque.capitalize(), 1.1)
    prix_final *= coeff_motorisation.get(vehicule.motorisation, 1.0)
    prix_final *= coeff_categories.get(vehicule.categorie, 1.0)
    prix_final *= coeff_usage.get(vehicule.usage, 1.0)
    prix_final *= coeff_sinistres.get(vehicule.sinistres, 1.0)
    prix_final *= coef_puissance_val
    prix_final *= coef_age
    prix_final *= coef_histo
    prix_final *= coef_etat_val
    prix_final *= coef_km

    eligible_6mois = (
        age_vehicule <= 10 and
        vehicule.kilometrage <= 150000 and
        not (vehicule.proprietaires > 3 and vehicule.historique_entretien.lower() == "partiel") and
        vehicule.sinistres.lower() != "carrosserie + mécanique" and
        vehicule.etat.lower() != "nombreux défauts"
    )

    if vehicule.kilometrage > 170000 or age_vehicule > 15:
        eligible_6mois = False

    if eligible_6mois:
        tarif_3mois = round(prix_final, 2)
        tarif_6mois = round(prix_final * 1.9, 2)
        return {"eligibilite": "yes", "tarif_3mois": tarif_3mois, "tarif_6mois": tarif_6mois}
    else:
        tarif_3mois = round(prix_final, 2)
        return {"eligibilite": "yes", "tarif_3mois": tarif_3mois}

# -------------------------------
# Calcul du tarif pour les motos
# -------------------------------
def calculer_prix_moto(vehicule: VehicleInfo):
    annee_actuelle = datetime.now().year
    if vehicule.annee_mise_en_circulation > annee_actuelle:
        return {"eligibilite": "no", "motif": "Année de mise en circulation invalide"}
    
    if vehicule.historique_entretien and vehicule.historique_entretien.lower() == "innexistant":
        return {"eligibilite": "no", "motif": "Moto non éligible : Historique d’entretien inexistant"}
    
    if vehicule.kilometrage > 150000 and vehicule.marque.lower() not in ["honda", "bmw"]:
        return {"eligibilite": "no", "motif": "Moto non éligible : Kilométrage trop élevé"}
    
    prix_base = 100
    prix_final = prix_base
    
    prix_final *= coeff_marques_moto.get(vehicule.marque.capitalize(), 1.1)
    prix_final *= coeff_categories_moto.get(vehicule.categorie, 1.0)
    
    if vehicule.cylindree is not None:
        prix_final *= get_coefficient(coeff_cylindree, vehicule.cylindree)
    
    if vehicule.usage_moto:
        prix_final *= coeff_usage_moto.get(vehicule.usage_moto.lower(), 1.0)
    
    if vehicule.modification_echappement:
        prix_final *= coeff_modif_echappement.get(vehicule.modification_echappement.capitalize(), 1.0)
    
    if vehicule.modification_equipement_securite:
        prix_final *= coeff_modif_equip.get(vehicule.modification_equipement_securite.capitalize(), 1.0)
    
    if vehicule.historique_sinistres_moto:
        prix_final *= coeff_sinistres_moto.get(vehicule.historique_sinistres_moto, 1.0)
    
    if vehicule.historique_entretien:
        coef_entretien = coeff_entretien_moto.get(vehicule.historique_entretien.lower())
        if coef_entretien is None:
            return {"eligibilite": "no", "motif": "Moto non éligible : Historique d’entretien non reconnu"}
        prix_final *= coef_entretien
    
    return {"eligibilite": "yes", "prix_final": round(prix_final, 2)}

# -------------------------------
# Endpoint de calcul du tarif
# -------------------------------
@app.post("/calculer_prix")
async def calculer_prix(vehicule: VehicleInfo):
    print(f"🔍 Requête reçue : {vehicule.dict()}")
    
    if vehicule.type_vehicule.lower() == "moto":
        reponse = calculer_prix_moto(vehicule)
        print(f"✅ Réponse envoyée (moto) : {reponse}")
        return reponse
    elif vehicule.type_vehicule.lower() == "voiture":
        reponse = calculer_prix_voiture(vehicule)
        print(f"✅ Réponse envoyée (voiture) : {reponse}")
        return reponse
    else:
        return {"eligibilite": "no", "motif": "Type de véhicule inconnu"}
