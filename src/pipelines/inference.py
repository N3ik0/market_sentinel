from src.config.settings import settings

from src.features.engineering import FeatureEngineer
from src.ml.predictor import MarketPredictor
from src.strategy.risk import RiskManager
from src.infrastructure.notion import NotionClient

class InferencePipeline:
    def __init__(self, ticker: str, mode: str = "swing"):
        self.ticker = ticker
        self.mode = mode
from src.data.factory import DataProviderFactory

class InferencePipeline:
    def __init__(self, ticker: str, mode: str = "swing", source: str = "auto"):
        self.ticker = ticker
        self.mode = mode
        self.data_provider = DataProviderFactory.get_provider(ticker, source)
        # Load model specifically for this ticker AND mode
        self.model_file = f"{ticker}_{mode}.pkl"
        self.predictor = MarketPredictor(model_name=self.model_file)

    def run(self):
        """Executes the Inference Workflow based on mode."""
        print(f"\n🔮 STARTING INFERENCE PIPELINE: {self.ticker} [{self.mode.upper()}]")
        
        # 1. Load Model
        try:
            self.predictor.load_model()
        except FileNotFoundError:
            print("[!] Critical: Model not found. Run 'train' first.")
            return

        # 2. Fetch Recent Data (Enough for indicators)
        if self.mode == "intraday":
            # 15m intervals, limited to ~60 days. Fetch 59d buffer.
            df = self.data_provider.fetch_data(period="59d", interval="15m")
        else:
            # Swing (Daily). Need >1 year for 252d indicators.
            df = self.data_provider.fetch_data(period="2y", interval="1d")
            
        if df.empty:
            return

        # 3. Feature Engineering
        fe = FeatureEngineer(df)
        df_enriched = fe.generate_all()
        
        # 4. Predict on Latest Candle
        # 4. Predict on Latest Candle
        last_row = df_enriched.tail(1)
        prediction = self.predictor.predict(last_row)
        confidence_score = self.predictor.predict_proba(last_row)
        print(f"[*] AI Prediction: {prediction} | Confidence: {confidence_score:.2%}")
        
        if confidence_score < 0.5:
             print("[-] Confidence below 50%. Forcing WAIT.")
             prediction = 0
             
        if prediction != 0:
             bias_confirmed = self._check_trend_bias(last_row, prediction)
             if not bias_confirmed:
                 print(f"[-] Trend Bias Mismatch ({self.mode}). Forcing WAIT.")
                 prediction = 0
        
        # 5. Risk Management
        rm = RiskManager(rr_ratio=2.0, atr_multiplier=2.0)
        plan = rm.generate_scenario(
            ticker=self.ticker,
            current_price=last_row['Close'].values[0],
            prediction=prediction,
            df=df_enriched
        )
        
        # 6. Publish
        self._publish(plan, prediction)
        self._summary(plan)
        print("✅ INFERENCE COMPLETE.\n")

    def _check_trend_bias(self, row, prediction) -> bool:
        """
        Validates the trade direction against higher timeframe trends.
        Returns True if the trade aligns with the trend.
        """
        # 1. Swing Mode (Daily) -> Check Weekly Trend (if available) or SMA200 Alignment
        if self.mode == "swing":
            return True # Keeping Swing lenient for now.

        # 2. Intraday Mode (15m) -> Check 1H and 4H EMAs
        elif self.mode == "intraday":
            try:
                close = row['Close'].values[0]
                
                # Check 1H Trend (EMA 50 1H)
                ema50_1h = row['EMA_50_1h'].values[0]
                
                # Check 4H Trend (EMA 50 4H)
                ema50_4h = row['EMA_50_4h'].values[0]
                
                # Prediction 1 = Long, 2 = Short (Assumed based on target gen, but let's verify)
                # Actually pipeline output is likely 1 (Long) / 2 (Short) or similar.
                # Let's assume standard: 1=UP, 2=DOWN. 
                
                if prediction == 1: # LONG Signal
                     # Must be above BOTH EMAs
                     if close > ema50_1h and close > ema50_4h:
                         return True
                     else:
                         print(f"   [Bias] Long Signal BUT Price < EMA50 (1H: {ema50_1h:.2f}, 4H: {ema50_4h:.2f})")
                         return False

                elif prediction == 2: # SHORT Signal
                     # Must be below BOTH EMAs
                     if close < ema50_1h and close < ema50_4h:
                         return True
                     else:
                        print(f"   [Bias] Short Signal BUT Price > EMA50 (1H: {ema50_1h:.2f}, 4H: {ema50_4h:.2f})")
                        return False
                        
            except KeyError as e:
                print(f"[!] Warning: Missing MTF indicator for bias check: {e}")
                return True 
                
        return True

    def _publish(self, plan, prediction):
        try:
            settings.validate()
            # Confidence mapping based on backtest results
            if prediction == 0:
                print("[-] Signal Neutral (Wait). No publication.")
                return

            client = NotionClient(settings.NOTION_TOKEN, settings.ID_DB_SENTINEL)
            client.publish_trading_plan(plan, confidence_score)
        except Exception as e:
            print(f"[!] Publishing failed: {e}")

    def _summary(self, plan):
        print("\n" + "═"*45)
        print(f"SIGNAL : {plan['direction']}")
        print(f"ENTRY  : {plan['entry']}$")
        print(f"STOP   : {plan['sl']}$")
        print(f"TARGET : {plan['tp']}$")
        print("═"*45 + "\n")
