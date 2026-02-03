import ccxt
import pandas as pd
from typing import Dict, List, Optional
import time

class BinanceDataProvider:
    """
    Data Provider for Binance using CCXT.
    """

    def __init__(self, ticker: str):
        """
        ticker: Format should be consistent.
                However, internal CCXT uses 'BTC/USDT'.
                Input might be 'BTC-USD' (Yahoo style).
        """
        self.raw_ticker = ticker
        self.symbol = self._normalize_symbol(ticker)
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
        })

    def _normalize_symbol(self, ticker: str) -> str:
        """
        Converts 'BTC-USD' -> 'BTC/USDT'.
        """
        if '-' in ticker:
            base, quote = ticker.split('-')
            # Assuming USD usually maps to USDT in Binance for Crypto pairs
            if quote == 'USD':
                quote = 'USDT'
            return f"{base}/{quote}"
        
        # Fallback for BTCUSD format
        if ticker.endswith('USD') and '/' not in ticker:
             # Heuristic: BTCUSD -> BTC/USDT
             base = ticker[:-3]
             return f"{base}/USDT"
             
        return ticker.replace('-', '/')

    def fetch_data(self, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetch OHLCV data.
        limit: CCXT fetch_ohlcv limit.
        period: '1y', '60d'. We need to calculate limit or start_time based on this.
        For simplicity in this V1, we fetch the max allowed or a fixed limit if period is vague.
        """
        print(f"[*] Fetching data for {self.symbol} via Binance...")
        
        # Map interval
        timeframe = interval
        if interval == '1W' or interval == '1wk': timeframe = '1w'
        
        # Calculate limit based on period (approx)
        # 1y = 365 days. 
        limit = 1000 # default ccxt
        
        if period == "2y":
            limit = 730 if interval == '1d' else 1000 # ccxt binance limit is usually 1000
        elif period == "60d" and interval == '15m':
             # 60 days * 24h * 4 = 5760 candles. Exceeds single call limit (1000).
             # We would need pagination.
             # For MVP V1, we stick to 1000 candles (approx 10 days of 15m data).
             limit = 1000

        try:
            ohlcv = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, limit=limit)
            
            if not ohlcv:
                print(f"[!] Warning: No data returned for {self.symbol}")
                return pd.DataFrame()

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            print(f"[+] {len(df)} rows fetched.")
            return df
            
        except Exception as e:
            print(f"[!] Binance API Error: {e}")
            return pd.DataFrame()

    def fetch_mtf_data(self, intervals: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Fetch multi-timeframe data: 1d, 4h, 1h."""
        if intervals is None:
            intervals = ["1d", "4h", "1h"]
            
        mtf_data = {}
        for inter in intervals:
            # Simple wrapper
            mtf_data[inter] = self.fetch_data(interval=inter) # Period handled defaults
        return mtf_data
