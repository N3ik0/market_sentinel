import pandas as pd
import pandas_ta as ta

def add_momentum_features(df: pd.DataFrame, prefix: str = "") -> pd.DataFrame:
    """
    Adds momentum indicators to the DataFrame.
    
    Args:
        df: Input DataFrame with OHLCv data.
        prefix: Optional prefix for column names (e.g. "1h_", "4h_").
    
    Returns:
        DataFrame with added momentum features.
    """
    # 1. RSI
    rsi14 = ta.rsi(df['Close'], length=14)
    if rsi14 is not None:
        df[f'{prefix}RSI_14'] = rsi14
        
    rsi20 = ta.rsi(df['Close'], length=20)
    if rsi20 is not None:
        df[f'{prefix}RSI_20'] = rsi20

    # 2. Stochastic
    # stoch returns two columns: STOCHk_14_3_3, STOCHd_14_3_3 (default)
    stoch = ta.stoch(df['High'], df['Low'], df['Close'], k=14, d=3, smooth_k=3)
    if stoch is not None:
        # Rename to match user request better or keep standard
        # User asked for stoch_k14 and stoch_d14
        # pandas_ta default columns are STOCHk_..., STOCHd_...
        # We rename the found columns
        stoch_k_cols = [c for c in stoch.columns if c.startswith('STOCHk')]
        stoch_d_cols = [c for c in stoch.columns if c.startswith('STOCHd')]
        
        if stoch_k_cols and stoch_d_cols:
            df[f'{prefix}Stoch_K14'] = stoch[stoch_k_cols[0]]
            df[f'{prefix}Stoch_D14'] = stoch[stoch_d_cols[0]]

    # 3. MACD
    # User asked for macd_line, macd_signal, macd_hist
    macd = ta.macd(df['Close'])
    if macd is not None:
        # Columns: MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        # k -> line, s -> signal, h -> hist
        macd_line_cols = [c for c in macd.columns if c.startswith('MACD_')]
        macd_hist_cols = [c for c in macd.columns if c.startswith('MACDh_')]
        macd_signal_cols = [c for c in macd.columns if c.startswith('MACDs_')]
        
        if macd_line_cols and macd_hist_cols and macd_signal_cols:
            df[f'{prefix}MACD_Line'] = macd[macd_line_cols[0]]
            df[f'{prefix}MACD_Signal'] = macd[macd_signal_cols[0]]
            df[f'{prefix}MACD_Hist'] = macd[macd_hist_cols[0]]

    # 4. CCI
    cci = ta.cci(df['High'], df['Low'], df['Close'], length=20)
    if cci is not None:
        df[f'{prefix}CCI_20'] = cci

    # 5. Williams R
    willr = ta.willr(df['High'], df['Low'], df['Close'], length=14)
    if willr is not None:
        df[f'{prefix}WillR_14'] = willr

    # 6. ROC (Rate of Change)
    roc5 = ta.roc(df['Close'], length=5)
    if roc5 is not None:
        df[f'{prefix}ROC_5'] = roc5
        
    roc10 = ta.roc(df['Close'], length=10)
    if roc10 is not None:
        df[f'{prefix}ROC_10'] = roc10

    # 7. Momentum Rank 5d
    # "mom_rank5d" -> We interpret this as Time Series Rank of 5-day Momentum over a window (e.g. 20 or 252?)
    # Or just 5-day Momentum (which is ROC/Close diff).
    # Given the user says "rank", and "vol_rank20d", it's likely a percentile rank.
    # We'll use a rolling window for rank, say 126 days (6 months) or 20 days.
    # Let's use 60 days as a robust window for rank.
    # FIX: Ensure we have enough data for the window
    if len(df) > 65: # 60 window + 5 lag
        mom5 = ta.mom(df['Close'], length=5)
        if mom5 is not None:
            df[f'{prefix}MOM_Rank5d'] = mom5.rolling(window=60).rank(pct=True)

    return df
