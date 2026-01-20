import pandas as pd
import numpy as np
from typing import Dict, Any

class RiskManager:
    """Manages trade risk and position sizing logic."""
    
    def __init__(self, rr_ratio: float = 2.0, atr_multiplier: float = 2.0):
        self.rr_ratio = rr_ratio
        self.atr_multiplier = atr_multiplier

    def generate_scenario(self, ticker: str, current_price: float, prediction: int, df: pd.DataFrame) -> Dict[str, Any]:
        """Generates a trading plan based on prediction and volatility."""
        
        # Get latest ATR
        atr = df['ATR'].iloc[-1]
        
        # Fallback if ATR is invalid
        if np.isnan(atr) or atr <= 0:
            atr = current_price * 0.02

        if prediction == 1:  # LONG
            direction = "LONG 🚀"
            stop_loss = current_price - (atr * self.atr_multiplier)
            risk = current_price - stop_loss
            take_profit = current_price + (risk * self.rr_ratio)
            
        elif prediction == 2:  # SHORT
            direction = "SHORT 📉"
            stop_loss = current_price + (atr * self.atr_multiplier)
            risk = stop_loss - current_price
            take_profit = current_price - (risk * self.rr_ratio)
            
        else: # NEUTRAL / WAIT
            direction = "WAIT ⏳"
            stop_loss = 0.0
            take_profit = 0.0
            risk = 0.0

        return {
            "ticker": ticker,
            "direction": direction,
            "entry": round(current_price, 2),
            "sl": round(stop_loss, 2),
            "tp": round(take_profit, 2),
            "risk_amount": round(risk, 2),
            "rr_ratio": self.rr_ratio
        }
