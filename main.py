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
    usage: Optional[str] = None  # Optionnel pour les motos
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

# Coefficient pour la transmission des voitures
coeff_transmission_voiture = {
    "Traction": 1.0,
    "Propulsion": 1.1,
    "Intégrale": 1.2
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

coeff_transmission_moto = {
    "chaîne": 1.0,
    "cardan": 1.1,
    "courroie": 1.2
}

def get_coefficient(coeff_map, valeur):
    for (borne_min, borne_max), coef in coeff_map.items():
        if borne_min <= valeur <= borne_max:
            return coef
    return 1.0

# Plafonds maximums pour les voitures
plafonds_max_voitures = {
    "Citadine": 1500,
    "Berline compacte": 1500,
    "Monospace": 1500,
    "Berline": 1500,
    "SUV": 2000,
    "Utilitaire": 1500,
    "Break": 1500,
    "Coupé cabriolet": 1500,
    "Coupé": 1500,
    "Berline premium": 2200,
    "Citadine premium": 1500,
    "SUV premium": 2200,
    "Break premium": 1500,
    "Break compact": 1500,
    "SUV compact": 1500,
    "Berline luxe": 2200,
    "SUV luxe": 2200,
    "Micro-citadine": 1500
}

# Plafonds maximums pour les motos
plafonds_max_motos = {
    "Roadster": 1500,
    "Sportive": 2000,
    "Supermotard": 1500,
    "Trail": 1800,
    "Sport-Touring": 2000,
    "Touring": 2000,
    "Trail Sportif": 2000,
    "Roadster Néorétro": 1500,
    "Cruiser": 2000,
    "Power Cruiser": 2000,
    "Électrique": 2000,
    "Custom": 2000,
    "Scooter": 1500,
    "Scooter/Trail": 1500,
    "Trail Routier": 1800,
    "Motocross": 1500,
    "Enduro": 1500,
    "Supermoto": 1500,
    "Scooter urbain": 1500,
    "Scooter à grandes roues": 1500,
    "Scooter GT à grandes roues": 1500,
    "Maxi-scooter": 1500,
    "Maxi-scooter compact": 1500,
    "Scooter à trois roues": 1500,
    "Scooter sportif": 1500,
    "Scooter urbain compact": 1500,
    "Scooter léger": 1500,
    "Scooter classique": 1500,
    "Classique": 2000,
    "Café Racer": 2000,
    "Scrambler": 1800,
    "Adventure": 1800,
    "Adventure/Touring": 2000,
    "Scooter GT": 1500,
    "Scooter urbain sportif": 1500,
    "Scooter premium": 2000,
    "Scooter électrique": 2000
}

# Plafonds intermédiaires et conditions pour les voitures
plafonds_intermediaires_voitures = {
    "Citadine": {"plafond": 900, "conditions": "+120 000 km ou historique d'entretien partiel"},
    "Berline compacte": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Monospace": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Berline": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "SUV": {"plafond": 1200, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Utilitaire": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Break": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Coupé cabriolet": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Coupé": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Berline premium": {"plafond": 1300, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Citadine premium": {"plafond": 900, "conditions": "+120 000 km ou historique d'entretien partiel"},
    "SUV premium": {"plafond": 1300, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Break premium": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Break compact": {"plafond": 1000, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "SUV compact": {"plafond": 1200, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Berline luxe": {"plafond": 1300, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "SUV luxe": {"plafond": 1300, "conditions": "+150 000 km ou historique d'entretien partiel"},
    "Micro-citadine": {"plafond": 900, "conditions": "+120 000 km ou historique d'entretien partiel"}
}

# Plafonds intermédiaires et conditions pour les motos
plafonds_intermediaires_motos = {
    "Roadster": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Sportive": {"plafond": 1300, "conditions": "+30 000 km ou historique d'entretien partiel"},
    "Supermotard": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Trail": {"plafond": 1100, "conditions": "+70 000 km ou historique d'entretien partiel"},
    "Sport-Touring": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Touring": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Trail Sportif": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Roadster Néorétro": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Cruiser": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Power Cruiser": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Électrique": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Custom": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Scooter": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter/Trail": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Trail Routier": {"plafond": 1100, "conditions": "+70 000 km ou historique d'entretien partiel"},
    "Motocross": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Enduro": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Supermoto": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter urbain": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter à grandes roues": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter GT à grandes roues": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Maxi-scooter": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Maxi-scooter compact": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter à trois roues": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter sportif": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter urbain compact": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter léger": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter classique": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Classique": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Café Racer": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Scrambler": {"plafond": 1100, "conditions": "+70 000 km ou historique d'entretien partiel"},
    "Adventure": {"plafond": 1100, "conditions": "+70 000 km ou historique d'entretien partiel"},
    "Adventure/Touring": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Scooter GT": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter urbain sportif": {"plafond": 900, "conditions": "+60 000 km ou historique d'entretien partiel"},
    "Scooter premium": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"},
    "Scooter électrique": {"plafond": 1300, "conditions": "+100 000 km ou historique d'entretien partiel"}
}

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

    # Ajout du coefficient pour le type de transmission
    prix_final *= coeff_transmission_voiture.get(vehicule.transmission.capitalize(), 1.0)

    tarif_3mois = round(prix_final, 2)

    # Ajouter les plafonds maximum et intermédiaire à la réponse
    plafond_max = plafonds_max_voitures.get(vehicule.categorie, 0)
    plafond_intermediaire = plafonds_intermediaires_voitures.get(vehicule.categorie, {}).get("plafond", 0)
    conditions = plafonds_intermediaires_voitures.get(vehicule.categorie, {}).get("conditions", "")
    reponse = {
        "eligibilite": "yes",
        "tarif_3mois": tarif_3mois,
        "plafond_max": plafond_max,
        "plafond_intermediaire": plafond_intermediaire,
        "conditions": conditions
    }
    return reponse

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

    # Ajout du coefficient pour le type de transmission
    prix_final *= coeff_transmission_moto.get(vehicule.transmission.lower(), 1.0)

    # Ajouter les plafonds maximum et intermédiaire à la réponse
    plafond_max = plafonds_max_motos.get(vehicule.categorie, 0)
    plafond_intermediaire = plafonds_intermediaires_motos.get(vehicule.categorie, {}).get("plafond", 0)
    conditions = plafonds_intermediaires_motos.get(vehicule.categorie, {}).get("conditions", "")
    reponse = {
        "eligibilite": "yes",
        "tarif_3mois": round(prix_final, 2),
        "plafond_max": plafond_max,
        "plafond_intermediaire": plafond_intermediaire,
        "conditions": conditions
    }
    return reponse

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
