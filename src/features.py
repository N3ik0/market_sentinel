import pandas as pd
import pandas_ta as ta

class FeatureEngineer:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        # Toujours travailler sur une copi du document pour ne pas corrompres les datas

    def add_all_features(self) -> pd.DataFrame:
        """ Point d'entrée principal qui appelle les dif modules """
        
        self._add_momentum_features()
        self._add_trend_features()
        self._add_volatility_features()
        self._add_structure_features()

        # Nettoyage final
        self.df.dropna(inplace=True)
        return self.df

# ------------ FONCTIONS ------------ #

    def _add_momentum_features(self):
        """ Indicateurs de force du mouvement. """
        # RSI
        self.df['RSI'] = ta.rsi(self.df['Close'], length=14)
        # MACD
        macd = ta.macd(self.df['Close'])
        self.df = pd.concat([self.df, macd], axis=1)
        # Rendements
        self.df['Returns'] = self.df['Close'].pct_change()

    def _add_trend_features(self):
        """ Indicateurs de direction de fond. """
        self.df['EMA_20'] = ta.ema(self.df['Close'], length=20)
        self.df['EMA_50'] = ta.ema(self.df['Close'], length=50)
        self.df['Dist_EMA_20'] = (self.df['Close'] - self.df['EMA_20'] / self.df['EMA_20'])
        # Signal de croisement : 1 si haussier, -1 si baissier
        self.df['Trend_Signal'] = (self.df['EMA_20'] > self.df['EMA_50']).astype(int)

    def _add_volatility_features(self):
        """Indicateurs de nervosité du marché."""
        # ATR : Average True Range (Volatilité réelle)
        self.df['ATR'] = ta.atr(self.df['High'], self.df['Low'], self.df['Close'], length=14)

    def _add_structure_features(self):
        """
        VARIABLES AVANCÉES : Structure de marché (BOS, Gaps, etc.)
        C'est ici que ton modèle va apprendre à lire le 'Price Action'.
        """
        # 1. Plus haut / Plus bas des 20 derniers jours (Donne les zones de support/résistance)
        self.df['Rolling_High'] = self.df['High'].rolling(window=20).max()
        self.df['Rolling_Low'] = self.df['Low'].rolling(window=20).min()
        
        # 2. Distance par rapport au break de structure (BOS)
        # Si > 1, on a cassé le plus haut (Breakout)
        self.df['BOS_High'] = self.df['Close'] / self.df['Rolling_High'].shift(1)
        
        # 3. Taille du corps de la bougie vs mèches (Mouvements forts)
        body = (self.df['Close'] - self.df['Open']).abs()
        total_range = self.df['High'] - self.df['Low']
        self.df['Body_Strength'] = body / total_range

    def add_target(self, horizon: int = 5) -> pd.DataFrame:
        """Crée la cible pour l'entraînement."""
        self.df['Target_Price'] = self.df['Close'].shift(-horizon)
        self.df['Target'] = (self.df['Target_Price'] > self.df['Close']).astype(int)
        self.df.dropna(inplace=True)
        return self.df