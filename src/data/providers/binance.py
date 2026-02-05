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
        
        # Calculate start timestamp based on period
        now = self.exchange.milliseconds()
        duration_ms = 0
        if period == "2y":
            duration_ms = 730 * 24 * 60 * 60 * 1000
        elif period == "1y":
            duration_ms = 365 * 24 * 60 * 60 * 1000
        elif period.endswith('d'):
            try:
                days = int(period[:-1])
                duration_ms = days * 24 * 60 * 60 * 1000
            except:
                duration_ms = 60 * 24 * 60 * 60 * 1000
        else:
            # Default 60d
            duration_ms = 60 * 24 * 60 * 60 * 1000
            
        since_ts = now - duration_ms
        all_ohlcv = []
        
        print(f"[*] Fetching full history since {pd.to_datetime(since_ts, unit='ms')}...")
        
        # Pagination Loop
        fetch_since = since_ts
        market_id = self.symbol.replace('/', '') # basic normalization, or use self.exchange.market_id(self.symbol) if loaded
        
        while True:
            try:
                # Use raw public_get_klines to get Taker Buy Volume (Index 9)
                # Params: symbol, interval, startTime, limit
                params = {
                    'symbol': market_id,
                    'interval': timeframe,
                    'startTime': int(fetch_since),
                    'limit': 1000
                }
                
                # Retrieve Raw Data
                # [Open time, Open, High, Low, Close, Volume, Close time, Quote asset volume, Number of trades, Taker buy base asset volume, ...]
                klines = self.exchange.public_get_klines(params)
                
                if not klines:
                    break
                
                all_ohlcv.extend(klines)
                
                last_timestamp = klines[-1][0]
                fetch_since = int(last_timestamp) + 1
                
                # Check if we reached now
                if int(last_timestamp) >= now - ( interval_ms := 15*60*1000 ):  
                    break
                    
                time.sleep(self.exchange.rateLimit / 1000.0)
                
            except Exception as e:
                print(f"[!] Pagination Error: {e}")
                # Fallback to standard fetch if raw fails? Or just break.
                break

        if not all_ohlcv:
             print(f"[!] Warning: No data returned for {self.symbol}")
             return pd.DataFrame()

        # Columns for Raw Klines
        columns = [
            'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume', 
            'CloseTime', 'QuoteAssetVolume', 'Trades', 'Taker_Buy_Vol', 
            'Taker_Buy_Quote_Vol', 'Ignore'
        ]
        
        df = pd.DataFrame(all_ohlcv, columns=columns)
        
        # Type Conversion
        numeric_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Taker_Buy_Vol']
        for col in numeric_cols:
            df[col] = df[col].astype(float)
            
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Drop unused columns to keep it clean
        df = df[['Open', 'High', 'Low', 'Close', 'Volume', 'Taker_Buy_Vol']]
        
        # Deduplicate
        df = df[~df.index.duplicated(keep='first')]
        
        print(f"[+] {len(df)} rows fetched (with Taker Volume).")
        return df

    def fetch_mtf_data(self, intervals: List[str] = None) -> Dict[str, pd.DataFrame]:
        """Fetch multi-timeframe data: 1d, 4h, 1h."""
        if intervals is None:
            intervals = ["1d", "4h", "1h"]
            
        mtf_data = {}
        for inter in intervals:
            # Simple wrapper
            mtf_data[inter] = self.fetch_data(interval=inter) # Period handled defaults
        return mtf_data
