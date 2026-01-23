import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from src.data.providers.yahoo import YahooDataProvider
from src.features.engineering import FeatureEngineer
from src.ml.predictor import MarketPredictor
from src.strategy.risk import RiskManager

class BacktestPipeline:
    def __init__(self, ticker: str, mode: str = "swing", initial_capital: float = 10000.0, threshold: float = 0.5):
        self.ticker = ticker
        self.mode = mode
        self.capital = initial_capital
        self.balance = initial_capital
        self.trades = []
        self.threshold = threshold
        
        # We use a temporary model for backtesting to avoid overwriting production models
        self.model_file = f"{ticker}_{mode}_backtest.pkl" 
        self.data_provider = YahooDataProvider(ticker)
        self.predictor = MarketPredictor(model_name=self.model_file)

    def run(self, period: str = "2y"):
        print(f"\n🧪 STARTING BACKTEST: {self.ticker} [{self.mode.upper()}] | Capital: ${self.capital}")
        
        # 0. Configure based on Mode
        if self.mode == "intraday":
            period = "59d"
            interval = "15m"
            horizon = 8
        else:
             interval = "1d"
             horizon = 5

        # 1. Fetch Data
        df = self.data_provider.fetch_data(period=period, interval=interval)
        if df.empty: return

        # 2. Features
        fe = FeatureEngineer(df)
        df = fe.generate_all()
        df = fe.add_target(horizon=horizon)
        
        # 3. Cross-Validation (Time Series Split)
        print("[*] Running TimeSeries Cross-Validation (3 Splits)...")
        tscv = TimeSeriesSplit(n_splits=3)
        
        fold = 1
        results = []
        
        X = df # Full dataframe
        
        for train_index, test_index in tscv.split(X):
            train_df = X.iloc[train_index]
            test_df = X.iloc[test_index]
            
            print(f"\n---> FOLD {fold}: Train ({len(train_df)}) | Test ({len(test_df)})")
            
            # Train on this fold
            self.predictor.train(train_df)
            
            # Simulate on this fold
            # Simulate on this fold
            metrics = self._simulate(test_df)
            if metrics:
                results.append(metrics)
            fold += 1
            
            # Reset balance for next fold or keep cumulative? 
            # Standard CV resets to evaluate model performance, not cumulative wealth.
            self.balance = self.capital 
            self.trades = [] # Clear trades for next fold logic in simulate? 
            # Actually _simulate currently uses self.trades and self.balance directly.
            # I should refactor _simulate calls to be cleaner or just reset here.
            
        # Summarize CV Results
        print("\n" + "═"*45)
        print("📊 CV AGGREGATED RESULTS")
        avg_win_rate = np.mean([r['win_rate'] for r in results])
        avg_profit_factor = np.mean([r['profit_factor'] for r in results])
        print(f"Avg Win Rate      : {avg_win_rate:.2f}%")
        print(f"Avg Profit Factor : {avg_profit_factor:.2f}")
        print("═"*45 + "\n")

    def _simulate(self, test_df):
        """Runs simulation on a specific test set."""
        self.balance = self.capital
        self.trades = []
        rm = RiskManager(rr_ratio=2.0, atr_multiplier=2.0)
        
        # Iterate through Test Data
        for i in range(len(test_df) - 8): # Buffer for horizon
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

        return self._report(return_metrics=True)

    def _report(self, return_metrics=False):
        if not self.trades:
            print("[!] No trades taken by the model.")
            if return_metrics:
                return {
                    "win_rate": 0.0,
                    "profit_factor": 0.0,
                    "final_balance": self.balance
                }
            return

        df_res = pd.DataFrame(self.trades)
        wins = df_res[df_res['PnL'] > 0]
        losses = df_res[df_res['PnL'] <= 0]
        
        total_trades = len(df_res)
        win_rate = (len(wins) / total_trades) * 100
        profit_factor = wins['PnL'].sum() / abs(losses['PnL'].sum()) if len(losses) > 0 else 0
        
        print("\n" + "═"*45)
        print(f"📝 FOLD RESULTS")
        print(f"Final Balance : ${self.balance:,.2f} ({((self.balance-self.capital)/self.capital)*100:+.2f}%)")
        print(f"Total Trades  : {total_trades}")
        print(f"Win Rate      : {win_rate:.2f}%")
        print(f"Profit Factor : {profit_factor:.2f}")
        print("═"*45)
        
        if return_metrics:
            return {
                "win_rate": win_rate,
                "profit_factor": profit_factor,
                "final_balance": self.balance
            }
