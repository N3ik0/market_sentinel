import pandas as pd
import numpy as np
from src.data.providers.yahoo import YahooDataProvider
from src.features.engineering import FeatureEngineer
from src.ml.predictor import MarketPredictor
from src.strategy.risk import RiskManager

class BacktestPipeline:
    def __init__(self, ticker: str, initial_capital: float = 10000.0, threshold: float = 0.5):
        self.ticker = ticker
        self.capital = initial_capital
        self.balance = initial_capital
        self.trades = []
        self.threshold = threshold
        
        # We use a temporary model for backtesting to avoid overwriting production models
        self.model_file = f"{ticker}_backtest.pkl" 
        self.data_provider = YahooDataProvider(ticker)
        self.predictor = MarketPredictor(model_name=self.model_file)

    def run(self, period: str = "2y"):
        print(f"\n🧪 STARTING BACKTEST: {self.ticker} | Capital: ${self.capital}")
        
        # 1. Fetch Data
        df = self.data_provider.fetch_data(period=period)
        if df.empty: return

        # 2. Features
        fe = FeatureEngineer(df)
        df = fe.generate_all()
        df = fe.add_target(horizon=5)
        
        # 3. Train/Test Split (Time Series)
        split_idx = int(len(df) * 0.7) # Train on first 70%
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]
        
        print(f"[*] Training on {len(train_df)} candles (Past). Backtesting on {len(test_df)} candles (Recent).")
        
        # 4. Train Model (On Past Data Only)
        self.predictor.train(train_df)
        
        # 5. Simulation Loop (Walk-Forward)
        print("[*] Running simulation...")
        rm = RiskManager(rr_ratio=2.0, atr_multiplier=2.0)
        
        # Iterate through Test Data
        # We need to look ahead, so stop before the very end
        for i in range(len(test_df) - 5):
            current_row = test_df.iloc[i]
            current_idx = test_df.index[i]
            
            # Predict
            # Note: In a real rigorous backtest, we would retrain or use a rolling window.
            # Here we use the fixed model trained on past data.
            features = current_row[self.predictor.features].to_frame().T
            prediction = self.predictor.model.predict(features)[0]
            confidence = self.predictor.predict_proba(features)
            
            # CONFIDENCE FILTER
            if confidence < self.threshold:
                prediction = 0 # Force Wait
            
            if prediction == 1: # SIGNAL LONG
                price = current_row['Close']
                direction = "LONG"
                
                # Get Strategy Params
                plan = rm.generate_scenario(self.ticker, price, prediction, test_df.iloc[:i+1])
                
                sl = plan['sl']
                tp = plan['tp']
                
                # Check Outcome in next 5 days
                outcome = "HOLD"
                pnl = 0
                
                # Look forward 5 candles
                future_window = test_df.iloc[i+1 : i+6]
                
                for _, future_row in future_window.iterrows():
                    # Check Low for SL
                    if future_row['Low'] <= sl:
                        outcome = "SL Hit ❌"
                        loss_per_share = price - sl
                        if loss_per_share <= 0: continue # Should not happen unless gap
                        risk_amt = self.balance * 0.02
                        qty = risk_amt / loss_per_share
                        pnl = -risk_amt
                        break
                    
                    # Check High for TP
                    if future_row['High'] >= tp:
                        outcome = "TP Hit 🚀"
                        gain_per_share = tp - price
                        loss_per_share = price - sl
                        if loss_per_share <= 0: continue
                        risk_amt = self.balance * 0.02
                        qty = risk_amt / loss_per_share
                        pnl = qty * gain_per_share
                        break
                        
                # If neither hit in 5 days, close at market
                if outcome == "HOLD":
                    exit_price = future_window.iloc[-1]['Close']
                    loss_per_share = price - sl
                    if loss_per_share > 0:
                        risk_amt = self.balance * 0.02
                        qty = risk_amt / loss_per_share
                        pnl = qty * (exit_price - price)
                        outcome = "Time Exit ⏱️"

            elif prediction == 2: # SIGNAL SHORT
                price = current_row['Close']
                direction = "SHORT"
                
                plan = rm.generate_scenario(self.ticker, price, prediction, test_df.iloc[:i+1])
                sl = plan['sl']
                tp = plan['tp']
                
                outcome = "HOLD"
                pnl = 0
                
                future_window = test_df.iloc[i+1 : i+6]
                
                for _, future_row in future_window.iterrows():
                    # Check High for SL (Short SL is above Price)
                    if future_row['High'] >= sl:
                        outcome = "SL Hit ❌"
                        loss_per_share = sl - price
                        if loss_per_share <= 0: continue
                        risk_amt = self.balance * 0.02
                        qty = risk_amt / loss_per_share
                        pnl = -risk_amt
                        break
                    
                    # Check Low for TP (Short TP is below Price)
                    if future_row['Low'] <= tp:
                        outcome = "TP Hit 🚀"
                        gain_per_share = price - tp
                        loss_per_share = sl - price
                        if loss_per_share <= 0: continue
                        risk_amt = self.balance * 0.02
                        qty = risk_amt / loss_per_share
                        pnl = qty * gain_per_share
                        break

                if outcome == "HOLD":
                    exit_price = future_window.iloc[-1]['Close']
                    loss_per_share = sl - price
                    if loss_per_share > 0:
                        risk_amt = self.balance * 0.02
                        qty = risk_amt / loss_per_share
                        # Profit = Entry - Exit
                        pnl = qty * (price - exit_price) 
                        outcome = "Time Exit ⏱️"
            
            else: # NEUTRAL
                continue

            # Update Wallet
            self.balance += pnl
            self.trades.append({
                "Date": current_idx,
                "Type": direction,
                "Entry": price,
                "Outcome": outcome,
                "PnL": round(pnl, 2),
                "Balance": round(self.balance, 2)
            })

        self._report()

    def _report(self):
        if not self.trades:
            print("[!] No trades taken by the model.")
            return

        df_res = pd.DataFrame(self.trades)
        wins = df_res[df_res['PnL'] > 0]
        losses = df_res[df_res['PnL'] <= 0]
        
        total_trades = len(df_res)
        win_rate = (len(wins) / total_trades) * 100
        profit_factor = wins['PnL'].sum() / abs(losses['PnL'].sum()) if len(losses) > 0 else 0
        
        print("\n" + "═"*45)
        print("📊 BACKTEST RESULTS")
        print(f"Final Balance : ${self.balance:,.2f} ({((self.balance-self.capital)/self.capital)*100:+.2f}%)")
        print(f"Total Trades  : {total_trades}")
        print(f"Win Rate      : {win_rate:.2f}%")
        print(f"Profit Factor : {profit_factor:.2f}")
        print("═"*45)
        print("Last 5 Trades:")
        print(df_res[['Date', 'Outcome', 'PnL', 'Balance']].tail(5).to_string(index=False))
        print("═"*45 + "\n")
