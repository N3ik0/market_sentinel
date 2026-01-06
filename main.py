#page1

from src.data_loader import DataLoader

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

    print(f"Prêt à travailler sur {len(data)} bougies pour {ticker}")

if __name__ == "__main__":
    main()