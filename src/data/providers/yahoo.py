import yfinance as yf
import pandas as pd
from typing import Dict, List

class YahooDataProvider:
    """Provider data from Yahoo Finance."""
    
    def __init__(self, ticker: str):
        self.ticker = ticker

    def fetch_data(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """Fetch OHLCV data."""
        print(f"[*] Fetching data for {self.ticker}...")

        df = yf.download(tickers=self.ticker, period=period, interval=interval)

        if df.empty:
            print(f"[!] Error: No results for {self.ticker}.")
            return pd.DataFrame()

        # Handle MultiIndex columns if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        # Ensure Datetime Index
        df.index = pd.to_datetime(df.index)

        print(f"[+] {len(df)} rows fetched.")
        return df

    def fetch_mtf_data(self, intervals: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Fetch multi-timeframe data."""
        if intervals is None:
            intervals = ["1d", "4h", "1h"]
            
        mtf_data = {}
        for inter in intervals:
            # Adjust period based on interval to avoid API errors or empty returns
            period = "2y" if inter == "1d" else "60d" 
            mtf_data[inter] = self.fetch_data(period=period, interval=inter)
        return mtf_data
