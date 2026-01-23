---
trigger: always_on
---

# Machine Learning Guidelines

## Dynamic Target Labeling
The prediction horizon depends on the pipeline mode. Do not hardcode "5 days".
- **Concept:** Predict outcome **N bars** ahead.
- **Configuration:**
  - If Mode == SWING (D1): Target = 5 bars (1 week).
  - If Mode == INTRADAY (H1): Target = 8 to 12 bars (End of Session).

## Training & Validation
- **NO SHUFFLING:** Always use `TimeSeriesSplit`.
- **Regime Filtering:** Train separate models for different volatility regimes if possible (High Volatility vs Ranging), or include Volatility as a core feature.

## Feature Engineering Rules
- **Lag Features:** When creating lag features (e.g., `close_t-1`), ensure they respect the current timeframe interval.
- **Normalization:** Scale features strictly on the **Training Set** parameters to avoid look-ahead bias.

## Model Evaluation
- Primary Metric: **Precision** (on the positive class).
- Focus on **Profit Factor** rather than raw Accuracy. A model with 40% accuracy but 1:3 R/R is superior to 70% accuracy with 1:1 R/R.