import pandas as pd
import numpy as np

def add_stats_features(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """Adds statistical features (Returns, Range, etc)."""
    
    # Log Returns
    # ln(Pt / Pt-1)
    df['Log_Ret'] = np.log(df['Close'] / df['Close'].shift(1))
    
    # Lags 1 to 5 (Items 1-5)
    # Note: 'Log_Ret' itself is the return of the current bar.
    # 'Log_Ret_Lag1' is the return of the previous bar.
    for i in range(1, 6):
        df[f'{prefix}Log_Ret_Lag{i}'] = df['Log_Ret'].shift(i)
        
    # HL Pct (Item 6)
    # (High - Low) / Close
    df[f'{prefix}HL_Pct'] = (df['High'] - df['Low']) / df['Close']
    
    # Range Pct 20 (Item 50)
    # Interpreted as (RollingHigh20 - RollingLow20) / Close
    # A measure of the 20-day price channel width relative to price.
    roll_high = df['High'].rolling(20).max()
    roll_low = df['Low'].rolling(20).min()
    df[f'{prefix}Range_Pct20'] = (roll_high - roll_low) / df['Close']
    
    return df
