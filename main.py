print("[*] Sentinel MVP - Mode Entraînement & Publication Notion")
import os
from dotenv import load_dotenv
from src.data_loader import DataLoader
from src.features import FeatureEngineer
from src.model import MarketModel
from src.risk_manager import RiskManager
from src.notion_publisher import NotionPublisher

# 1. CHARGEMENT DES VARIABLES D'ENVIRONNEMENT
# Charge le Token et l'ID de la Database depuis ton fichier .env
load_dotenv()

def main():
    # PARAMÈTRES DU MVP
    ticker = "TSLA"
    period = "5y" 
    interval = "1d"

    print(f"[*] Onboarding du MVP sur {ticker} ({period})...")

    # 2. CHARGEMENT & PRÉPARATION DES DONNÉES
    loader = DataLoader(ticker)
    data = loader.fetch_data(period=period, interval=interval)
    loader.save_to_parquet()

    fe = FeatureEngineer(data)
    data_enriched = fe.add_all_features()
    data_final = fe.add_target(horizon=5)

    # 3. ENTRAÎNEMENT DU MODÈLE XGBOOST
    model = MarketModel()
    model.train(data_final)

    # 4. ANALYSE DES COMPÉTENCES (Importance des features)
    model.get_feature_importance()

    # 5. PRÉDICTION LIVE
    last_row = data_enriched.tail(1)
    current_features = last_row[model.features]
    prediction = model.model.predict(current_features)[0]

    # 6. GÉNÉRATION DU SCÉNARIO (Risk Management)
    rm = RiskManager(rr_ratio=2.0, atr_multiplier=2.0)
    plan = rm.generate_scenario(
        ticker=ticker, 
        current_price=last_row['Close'].values[0], 
        prediction=prediction, 
        df=data_enriched
    )

    # 7. PUBLICATION VERS NOTION
    # Récupération des clés depuis le .env
    token = os.getenv("NOTION_TOKEN")
    db_id = os.getenv("ID_DB_SENTINEL")
    
    # Détermination de la confiance basée sur tes rapports de classification
    # Précision ~65% pour la hausse, ~42% pour la baisse
    confidence_score = 0.65 if prediction == 1 else 0.42

    if token and db_id:
        try:
            publisher = NotionPublisher(token, db_id)
            publisher.publish_plan(plan, confidence=confidence_score)
            print(f"[+] Diagnostic terminé et publié sur Notion pour {ticker}")
        except Exception as e:
            print(f"[!] Erreur lors de la publication Notion : {e}")
    else:
        print("[!] Erreur : NOTION_TOKEN ou ID_DB_SENTINEL manquant dans le .env")

    # 8. RÉSUMÉ CONSOLE RAPIDE
    print("\n" + "═"*45)
    print(f"Signal IA : {plan['direction']} | Prix : {plan['entry']}$")
    print(f"SL : {plan['sl']}$ | TP : {plan['tp']}$")
    print("═"*45 + "\n")

if __name__ == "__main__":
    main()