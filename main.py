print("[*] Sentinel MVP - Mode Entraînement Qualitatif")
from src.data_loader import DataLoader
from src.features import FeatureEngineer
from src.model import MarketModel

def main():
    # 1. PARAMÈTRES DU MVP
    ticker = "NVDA"
    # On passe à 5 ans pour donner de la profondeur à XGBoost
    period = "5y" 
    interval = "1d"

    print(f"[*] Onboarding du MVP sur {ticker} ({period})...")

    # 2. CHARGEMENT DES DONNÉES
    loader = DataLoader(ticker)
    # On force le fetch pour avoir les 5 ans si le parquet local est plus vieux
    data = loader.fetch_data(period=period, interval=interval)
    loader.save_to_parquet()

    # 3. FEATURE ENGINEERING
    # On prépare les indicateurs techniques
    fe = FeatureEngineer(data)
    data_enriched = fe.add_all_features()
    
    # On définit la cible à 5 jours (horizon de prédiction)
    data_final = fe.add_target(horizon=5)

    # 4. ENTRAÎNEMENT DU MODÈLE XGBOOST
    # C'est ici que ton nouveau src/model.py avec XGBoost va travailler
    model = MarketModel()
    model.train(data_final)

    # 5. ANALYSE DES COMPÉTENCES DU MODÈLE
    # Affichage des indicateurs qui influencent le plus les décisions
    model.get_feature_importance()

    # 6. VÉRIFICATION DU SIGNAL ACTUEL (Live)
    # On prend la dernière ligne connue pour voir ce que l'IA dit aujourd'hui
    last_row = data_enriched.tail(1)
    # On s'assure d'utiliser les mêmes features que lors de l'entraînement
    current_features = last_row[model.features]
    prediction = model.model.predict(current_features)[0]

    print("\n" + "="*40)
    print(f"   DIAGNOSTIC MVP - {ticker}")
    print("="*40)
    print(f"Signal IA (J+5) : {'🚀 HAUSSIER' if prediction == 1 else '📉 BAISSIER'}")
    print(f"Prix actuel    : {round(last_row['Close'].values[0], 2)}$")
    print(f"RSI actuel     : {round(last_row['RSI'].values[0], 2)}")
    print("="*40)

if __name__ == "__main__":
    main()