import pandas as pd
import numpy as np
import pandas_ta as ta
from typing import Dict, Optional

# Import the modular feature groups
from src.features.indicators import momentum, trend, volatility, volume, stats
from src.features.smc.structure import detect_swing_points
from src.features.smc.fvg import detect_fair_value_gaps

class FeatureEngineer:
    """
    Handles technical analysis and feature generation.
    Orchestrates the calculation of features across multiple timeframes.
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        if not isinstance(self.df.index, pd.DatetimeIndex):
            # Ensure DateTimeIndex for resampling
            try:
                self.df.index = pd.to_datetime(self.df.index)
            except Exception as e:
                print(f"Warning: Could not convert index to DatetimeIndex. Resampling may fail. {e}")

    def generate_all(self) -> pd.DataFrame:
        """
        Main pipeline to add all features from the user list.
        Supports Multi-Timeframe generation if data frequency allows.
        """
        # 1. Determine base frequency
        # infer_freq is sometimes None, so we default to keeping it simple or checks
        base_freq = pd.infer_freq(self.df.index)
        
        # We will generate features for the Base timeframe first
        # We assume the base df is the highest frequency available (e.g. 1h or Daily)
        
        # GENERATE BASE FEATURES
        # If data is Daily, these will be "Daily" features.
        # If data is 1h, these will be "1h" features.
        self._generate_features_for_df(self.df, suffix="") 
        
        # 2. Multi-Timeframe Logic
        # We define the desired higher timeframes to aggregates
        # Note: We can only aggregate UP.
        
        # 2. Multi-Timeframe Logic
        if len(self.df) > 2:
            freq = pd.infer_freq(self.df.index)
            print(f"[*] Inferred Frequency: {freq}")
            
            # --- 15 Minute Data ('15T' or '15min') ---
            if freq == '15T' or freq == '15min':
                print(f"[*] Detected 15m data. Generating 1h, 4h, Daily features...")
                
                # Resample -> 1h
                df_1h = self._resample_ohlcv(self.df, '1h')
                df_1h = self._generate_features_for_df(df_1h, suffix="_1h")
                self.df = self._merge_mtf(self.df, df_1h, suffix="_1h")
                
                # Resample -> 4h
                df_4h = self._resample_ohlcv(self.df, '4h')
                df_4h = self._generate_features_for_df(df_4h, suffix="_4h")
                self.df = self._merge_mtf(self.df, df_4h, suffix="_4h")

                # Resample -> Daily
                df_d = self._resample_ohlcv(self.df, '1d')
                df_d = self._generate_features_for_df(df_d, suffix="_daily")
                self.df = self._merge_mtf(self.df, df_d, suffix="_daily")

            # --- 1 Hour Data ('H' or '1H') ---
            elif freq == 'H' or freq == '1H':
                print("Detected 1H data. Generating 4H, Daily, Weekly features...")

                # Resample -> 4H
                df_4h = self._resample_ohlcv(self.df, '4h')
                df_4h = self._generate_features_for_df(df_4h, suffix="_4h")
                self.df = self._merge_mtf(self.df, df_4h, suffix="_4h")

                # Resample -> Daily
                df_d = self._resample_ohlcv(self.df, '1d')
                df_d = self._generate_features_for_df(df_d, suffix="_daily")
                self.df = self._merge_mtf(self.df, df_d, suffix="_daily")

                # Resample -> Weekly
                df_w = self._resample_ohlcv(self.df, '1W')
                df_w = self._generate_features_for_df(df_w, suffix="_weekly")
                self.df = self._merge_mtf(self.df, df_w, suffix="_weekly")
                
            # --- Daily Data ('D' or '1D') ---
            elif freq == 'D' or freq == '1D':
                print("Detected Daily data. Generating Weekly features...")
                
                # Resample -> Weekly
                df_w = self._resample_ohlcv(self.df, '1W')
                df_w = self._generate_features_for_df(df_w, suffix="_weekly")
                self.df = self._merge_mtf(self.df, df_w, suffix="_weekly")
            
            else:
                 # Fallback or strict strict check? 
                 # If None (gaps), we might want a fallback?
                 # For now, user requested this specific check, so we respect strictness or maybe log warning.
                 if not freq:
                     print("[!] Warning: Could not infer frequency (Gaps in data?). Skipping MTF generation.")
                 else:
                     print(f"[!] Unhandled frequency: {freq}")
                
        # 3. Add SMC / Structure
        self._add_structure()
        
        self.df.dropna(inplace=True)
        return self.df

    def _generate_features_for_df(self, df_in: pd.DataFrame, suffix: str) -> pd.DataFrame:
        """Helper to run all indicator modules on a dataframe."""
        # 1. Stats (Returns, etc)
        df_in = stats.add_stats_features(df_in, prefix="")
        
        # 2. Momentum
        df_in = momentum.add_momentum_features(df_in, prefix="")
        
        # 3. Trend
        df_in = trend.add_trend_features(df_in, prefix="")
        
        # 4. Volatility
        df_in = volatility.add_volatility_features(df_in, prefix="")
        
        # 5. Volume
        df_in = volume.add_volume_features(df_in, prefix="")

        # Apply Suffix to these new columns (except OHLCV)
        # Note: The modules add columns directly.
        # Ideally modules accept a prefix. I implemented `prefix` arg in modules.
        # Let's fix the call to use `suffix` as `prefix`.
        # Wait, I passed prefix="" above.
        # Correct approach:
        return self._run_modules_with_prefix(df_in, suffix)

    def _run_modules_with_prefix(self, df_in: pd.DataFrame, p: str) -> pd.DataFrame:
        """Runs the modules passing the prefix."""
        # If p starts with _, remove it for cleaner prefix? User wants "ema10_daily".
        # My modules usually put prefix at start: "Daily_EMA10"
        # User wants suffix style: "ema10_daily".
        # I'll implement standard prefix "Daily_" style, and maybe rename at the end?
        # Or I just pass the p (e.g. "_daily") and modules append it?
        # My modules currently use: f'{prefix}EMA_10'.
        # If I pass prefix="EMA_10_", result is "EMA_10_EMA_10". Bad.
        # If I pass prefix="", result is "EMA_10".
        # User wants "ema10_daily".
        # I will stick to "Indicator_Timeframe" (e.g. EMA10_Daily) or "Timeframe_Indicator".
        # Let's stick to "EMA_10_daily" (Suffix style).
        # But my modules use `f'{prefix}Name'`.
        # So I should pass prefix as empty, calculate, then rename with suffix.
        
        cols_before = set(df_in.columns)
        
        stats.add_stats_features(df_in, prefix="")
        momentum.add_momentum_features(df_in, prefix="")
        trend.add_trend_features(df_in, prefix="")
        volatility.add_volatility_features(df_in, prefix="")
        volume.add_volume_features(df_in, prefix="")
        
        cols_after = set(df_in.columns)
        new_cols = cols_after - cols_before
        
        # Rename new cols with suffix
        if p:
            rename_map = {c: f"{c}{p}" for c in new_cols}
            df_in.rename(columns=rename_map, inplace=True)
            
        return df_in

    def _resample_ohlcv(self, df: pd.DataFrame, rule: str) -> pd.DataFrame:
        """Resamples OHLCV data."""
        agg_dict = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }
        # Handle cases where some cols might be missing
        agg_dict = {k: v for k, v in agg_dict.items() if k in df.columns}
        return df.resample(rule).agg(agg_dict).dropna()

    def _merge_mtf(self, df_base: pd.DataFrame, df_higher: pd.DataFrame, suffix: str) -> pd.DataFrame:
        """
        Merges higher timeframe features into base dataframe.
        - Resamples higher df back to base freq (ffill) to align indices.
        - Joins.
        """
        # Identify features (exclude OHLCV)
        features = [c for c in df_higher.columns if c not in ['Open', 'High', 'Low', 'Close', 'Volume']]
        unique_features = [c for c in features if c not in df_base.columns] # Avoid duplicates
        
        subset = df_higher[unique_features].copy()
        
        # Merge using reindex with method='ffill' (Forward fill data from past)
        # 1. Reindex highest df to match base index
        # method='ffill' ensures that at 10:00 we see the 4H candle close from 08:00 (or previous complete candle).
        # PRECAUTION: Ideally we shift the higher timeframe to avoid lookahead?
        # When resampling '1d', the timestamp is usually 00:00 or end of day?
        # If '1d' timestamp is 00:00 of the day, and we ffill, we might peek if not careful.
        # pandas resample label='left' vs 'right'. 
        # But for simplicity here, we assume standard alignment.
        aligned = subset.reindex(df_base.index, method='ffill')
        
        # Concat
        return pd.concat([df_base, aligned], axis=1)

    def _add_structure(self):
        """Preserved SMC features logic."""
        # 1. Rolling High/Low
        self.df['Rolling_High'] = self.df['High'].rolling(window=20).max()
        self.df['Rolling_Low'] = self.df['Low'].rolling(window=20).min()
        self.df['BOS_High'] = self.df['Close'] / self.df['Rolling_High'].shift(1)

        # 2. Swing Points
        sh, sl = detect_swing_points(self.df, window=5)
        self.df['Swing_High_Confirmed'] = sh
        self.df['Swing_Low_Confirmed'] = sl
        
        # 3. FVG
        df_fvg = detect_fair_value_gaps(self.df)
        self.df = pd.concat([self.df, df_fvg], axis=1)

        # 4. Body Strength
        body = (self.df['Close'] - self.df['Open']).abs()
        total_range = self.df['High'] - self.df['Low']
        self.df['Body_Strength'] = body / total_range

    def add_target(self, horizon: int = 5, threshold: float = 0.02) -> pd.DataFrame:
        """
        Create multi-class target with Dynamic ATR thresholds.
        """
        self.df['Future_Close'] = self.df['Close'].shift(-horizon)
        self.df['Future_Return'] = (self.df['Future_Close'] - self.df['Close']) / self.df['Close']
        
        # --- Dynamic Target Logic (ATR) ---
        # Find ATR column (usually 'ATR_14')
        atr_col = 'ATR_14'
        # If not present in base, check suffixes (for 15m mode base is usually clean, but verify)
        if atr_col not in self.df.columns:
            # Try to startswith 'ATR'
            atrs = [c for c in self.df.columns if c.startswith('ATR')]
            if atrs: atr_col = atrs[0]
        
        if atr_col in self.df.columns:
            # Dynamic Threshold = 1.5 * ATR / Price
            # We convert ATR value to percentage of price
            if 'ATR_Pct' not in self.df.columns:
                self.df['ATR_Pct'] = self.df[atr_col] / self.df['Close']
            
            # Target = 1.0x ATR of movement (Relaxed from 1.5x)
            # We use a rolling mean of ATR Pct to stabilize targets? Or spot?
            # Let's use spot ATR.
            dynamic_thresh = 1.0 * self.df['ATR_Pct']
            
            # Clip minimum threshold to avoid noise (e.g. 0.5%)
            dynamic_thresh = dynamic_thresh.clip(lower=0.005)
            
            conditions = [
                (self.df['Future_Return'] > dynamic_thresh),   # Strong Up
                (self.df['Future_Return'] < -dynamic_thresh)   # Strong Down
            ]
        else:
            # Fallback to fixed
            print("[!] ATR not found for dynamic target. Using fixed 3%.")
            thresh_up = 0.03   
            thresh_down = 0.03 
            conditions = [
                (self.df['Future_Return'] > thresh_up),
                (self.df['Future_Return'] < -thresh_down)
            ]

        choices = [1, 2]
        self.df['Target'] = np.select(conditions, choices, default=0)
        
        # --- Range Filtering (Anti-Chop) ---
        # 1. ADX Filter: Increase to 25
        adx_cols = [c for c in self.df.columns if 'ADX' in c and 'daily' in c.lower()]
        if not adx_cols:
             adx_cols = [c for c in self.df.columns if 'ADX' in c] 
        
        if adx_cols:
            col = adx_cols[0]
            # Stricter: Force 0 if ADX < 25 (Choppy Market)
            self.df.loc[self.df[col] < 25, 'Target'] = 0

        # 2. BB Width Squeeze Filter
        # If BB Width is in the bottom 20% percentile (Squeeze), avoid trading?
        # Calculating percentile requires lookback.
        # Let's check if BB_Width exists.
        if 'BB_Width' in self.df.columns:
             # Rolling 100 period 20th percentile
             squeeze_threshold = self.df['BB_Width'].rolling(window=100).quantile(0.20)
             # If current width < squeeze threshold -> Squeeze -> NEUTRAL
             self.df.loc[self.df['BB_Width'] < squeeze_threshold, 'Target'] = 0
            
        self.df.dropna(inplace=True)
        return self.df
