from src.ml.predictor import MarketPredictor
import pandas as pd
import numpy as np

def run_repro():
    print("Running Predictor Feature Mismatch Reproduction...")
    
    # 1. Simulate a trained model that expects long-term features
    p = MarketPredictor("dummy.pkl")
    # Manually inject features that would exist if trained on 5y data
    p.features = ['Close', 'Vol_Rank20d'] 
    
    # 2. Simulate inference data (shorter than required for Vol_Rank20d)
    # 6 months ~ 126 rows. 
    # Our volatility calc requires > 272 rows.
    # So FeatureEngineer would NOT produce 'Vol_Rank20d'.
    df_inference = pd.DataFrame({
        'Close': np.random.rand(126)
    })
    
    print(f"Inference Data Columns: {df_inference.columns.tolist()}")
    print(f"Model Expected Features: {p.features}")
    
    try:
        p.predict(df_inference.tail(1))
        print("Prediction success (Unexpected!)")
    except KeyError as e:
        print(f"Caught expected KeyError: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    run_repro()
