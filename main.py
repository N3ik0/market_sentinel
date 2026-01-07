#page1

from src.data_loader import DataLoader
from src.features import FeatureEngineer
from src.model import MarketModel

def main():
    ticker = "NVDA"
    loader = DataLoader(ticker)

    # Test de chargemnt des données locales dans un premier temps
    data = loader.load_from_parquet()

    # Si vide, on dl & sauvegarde
    if data.empty:
        print("[!] Données locales absences. Téléchargement...")
        data = loader.fetch_data(period = "2y", interval="1d")
        loader.save_to_parquet()

    # Récuperation des features (graph)
    fe = FeatureEngineer(data)
    data_enriched = fe.add_all_features()
    data_final = fe.add_target(horizon=5)
    print("\n--- Aperçu de la Target ---")
    print(data_final[['Close', 'Target']].tail(10))

    print(f"Données enrichies pour {ticker}")
    print(data_enriched.tail())
    print(f"Colonnes disponibles : {data_enriched.columns.tolist()}")

    model = MarketModel()
    model.train(data_final)

if __name__ == "__main__":
    main()