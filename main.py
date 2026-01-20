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
    train_parser.add_argument("--ticker", type=str, default="TSLA", help="Ticker symbol (default: TSLA)")
    train_parser.add_argument("--period", type=str, default="5y", help="Data period (default: 5y)")
    
    # Predict Command
    predict_parser = subparsers.add_parser("predict", help="Run inference and publish to Notion")
    predict_parser.add_argument("--ticker", type=str, default="TSLA", help="Ticker symbol (default: TSLA)")

    # Backtest Command
    backtest_parser = subparsers.add_parser("backtest", help="Simulate performance on past data")
    backtest_parser.add_argument("--ticker", type=str, default="TSLA", help="Ticker symbol")
    backtest_parser.add_argument("--period", type=str, default="2y", help="Data period")

    
    args = parser.parse_args()
    
    if args.command == "train":
        pipeline = TrainingPipeline(args.ticker)
        pipeline.run(period=args.period)
        
    elif args.command == "predict":
        pipeline = InferencePipeline(args.ticker)
        pipeline.run()

    elif args.command == "backtest":
        pipeline = BacktestPipeline(args.ticker)
        pipeline.run(period=args.period)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()