import pandas as pd
import numpy as np

class RiskManager:
    def __init__(self, rr_ratio: float = 2.0, atr_multiplier: float = 2.0):
        """
        rr_ratio : Le ratio Risk/Reward (on veut gagner X fois ce qu'on risque).
        atr_multiplier : Coefficient pour placer le Stop Loss par rapport à la volatilité.
        """
        self.rr_ratio = rr_ratio
        self.atr_multiplier = atr_multiplier

    def generate_scenario(self, ticker: str, current_price: float, prediction: int, df: pd.DataFrame):
        """
        Prend une prédiction de l'IA (0 ou 1) et retourne un plan de trading.
        """
        # On récupère l'ATR le plus récent calculé dans tes features
        atr = df['ATR'].iloc[-1]
        
        # Sécurité : si l'ATR est invalide, on utilise une volatilité par défaut de 2%
        if np.isnan(atr) or atr <= 0:
            atr = current_price * 0.02

        if prediction == 1:  # Scénario LONG (Achat)
            direction = "LONG 🚀"
            # Stop Loss : placé sous le prix actuel d'un multiple de la volatilité
            stop_loss = current_price - (atr * self.atr_multiplier)
            risk = current_price - stop_loss
            # Take Profit : basé sur le ratio Risk/Reward
            take_profit = current_price + (risk * self.rr_ratio)
        else:  # Scénario SHORT (Vente)
            direction = "SHORT 📉"
            # Stop Loss : placé au-dessus du prix actuel
            stop_loss = current_price + (atr * self.atr_multiplier)
            risk = stop_loss - current_price
            take_profit = current_price - (risk * self.rr_ratio)

        return {
            "ticker": ticker,
            "direction": direction,
            "entry": round(current_price, 2),
            "sl": round(stop_loss, 2),
            "tp": round(take_profit, 2),
            "risk_amount": round(risk, 2),
            "rr_ratio": self.rr_ratio
        }