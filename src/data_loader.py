# Module de récupération des données
import os
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

        # Si Yahoo renvoie un MultiIndex (Ticker en sous-colonne), on le simplifie
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        # On s'assure que l'index est bien au format Datetime (propre pour le ML)
        df.index = pd.to_datetime(df.index)

        self.data = df
        print(f"[+] {len(self.data)} lignes récupérées.")
        return self.data

        """ Récupération des données multi-timeframes
        """
        def fetch_mtf_data(self, intervals=["1d", "4h", "1h"]):
            mtf_data = {}
            for inter in intervals:
                # On ajuste la période selon l'intervalle pour éviter les erreurs d'API
                period = "2y" if inter == "1d" else "60d" 
                mtf_data[inter] = self.fetch_data(period=period, interval=inter)
            return mtf_data

    def save_to_parquet(self, folder: str = "data") -> str:
        """ Sauvegarde des données en parquet. 
        Args : 
            folder: Données à sauvegardées
        """

        if self.data is None or self.data.empty:
            print(f"[!] Erreur : les données à sauvegarder sont vides pour {self.ticker}")
            return ""

        # Crétaion du dossier
        os.makedirs(folder, exist_ok=True)

        # Construction du chemin : "data/Symbole.parquet"
        file_path = os.path.join(folder, f"{self.ticker}.parquet")

        try:
            # Sauvegarde binaire (rapide)
            self.data.to_parquet(file_path, engine='pyarrow')
            print(f"[+] Données sauvegardées : {file_path}")
            return file_path
        except Exception as e:
            print(f"[!] Échec de la sauvegarde : {e}")
            return ""

    def load_from_parquet(self, folder: str="data") -> pd.DataFrame:
        """ Charge les données depuis un fichier local s'il existe. """
        file_path = os.path.join(folder, f"{self.ticker}.parquet")

        if os.path.exists(file_path):
            try:
                self.data = pd.read_parquet(file_path)
                print(f"[+] Données chargées localement pour {self.ticker}")
                return self.data
            except Exception as e:
                print(f"[!] Erreur lors de la lecture du fichier : {e}")
                return pd.DataFrame()
        else: 
            print(f"[?] Aucun fichier local trouvé pour {self.ticker}")
            return pd.DataFrame()