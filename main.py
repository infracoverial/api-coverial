from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# ✅ Configuration CORS pour autoriser Framer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://framer.com", "https://*.framer.app"],  # Autoriser uniquement Framer
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Autoriser les requêtes GET, POST et OPTIONS
    allow_headers=["Content-Type", "Authorization"],  # Autoriser les en-têtes nécessaires
)

# ✅ Modèle des données envoyées par le client
class VehicleInfo(BaseModel):
    kilometrage: int
    age: int
    taille: str
    proprietaires: int
    historique_entretien: str
    etat: str
    marque: str

# ✅ Coefficients multiplicateurs
coefficients = {
    "kilometrage": {50000: 1.0, 100000: 1.1, 150000: 1.2, 200000: 1.4, 999999: 1.6},
    "age": {3: 1.0, 5: 1.1, 8: 1.2, 12: 1.4, 999: 1.6},
    "taille": {"Citadine": 0.9, "Berline": 1.0, "SUV": 1.1},
    "proprietaires": {1: 1.0, 3: 1.1, 999: 1.3},
    "historique_entretien": {"complet": 0.9, "partiel": 1.1, "inconnu": 1.3},
    "etat": {"tres_bon": 0.95, "quelques_defauts": 1.0, "nombreux_defauts": 1.1, "problemes_mecaniques": 1.3},
    "marque": {"Renault": 1.0, "Volkswagen": 1.1, "Audi": 1.2, "Mercedes": 1.2, "BMW": 1.2}
}

# ✅ Fonction pour appliquer les coefficients
def calculer_prix(vehicule: VehicleInfo):
    prix_base = 120
    prix_final = prix_base

    # Appliquer les coefficients
    for critere, valeurs in coefficients.items():
        valeur_vehicule = getattr(vehicule, critere)

        if isinstance(valeurs, dict):  # Si c'est un dict (catégories fixes)
            if isinstance(valeur_vehicule, int):  # Pour les valeurs numériques
                for seuil, coef in sorted(valeurs.items()):
                    if valeur_vehicule <= seuil:
                        prix_final *= coef
                        break
            else:  # Pour les catégories fixes (ex: marque, taille)
                prix_final *= valeurs.get(valeur_vehicule, 1.0)

    return round(prix_final, 2)

# ✅ Route API pour calculer le prix de la garantie avec logs
@app.post("/calcul_prix/")
async def get_price(vehicule: VehicleInfo):
    prix = calculer_prix(vehicule)
    response = {"prix_garantie": prix}

    print("🔍 Données reçues :", vehicule.dict())  # Voir les données reçues
    print("🔍 Prix calculé :", prix)  # Vérifier le calcul
    print("🔍 Réponse envoyée :", response)  # Vérifier la réponse envoyée

    return response