import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

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
from src.data.factory import DataProviderFactory

class BacktestPipeline:
    def __init__(self, ticker: str, mode: str = "swing", initial_capital: float = 10000.0, threshold: float = 0.5, source: str = "auto", risk_pct: float = 0.02, adx_threshold: int = 0, trend_filter: bool = False):
        self.ticker = ticker
        self.mode = mode
        self.capital = initial_capital
        self.balance = initial_capital
        self.trades = []
        self.threshold = threshold
        self.risk_pct = risk_pct
        self.adx_threshold = adx_threshold
        self.trend_filter = trend_filter
        
        # We use a temporary model for backtesting to avoid overwriting production models
        self.model_file = f"{ticker}_{mode}_backtest.pkl" 
        self.data_provider = DataProviderFactory.get_provider(ticker, source)
        self.predictor = MarketPredictor(model_name=self.model_file)

    def run(self, period: str = "2y"):
        print(f"\n🧪 STARTING BACKTEST: {self.ticker} [{self.mode.upper()}] | Capital: ${self.capital} | Threshold: {self.threshold} | Risk: {self.risk_pct*100}% | ADX: {self.adx_threshold} | Trend Filter: {self.trend_filter}")
        
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
            metrics = self._simulate(test_df)
            if metrics:
                results.append(metrics)
            fold += 1
            
            # Reset balance for next fold or keep cumulative? 
            # Standard CV resets to evaluate model performance, not cumulative wealth.
            self.balance = self.capital 
            self.trades = [] 
            
        # Summarize CV Results
        print("\n" + "═"*45)
        print("📊 CV AGGREGATED RESULTS")
        
        if results:
            # Filter out folds with no trades to avoid dragging down win rate with 0.0
            active_results = [r for r in results if r['total_trades'] > 0]
            
            if active_results:
                avg_win_rate = np.mean([r['win_rate'] for r in active_results])
                avg_profit_factor = np.mean([r['profit_factor'] for r in active_results])
                print(f"Avg Win Rate      : {avg_win_rate:.2f}%")
                print(f"Avg Profit Factor : {avg_profit_factor:.2f}")
            else:
                 print("No trades executed in any fold.")
        else:
            print("No valid results collected.")
            
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
            features = current_row[self.predictor.features].to_frame().T
            prediction = self.predictor.model.predict(features)[0]
            confidence = self.predictor.predict_proba(features)

            # ADX FILTER (Regime Filter)
            if self.adx_threshold > 0:
                # Try to find ADX column
                adx_cols = [c for c in test_df.columns if 'ADX' in c]
                if adx_cols:
                    adx_val = current_row[adx_cols[0]]
                    if adx_val < self.adx_threshold and prediction != 0:
                         print(f"  [~] Skipped signal {prediction} at {current_idx} (ADX: {adx_val:.2f} < {self.adx_threshold})")
                         prediction = 0
            
            # TREND FILTER (EMA 200)
            if self.trend_filter:
                # Find EMA 200 column (could be Daily_EMA_200 or EMA_200)
                ema_cols = [c for c in test_df.columns if 'EMA_200' in c]
                if ema_cols:
                    ema_val = current_row[ema_cols[0]]
                    price = current_row['Close']
                    if not np.isnan(ema_val):
                        if prediction == 1 and price < ema_val:
                            print(f"  [~] Skipped LONG at {current_idx} (Price {price:.2f} < EMA200 {ema_val:.2f})")
                            prediction = 0
                        elif prediction == 2 and price > ema_val:
                            print(f"  [~] Skipped SHORT at {current_idx} (Price {price:.2f} > EMA200 {ema_val:.2f})")
                            prediction = 0

            # RSI MOMENTUM FILTER (Sniper Mode)
            # Find RSI column
            rsi_cols = [c for c in test_df.columns if 'RSI_14' in c]
            if rsi_cols:
                 rsi = current_row[rsi_cols[0]]
                 
                 # LONG Logic: 
                 # 1. Must use "Momentum" (RSI > 50)
                 # 2. Must NOT be Overbought (RSI < 70)
                 if prediction == 1:
                     if rsi <= 50:
                         print(f"  [~] Skipped LONG at {current_idx} (RSI {rsi:.2f} <= 50 - No Momentum)")
                         prediction = 0
                     elif rsi >= 70:
                         print(f"  [~] Skipped LONG at {current_idx} (RSI {rsi:.2f} >= 70 - Overbought)")
                         prediction = 0
                         
                 # SHORT Logic:
                 # 1. Must use "Momentum" (RSI < 50)
                 # 2. Must NOT be Oversold (RSI > 30)
                 elif prediction == 2:
                     if rsi >= 50:
                         print(f"  [~] Skipped SHORT at {current_idx} (RSI {rsi:.2f} >= 50 - No Momentum)")
                         prediction = 0
                     elif rsi <= 30:
                         print(f"  [~] Skipped SHORT at {current_idx} (RSI {rsi:.2f} <= 30 - Oversold)")
                         prediction = 0

            # CONFIDENCE FILTER
            if confidence < self.threshold and prediction != 0:
                 # Only print if it was originally a signal (1 or 2)
                 print(f"  [~] Skipped signal {prediction} at {current_idx} (Conf: {confidence:.2f} < {self.threshold})")
                 prediction = 0 # Force Wait
            
            if prediction == 1: # SIGNAL LONG
                price = current_row['Close']
                direction = "LONG"
                
                # Get Strategy Params
                plan = rm.generate_scenario(self.ticker, price, prediction, test_df.iloc[:i+1])
                initial_sl = plan['sl']
                risk_per_share = price - initial_sl
                
                if risk_per_share <= 0: continue
                
                outcome = "HOLD"
                pnl = 0
                max_price = price 
                sl = initial_sl
                
                # ATR for Trailing
                # We can calculate separate ATR or use the risk_per_share as proxy (Risk = 2*ATR often in RiskManager)
                # Let's derive rough ATR from Risk Distance
                # If Risk = 2 * ATR -> ATR = Risk / 2
                atr_val = risk_per_share / 2.0
                
                future_window = test_df.iloc[i+1 : i+50] 
                
                for _, future_row in future_window.iterrows():
                    current_high = future_row['High']
                    current_low = future_row['Low']
                    
                    # Update Trailing (3x ATR Width)
                    if current_high > max_price:
                        max_price = current_high
                        # New SL is High - 3*ATR (Wider)
                        new_sl = max_price - (3.0 * atr_val)
                        if new_sl > sl:
                            sl = new_sl

                    # Check SL Hit
                    if current_low <= sl:
                        if sl > price:
                             outcome = "Trailing SL Hit 💰"
                             pnl_per_share = sl - price
                        else:
                             outcome = "SL Hit ❌"
                             pnl_per_share = sl - price # Negative
                             
                        exit_price = sl
                        qty = (self.balance * self.risk_pct) / risk_per_share
                        pnl = qty * pnl_per_share
                        break
                        
                # Time Exit
                if outcome == "HOLD":
                    exit_price = future_window.iloc[-1]['Close']
                    qty = (self.balance * self.risk_pct) / risk_per_share
                    pnl = qty * (exit_price - price)
                    outcome = "Time Exit ⏱️"

            elif prediction == 2: # SIGNAL SHORT
                price = current_row['Close']
                direction = "SHORT"
                
                plan = rm.generate_scenario(self.ticker, price, prediction, test_df.iloc[:i+1])
                initial_sl = plan['sl']
                risk_per_share = initial_sl - price
                
                if risk_per_share <= 0: continue
                
                outcome = "HOLD"
                pnl = 0
                min_price = price
                sl = initial_sl
                
                atr_val = risk_per_share / 2.0
                
                future_window = test_df.iloc[i+1 : i+50]
                
                for _, future_row in future_window.iterrows():
                    current_high = future_row['High']
                    current_low = future_row['Low']
                    
                    # Update Trailing
                    if current_low < min_price:
                        min_price = current_low
                        new_sl = min_price + (3.0 * atr_val)
                        if new_sl < sl:
                            sl = new_sl
                            
                    # Check SL Hit
                    if current_high >= sl:
                        if sl < price:
                             outcome = "Trailing SL Hit 💰"
                             pnl_per_share = price - sl
                        else:
                             outcome = "SL Hit ❌"
                             pnl_per_share = price - sl # Negative
                        
                        exit_price = sl
                        qty = (self.balance * self.risk_pct) / risk_per_share
                        pnl = qty * pnl_per_share
                        break

                if outcome == "HOLD":
                    exit_price = future_window.iloc[-1]['Close']
                    qty = (self.balance * self.risk_pct) / risk_per_share
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
            print(f"  [Trade] {direction} @ {price:.2f} -> {outcome} ({pnl:+.2f}) Balance: {self.balance:.2f}")

        return self._report(return_metrics=True)

    def _report(self, return_metrics=False):
        if not self.trades:
            print("[!] No trades taken by the model.")
            if return_metrics:
                return {
                    "win_rate": 0.0,
                    "profit_factor": 0.0,
                    "final_balance": self.balance,
                    "total_trades": 0
                }
            return

        df_res = pd.DataFrame(self.trades)
        wins = df_res[df_res['PnL'] > 0]
        losses = df_res[df_res['PnL'] <= 0]
        
        total_trades = len(df_res)
        win_rate = (len(wins) / total_trades) * 100
        
        # Safe Profit Factor
        total_loss = abs(losses['PnL'].sum())
        profit_factor = wins['PnL'].sum() / total_loss if total_loss > 0 else float('inf')
        
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
                "final_balance": self.balance,
                "total_trades": total_trades
            }
