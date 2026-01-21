import pandas as pd
import pandas_ta as ta

def add_volume_features(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """Adds volume indicators."""
    
    # Volume is usually already present, but we might want Log Volume or Norm Volume
    # Volume is usually already present, but we might want Log Volume or Norm Volume
    # Item 8: volume_sma20
    if 'Volume' in df.columns:
        vol_sma20 = ta.sma(df['Volume'], length=20)
        if vol_sma20 is not None:
            df[f'{prefix}Volume_SMA20'] = vol_sma20
        
        # OBV (Item 30)
        obv = ta.obv(df['Close'], df['Volume'])
        if obv is not None:
            df[f'{prefix}OBV'] = obv
        
        # OBV SMA 20 (Item 40)
        if f'{prefix}OBV' in df.columns:
            obv_sma20 = ta.sma(df[f'{prefix}OBV'], length=20)
            if obv_sma20 is not None:
                df[f'{prefix}OBV_SMA20'] = obv_sma20
            
    return df
