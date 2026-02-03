---
trigger: always_on
---

# Testing Guidelines

## Frameworks
- **Unit Testing:** `pytest` is the standard frameowrk.
- **Mocking:** Use `unittest.mock` or `pytest-mock` to isolate dependencies (e.g., API calls).

## Testing Pyramid
1.  **Unit Tests (70%):** Test individual functions and classes classes in isolation (e.g., `Indicator.calculate()`).
2.  **Integration Tests (20%):** Test interaction between components (e.g., `DataLoader` fetching data and `FeatureEngineer` processing it).
3.  **End-to-End / Backtests (10%):** Full system simulation.

## Backtesting Standards
- **Authenticity:** Backtests must account for slippage and realistic fees.
- **Split:** Always use Out-of-Sample data for final verification.
- **Metric:** Sharpe Ratio and Max Drawdown are key metrics.
