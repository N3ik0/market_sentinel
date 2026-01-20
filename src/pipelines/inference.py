from src.config.settings import settings
from src.data.providers.yahoo import YahooDataProvider
from src.features.engineering import FeatureEngineer
from src.ml.predictor import MarketPredictor
from src.strategy.risk import RiskManager
from src.infrastructure.notion import NotionClient

class InferencePipeline:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.data_provider = YahooDataProvider(ticker)
        # Load model specifically for this ticker
        self.model_file = f"{ticker}.pkl"
        self.predictor = MarketPredictor(model_name=self.model_file)

    def run(self):
        """Executes the Daily Inference Workflow."""
        print(f"\n🔮 STARTING INFERENCE PIPELINE: {self.ticker}")
        
        # 1. Load Model
        try:
            self.predictor.load_model()
        except FileNotFoundError:
            print("[!] Critical: Model not found. Run 'train' first.")
            return

        # 2. Fetch Recent Data (Enough for indicators)
        # We need at least 50 candles for EMA_50 + buffer
        df = self.data_provider.fetch_data(period="6mo", interval="1d")
        if df.empty:
            return

        # 3. Feature Engineering
        fe = FeatureEngineer(df)
        df_enriched = fe.generate_all()
        
        # 4. Predict on Latest Candle
        last_row = df_enriched.tail(1)
        prediction = self.predictor.predict(last_row)
        
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

    def _publish(self, plan, prediction):
        try:
            settings.validate()
            # Confidence mapping based on backtest results
            if prediction == 0:
                print("[-] Signal Neutral (Wait). No publication.")
                return

            confidence = 0.65 if prediction == 1 else 0.60 # Arbitrary for Short for now
            
            client = NotionClient(settings.NOTION_TOKEN, settings.ID_DB_SENTINEL)
            client.publish_trading_plan(plan, confidence)
        except Exception as e:
            print(f"[!] Publishing failed: {e}")

    def _summary(self, plan):
        print("\n" + "═"*45)
        print(f"SIGNAL : {plan['direction']}")
        print(f"ENTRY  : {plan['entry']}$")
        print(f"STOP   : {plan['sl']}$")
        print(f"TARGET : {plan['tp']}$")
        print("═"*45 + "\n")
