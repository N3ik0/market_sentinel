from src.config.settings import settings
from src.data.providers.yahoo import YahooDataProvider
from src.data.storage.filesystem import LocalStorage
from src.features.engineering import FeatureEngineer
from src.ml.predictor import MarketPredictor

class TrainingPipeline:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.data_provider = YahooDataProvider(ticker)
        self.storage = LocalStorage()
        # Save model specifically for this ticker
        self.model_file = f"{ticker}.pkl"
        self.predictor = MarketPredictor(model_name=self.model_file)

    def run(self, period: str = "5y", interval: str = "1d"):
        """Executes the Model Training Workflow."""
        print(f"\n🚀 STARTING TRAINING PIPELINE: {self.ticker}")
        
        # 1. Fetch History
        df = self.data_provider.fetch_data(period=period, interval=interval)
        if df.empty:
            print("[!] Training aborted: No data.")
            return

        # 2. Save Raw Data
        self.storage.save(df, f"{self.ticker}.parquet")
        
        # 3. Feature Engineering
        print("[*] Generating Features...")
        fe = FeatureEngineer(df)
        df_final = fe.generate_all()
        df_final = fe.add_target(horizon=5)
        
        # 4. Train Model
        print(f"[*] Training Model on {len(df_final)} samples...")
        self.predictor.train(df_final)
        self.predictor.get_feature_importance()
        
        print("✅ TRAINING COMPLETE. Model ready for inference.\n")
