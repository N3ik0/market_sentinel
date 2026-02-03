from src.data.providers.yahoo import YahooDataProvider
from src.data.providers.binance import BinanceDataProvider

class DataProviderFactory:
    """
    Factory to create the right DataProvider.
    """
    
    @staticmethod
    def get_provider(ticker: str, source: str = "auto"):
        """
        source: 'yahoo', 'binance', or 'auto'.
        """
        
        if source == "binance":
            return BinanceDataProvider(ticker)
        
        elif source == "yahoo":
            return YahooDataProvider(ticker)
            
        else: # Auto
            # Heuristic: If it looks like a Pair (BTC-USD) and is in top crypto list? 
            # Or just default all '-USD' to Yahoo unless specified?
            # User wants Binance for Crypto.
            
            # Simple heuristic:
            if ticker in ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD']:
                 return BinanceDataProvider(ticker)
            
            # Additional heuristic for non-hyphenated tickers (common user input)
            if ticker in ['BTCUSD', 'ETHUSD', 'SOLUSD', 'XRPUSD']:
                 return BinanceDataProvider(ticker)
            
            # Or if it has USDT
            if 'USDT' in ticker:
                 return BinanceDataProvider(ticker)

            return YahooDataProvider(ticker)
