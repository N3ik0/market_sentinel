import pandas as pd
import numpy as np
from typing import Tuple

def detect_swing_points(df: pd.DataFrame, window: int = 5) -> Tuple[pd.Series, pd.Series]:
    """
    Identifies Swing Highs and Swing Lows (Fractals).
    A Swing High is a High greater than 'window' highs on left and right.
    
    CRITICAL FOR AI: We cannot peak into the future.
    A swing point at time 't' is only CONFIRMED at time 't + window'.
    So at time 'current', we only know if a swing happened 'window' candles ago.
    """
    # 1. Identification (Center-based)
    # rolling(window*2+1, center=True) checks left and right neighbors.
    # This operation mathematically uses future data relative to index 'i'.
    # e.g. at index 100, rolling centered looks at 105.
    
    rolling_max = df['High'].rolling(window=window*2+1, center=True).max()
    rolling_min = df['Low'].rolling(window=window*2+1, center=True).min()
    
    is_swing_high = (df['High'] == rolling_max)
    is_swing_low = (df['Low'] == rolling_min)
    
    # 2. Shift for Real-Time Availability (Lagging feature)
    # We only know it WAS a swing high 'window' bars later.
    # So we shift the result forward by 'window' steps.
    # Feature meaning: "Did we confirm a Swing High exactly 'window' days ago?"
    feature_swing_high = is_swing_high.shift(window).fillna(0).astype(int)
    feature_swing_low = is_swing_low.shift(window).fillna(0).astype(int)
    
    return feature_swing_high, feature_swing_low
