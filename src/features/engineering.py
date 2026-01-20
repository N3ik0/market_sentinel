import pandas as pd
import pandas_ta as ta
import numpy as np
from src.features.smc.structure import detect_swing_points
from src.features.smc.fvg import detect_fair_value_gaps

class FeatureEngineer:
    """Handles technical analysis and feature generation."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def generate_all(self) -> pd.DataFrame:
        """Main pipeline to add all features."""
        self._add_momentum()
        self._add_trend()
        self._add_volatility()
        self._add_structure()
        
        self.df.dropna(inplace=True)
        return self.df

    def _add_momentum(self):
        """Momentum indicators."""
        # RSI
        self.df['RSI'] = ta.rsi(self.df['Close'], length=14)
        # MACD
        macd = ta.macd(self.df['Close'])
        self.df = pd.concat([self.df, macd], axis=1)
        # Returns
        self.df['Returns'] = self.df['Close'].pct_change()

    def _add_trend(self):
        """Trend & Filter indicators."""
        self.df['EMA_20'] = ta.ema(self.df['Close'], length=20)
        self.df['EMA_50'] = ta.ema(self.df['Close'], length=50)
        self.df['Dist_EMA_20'] = (self.df['Close'] - self.df['EMA_20']) / self.df['EMA_20']
        # Trend signal: 1 if bullish, 0 if bearish
        self.df['Trend_Signal'] = (self.df['EMA_20'] > self.df['EMA_50']).astype(int)
        
        # ADX for Range Filter (if ADX < 25 => Range)
        adx = ta.adx(self.df['High'], self.df['Low'], self.df['Close'], length=14)
        self.df = pd.concat([self.df, adx], axis=1)

    def _add_volatility(self):
        """Volatility indicators."""
        self.df['ATR'] = ta.atr(self.df['High'], self.df['Low'], self.df['Close'], length=14)

    def _add_structure(self):
        """Market Structure (SMC) features."""
        # 1. Rolling High/Low (Simplified Support/Resistance)
        self.df['Rolling_High'] = self.df['High'].rolling(window=20).max()
        self.df['Rolling_Low'] = self.df['Low'].rolling(window=20).min()
        self.df['BOS_High'] = self.df['Close'] / self.df['Rolling_High'].shift(1)

        # 2. Swing Points (Fractals)
        sh, sl = detect_swing_points(self.df, window=5)
        self.df['Swing_High_Confirmed'] = sh
        self.df['Swing_Low_Confirmed'] = sl
        
        # 3. Fair Value Gaps (Imbalances)
        df_fvg = detect_fair_value_gaps(self.df)
        self.df = pd.concat([self.df, df_fvg], axis=1)

        # 4. Body Strength
        body = (self.df['Close'] - self.df['Open']).abs()
        total_range = self.df['High'] - self.df['Low']
        self.df['Body_Strength'] = body / total_range

    def add_target(self, horizon: int = 5, threshold: float = 0.02) -> pd.DataFrame:
        """
        Create multi-class target.
        0: Neutral / Range (Return between -2% and +2%, or Low ADX)
        1: Bullish (Return > +2%)
        2: Bearish (Return < -2%)
        """
        self.df['Future_Close'] = self.df['Close'].shift(-horizon)
        self.df['Future_Return'] = (self.df['Future_Close'] - self.df['Close']) / self.df['Close']
        
        conditions = [
            (self.df['Future_Return'] > threshold), # Strong Up
            (self.df['Future_Return'] < -threshold)# Strong Down
        ]
        choices = [1, 2]
        
        # Default is 0 (Neutral)
        self.df['Target'] = np.select(conditions, choices, default=0)
        
        # ADX Filter: If Trend is weak (ADX < 20), Force Target 0 to avoid noise
        # ADX_14 is the standard column name from pandas_ta
        if 'ADX_14' in self.df.columns:
            self.df.loc[self.df['ADX_14'] < 20, 'Target'] = 0
            
        self.df.dropna(inplace=True)
        return self.df
