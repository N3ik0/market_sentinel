import pandas as pd
import pandas_ta as ta

def add_volatility_features(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """
    Adds volatility indicators.
    """
    # ATR
    # Items 31, 32
    # ATR
    # Items 31, 32
    atr14 = ta.atr(df['High'], df['Low'], df['Close'], length=14)
    if atr14 is not None:
        df[f'{prefix}ATR_14'] = atr14

    atr20 = ta.atr(df['High'], df['Low'], df['Close'], length=20)
    if atr20 is not None:
        df[f'{prefix}ATR_20'] = atr20
    
    # Bollinger Bands
    # Items 33, 34, 35
    # bb_width_daily, bb_pb_daily (percent b), bb_ub_dist (distance to upper band?)
    bb = ta.bbands(df['Close'], length=20, std=2.0)
    if bb is not None:
        # Columns: BBL_20_2.0, BBM_20_2.0, BBU_20_2.0, BBB_20_2.0 (Bandwidth), BBP_20_2.0 (Percent B)
        # Note: pandas_ta naming varies by version, but usually consistent.
        # Bandwidth
        bw_cols = [c for c in bb.columns if c.startswith('BBB')]
        # Percent B
        pb_cols = [c for c in bb.columns if c.startswith('BBP')]
        # Upper Band
        ub_cols = [c for c in bb.columns if c.startswith('BBU')]
        
        if bw_cols and pb_cols and ub_cols:
            df[f'{prefix}BB_Width'] = bb[bw_cols[0]]
            df[f'{prefix}BB_Pb'] = bb[pb_cols[0]] # Percent B
            
            # UB Dist: Distance from Close to Upper Band? or High to Upper Band?
            # Usually (Ref - UB). Let's use Close - UB.
            df[f'{prefix}BB_UB_Dist'] = df['Close'] - bb[ub_cols[0]]

    # Volatility Rank 20d
    # Item 42: vol_rank20d
    # We define Volatility as Rolling Std Dev of Returns over 20d, then Percent Rank?
    # Or is it Rank of the current Volatility value compared to history?
    # "Rank of Volatility"
    # 1. Calc Returns
    ret = df['Close'].pct_change()
    # 2. Calc Volatility (Std Dev of Returns)
    vol_20 = ret.rolling(20).std()
    # 3. Rank of this Volatility in the last N periods (e.g. 1 Year = 252)
    # FIX: Ensure we have enough data for 252 rolling window
    if len(df) > 272: # 252 window + 20 lag
        df[f'{prefix}Vol_Rank20d'] = vol_20.rolling(window=252).rank(pct=True)
    
    # VIX Proxy and Dispersion Univ
    # These require external data (VIX or S&P500).
    # If the user provides a 'VIX' column, we use it.
    if 'VIX' in df.columns:
         df[f'{prefix}VIX_Proxy'] = df['VIX']
    
    # Dispersion Univ (Std Ret S&P)
    # If S&P500 returns available... placeholder
    
    return df
