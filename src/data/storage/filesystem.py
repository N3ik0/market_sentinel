import os
import pandas as pd
from typing import Optional
from src.config.settings import settings

class LocalStorage:
    """Handles local file persistence (Parquet)."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or settings.DATA_DIR

    def save(self, df: pd.DataFrame, filename: str) -> str:
        """Save DataFrame to parquet."""
        if df.empty:
            print("[!] Error: Data is empty, not saving.")
            return ""

        os.makedirs(self.data_dir, exist_ok=True)
        file_path = os.path.join(self.data_dir, filename)

        try:
            df.to_parquet(file_path, engine='pyarrow')
            print(f"[+] Data saved to: {file_path}")
            return file_path
        except Exception as e:
            print(f"[!] Failed to save data: {e}")
            return ""

    def load(self, filename: str) -> pd.DataFrame:
        """Load DataFrame from parquet."""
        file_path = os.path.join(self.data_dir, filename)

        if os.path.exists(file_path):
            try:
                df = pd.read_parquet(file_path)
                print(f"[+] Data loaded from {file_path}")
                return df
            except Exception as e:
                print(f"[!] Error reading file: {e}")
                return pd.DataFrame()
        else:
            print(f"[?] No local file found: {file_path}")
            return pd.DataFrame()
