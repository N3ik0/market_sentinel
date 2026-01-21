import pandas as pd
import pandas_ta as ta
import numpy as np

def add_trend_features(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """
    Adds trend indicators to the DataFrame.
    
    Args:
        df: Input DataFrame.
        prefix: Optional prefix (e.g. "Weekly_").
    
    Returns:
        DataFrame with added trend features.
    """
    # EC: Exponential Moving Averages
    # EC: Exponential Moving Averages
    ema10 = ta.ema(df['Close'], length=10)
    if ema10 is not None:
        df[f'{prefix}EMA_10'] = ema10
        
    ema20 = ta.ema(df['Close'], length=20)
    if ema20 is not None:
        df[f'{prefix}EMA_20'] = ema20
        
    ema50 = ta.ema(df['Close'], length=50)
    if ema50 is not None:
        df[f'{prefix}EMA_50'] = ema50

    # SMA: Simple Moving Averages
    sma5 = ta.sma(df['Close'], length=5)
    if sma5 is not None:
        df[f'{prefix}SMA_5'] = sma5
        
    sma20 = ta.sma(df['Close'], length=20)
    if sma20 is not None:
        df[f'{prefix}SMA_20'] = sma20
        
    sma50 = ta.sma(df['Close'], length=50)
    if sma50 is not None:
        df[f'{prefix}SMA_50'] = sma50
    
    # Ratchet up: SMA Ratio (Item 20: sma_ratio_50_20)
    # Assuming SMA50 / SMA20 or vice versa. Usually Short/Long or Long/Short.
    # List says "sma_ratio_50_20". I'll do SMA50 / SMA20.
    if f'{prefix}SMA_20' in df.columns and f'{prefix}SMA_50' in df.columns:
        df[f'{prefix}SMA_Ratio_50_20'] = df[f'{prefix}SMA_50'] / df[f'{prefix}SMA_20']

    # Crossovers
    # Item 17: crossover_ema10_20
    # We'll provide the State (1 if 10 > 20, 0 otherwise) 
    # and potentially the recent crossover event (change in state).
    # XGBoost likes continuous interaction, but explicit state helps.
    if f'{prefix}EMA_10' in df.columns and f'{prefix}EMA_20' in df.columns:
        df[f'{prefix}Crossover_EMA10_20'] = np.where(df[f'{prefix}EMA_10'] > df[f'{prefix}EMA_20'], 1, 0)

    # Slopes
    # Item 18, 19, 46, 47
    # Slope is usually calculating angle or linear regression slope over a window.
    # ta.slope returns slope of linear regression line over length n.
    # "Slope of SMA20" -> slope(sma20, 5?) or slope(sma20, 1 = diff)?
    # ta.slope(series, length) calculates slope over 'length' period.
    # I'll assume length=1 (just change) or length=5 (trend of the MA).
    # Usually "Slope of MA" implies the rate of change of the MA.
    # I'll use ta.slope with length=5 or 3. Let's use 5.
    if f'{prefix}SMA_20' in df.columns:
        slope_sma20 = ta.slope(df[f'{prefix}SMA_20'], length=5)
        if slope_sma20 is not None:
            df[f'{prefix}Slope_SMA20'] = slope_sma20
            
    if f'{prefix}EMA_20' in df.columns:
        slope_ema20 = ta.slope(df[f'{prefix}EMA_20'], length=5)
        if slope_ema20 is not None:
            df[f'{prefix}Slope_EMA20'] = slope_ema20

    # ADX
    # Items 43, 44, 45
    adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
    if adx is not None:
        # Columns: ADX_14, DMP_14, DMN_14
        adx_cols = [c for c in adx.columns if c.startswith('ADX')]
        if adx_cols:
            adx_col = adx_cols[0]
            df[f'{prefix}ADX_14'] = adx[adx_col]
            
            # Item 45: regime_trend (ADX>25)
            df[f'{prefix}Regime_Trend'] = np.where(df[f'{prefix}ADX_14'] > 25, 1, 0)

    return df
