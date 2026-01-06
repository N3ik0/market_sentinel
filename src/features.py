import pandas as pd
import pandas_ta as ta

class FeatureEngineer:
    """Module pour transformer les prix bruts en indicateurs techniques."""
    
    def __init__(self, df: pd.DataFrame):
        # On travaille sur une copie pour éviter de modifier le DF original par erreur
        self.df = df.copy()

    def add_all_features(self) -> pd.DataFrame:
        """Ajoute tous les indicateurs nécessaires."""
        
        # 1. RSI : Pour savoir si on est en sur-achat (>70) ou sur-vente (<30)
        self.df['RSI'] = ta.rsi(self.df['Close'], length=14)

        # 2. EMA (Exponential Moving Averages) : Pour la tendance court et moyen terme
        self.df['EMA_20'] = ta.ema(self.df['Close'], length=20)
        self.df['EMA_50'] = ta.ema(self.df['Close'], length=50)

        # 3. MACD : Pour le momentum
        macd = ta.macd(self.df['Close'])
        # Le MACD renvoie plusieurs colonnes, on les fusionne au DF
        self.df = pd.concat([self.df, macd], axis=1)

        # On supprime les lignes vides créées par les calculs (ex: les 20 premières lignes pour une EMA 20)
        self.df.dropna(inplace=True)
        
        return self.df