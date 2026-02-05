import argparse
import sys
import os

# Add root folder to python path to allow imports from src
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.pipelines.training import TrainingPipeline
from src.pipelines.inference import InferencePipeline
from src.pipelines.backtest import BacktestPipeline

def main():
    parser = argparse.ArgumentParser(description="Market Sentinel CLI")
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Train Command
    train_parser = subparsers.add_parser("train", help="Train the model on historical data")
    train_parser.add_argument("--ticker", type=str, default="BTCUSD", help="Ticker symbol (default: TSLA)")
    train_parser.add_argument("--period", type=str, default="5y", help="Data period (default: 5y)")
    train_parser.add_argument("--mode", type=str, default="swing", choices=["swing", "intraday"], help="Trading mode: swing or intraday")
    
    # Predict Command
    predict_parser = subparsers.add_parser("predict", help="Run inference and publish to Notion")
    predict_parser.add_argument("--ticker", type=str, default="BTCUSD", help="Ticker symbol (default: TSLA)")
    predict_parser.add_argument("--mode", type=str, default="swing", choices=["swing", "intraday"], help="Trading mode: swing (Daily) or intraday (15m)")

    # Backtest Command
    backtest_parser = subparsers.add_parser("backtest", help="Simulate performance on past data")
    backtest_parser.add_argument("--ticker", type=str, default="BTCUSD", help="Ticker symbol")
    backtest_parser.add_argument("--period", type=str, default="2y", help="Data period")
    backtest_parser.add_argument("--mode", type=str, default="swing", choices=["swing", "intraday"], help="Trading mode")
    backtest_parser.add_argument("--threshold", type=float, default=0.65, help="Confidence threshold (default: 0.65)")
    backtest_parser.add_argument("--risk", type=float, default=0.02, help="Risk per trade as decimal (default: 0.02 for 2%)")
    backtest_parser.add_argument("--filter_adx", type=int, default=0, help="Minimum ADX to trade (0 to disable, suggested 20-25)")
    backtest_parser.add_argument("--trend_filter", action="store_true", help="Enable EMA 200 Trend Filter")
    
    # Global args (could be parent parser, but for now adding to each or just one)
    # Ideally add to all or as a mixin. Simple way: Add to each.
    train_parser.add_argument("--source", type=str, default="auto", choices=["auto", "yahoo", "binance"], help="Data Provider")
    predict_parser.add_argument("--source", type=str, default="auto", choices=["auto", "yahoo", "binance"], help="Data Provider")
    backtest_parser.add_argument("--source", type=str, default="auto", choices=["auto", "yahoo", "binance"], help="Data Provider")

    
    args = parser.parse_args()
    
    if args.command == "train":
        pipeline = TrainingPipeline(args.ticker, mode=args.mode, source=args.source)
        pipeline.run(period=args.period)
        
    elif args.command == "predict":
        pipeline = InferencePipeline(args.ticker, mode=args.mode, source=args.source)
        pipeline.run()

    elif args.command == "backtest":
        pipeline = BacktestPipeline(args.ticker, mode=args.mode, source=args.source, threshold=args.threshold, risk_pct=args.risk, adx_threshold=args.filter_adx, trend_filter=args.trend_filter)
        pipeline.run(period=args.period)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()