import pandas as pd
import numpy as np

def detect_fair_value_gaps(df: pd.DataFrame, threshold: float = 0.0) -> pd.DataFrame:
    """
    Detects Bullish and Bearish Fair Value Gaps (FVG).
    A FVG is a 3-candle pattern showing liquidity imbalance.
    
    - Bullish FVG: Low[i] > High[i-2] (Gap created up)
    - Bearish FVG: High[i] < Low[i-2] (Gap created down)
    Note: Properly shifted for feature engineering (i is current candle).
    """
    df = df.copy()
    
    # We look at the gap formed by the PREVIOUS completed candle pattern.
    # To know if we HAVE a FVG at index 'i', we analyze candles i, i-1, i-2.
    # Actually, standard FVG is usually defined after candle i closes.
    # Bull FVG: Low[i] > High[i-2].
    
    # 1. Calculate Gaps
    # Bull IF: Low[i] > High[i-2] -> Gap = Low[i] - High[i-2]
    # Bear IF: High[i] < Low[i-2] -> Gap = Low[i-2] - High[i]
    
    # Using 'shift' to align with previous candles relative to current row 'i'
    # Row i is the "third" candle closing.
    prev_high_2 = df['High'].shift(2)
    prev_low_2 = df['Low'].shift(2)
    
    # Bullish Imbalance
    df['FVG_Bull'] = df['Low'] - prev_high_2
    df['Is_FVG_Bull'] = (df['FVG_Bull'] > threshold).astype(int)
    
    # Bearish Imbalance
    df['FVG_Bear'] = prev_low_2 - df['High']
    df['Is_FVG_Bear'] = (df['FVG_Bear'] > threshold).astype(int)
    
    # 2. Features for AI: "Distance to last FVG" or "Recent FVG Intensity"
    # Ideally we'd track unmitigated FVGs, but for MVP we use a rolling presence.
    # "Did a FVG occur in the last 3 days?"
    df['Recent_FVG_Bull'] = df['Is_FVG_Bull'].rolling(3).max().fillna(0)
    df['Recent_FVG_Bear'] = df['Is_FVG_Bear'].rolling(3).max().fillna(0)
    
    return df[['Is_FVG_Bull', 'Is_FVG_Bear', 'Recent_FVG_Bull', 'Recent_FVG_Bear']]
