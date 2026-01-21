
import pandas as pd
import numpy as np
import sys
import os

# Create dummy 1H data for 100 days
dates = pd.date_range(start='2023-01-01', periods=24*100, freq='1h')
df = pd.DataFrame({
    'Open': np.random.rand(len(dates)) * 100,
    'High': np.random.rand(len(dates)) * 105,
    'Low': np.random.rand(len(dates)) * 95,
    'Close': np.random.rand(len(dates)) * 100,
    'Volume': np.random.randint(100, 1000, len(dates))
}, index=dates)

print("Original DF shape:", df.shape)

try:
    from src.features.engineering import FeatureEngineer
    fe = FeatureEngineer(df)
    df_new = fe.generate_all()
    print("Feature generation successful!")
    print("New DF shape:", df_new.shape)
    print("Columns:", df_new.columns.tolist()[:10], "...")
    
    # Check for specific requested features
    has_daily = any('daily' in c.lower() for c in df_new.columns)
    has_4h = any('4h' in c.lower() for c in df_new.columns)
    print(f"Has Daily features: {has_daily}")
    print(f"Has 4h features: {has_4h}")
    
except ImportError as e:
    print(f"ImportError: {e}") 
    print("Please ensure pandas_ta is also installed: pip install pandas_ta")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
