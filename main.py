#page1

from src.data_loader import DataLoader

def main():
    # Initialisation pour Nvidia
    ticker = "NVDA"
    loader = DataLoader(ticker)

    # Récupération des données (1an, par jour)
    data = loader.fetch_data(period= "1y", interval="1d")

    # Vérification rapide
    if not data.empty:
        print(f'\n--- Aperçu des données pour {ticker} ---')
        print(data.head())
    else:
        print(f'[!] Échec de la récupération.')

if __name__ == "__main__":
    main()