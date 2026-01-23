---
trigger: always_on
---

# Architecture & Technical Stack

## File Structure (`src/`) & Responsibilities
- `main.py`: **Entry Point.** Must accept CLI arguments (e.g., `--mode swing` or `--interval 1h`). Orchestrates the pipeline based on the selected mode.
- `data_loader.py`: 
  - Must support dynamic intervals (`1d`, `1wk`, `1h`, `90m`).
  - Must handle API limitations (e.g., Yahoo Finance 730 days limit for hourly data).
- `features.py`: **Mathematical transformations.** Must be agnostic of the timeframe (calculation logic for RSI is the same for 1H or 1D).
- `model.py`: Training logic. **Crucial:** Models must be saved/loaded separately based on timeframe (e.g., `model_xgboost_1h.pkl` vs `model_xgboost_1d.pkl`).
- `risk_manager.py`: Adapts ATR calculation to the current data interval.

## Coding Standards
- **Typing:** Python 3.10+ Type Hints are mandatory.
- **Precision:** Use `float64` for all financial calculations.
- **Timezone:** All internal logic in UTC. Conversion to `Europe/Paris` only happens in `notion_publisher.py`.

## Packagess
- **Installation:** All packages must be installed directly inside the venv.

## Error Handling
- Validate data sufficiency: If `Intraday` mode is requested but data is missing (e.g., gaps), raise `InsufficientDataError`.