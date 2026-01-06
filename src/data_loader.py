# Module de récupération des données

import yfinance as yf
import pandas as pd
from typing import Optional

class DataLoader: 
    """ Module responsable de l'extraction des market data """ 

    def __init__(self, ticker: str):
        self.ticker = ticker

    def fetch_data(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """ Récupération des données via Yahoo finance. 
        Args : 
            period : période des données
            interval : intervalle de collecte des données
        """ 
        print(f"[*] Téléchargement en cours des données pour {self.ticker} ...")

        df = yf.download(tickers=self.ticker, period=period, interval=interval)

        if df.empty:
            print(f"[!] Erreur : Aucun résultat pour {self.ticker}. Vérifier le symbole.")
            return pd.DataFrame()

        self.data = df
        print(f"[+] {len(self.data)} lignes récupérées.")
        return self.data

    