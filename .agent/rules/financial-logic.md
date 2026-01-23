---
trigger: always_on
---

# Financial Logic & SMC Rules

## Timeframe Strategy (Multi-Timeframe)
The system operates in two distinct modes. The logic must adapt accordingly:

### Mode 1: SWING (Horizon: 5-15 Days)
- **Bias/Trend Timeframe:** Weekly (W1).
- **Execution/Entry Timeframe:** Daily (D1).
- **Target:** Capture mid-term trend moves.

### Mode 2: INTRADAY / SNIPER (Horizon: 1-3 Days)
- **Bias/Trend Timeframe:** Daily (D1).
- **Execution/Entry Timeframe:** 1 Hour (H1) or 4 Hours (H4).
- **Target:** Capture volatility within the daily range or precise entry into a D1 trend.

## Smart Money Concepts (SMC) Implementation
Prioritize these concepts for entry precision:
- **FVG (Fair Value Gap):** Must be detected on the *Execution Timeframe*.
- **Market Structure Shift (MSS):** Wait for a candle close creating a CHoCH (Change of Character) on the *Execution Timeframe* aligned with *Bias Timeframe*.
- **Premium vs Discount:** Only Buy in Discount zones (equilibrium < 50%), only Sell in Premium zones (equilibrium > 50%).

## Risk Management (NON-NEGOTIABLE)
- **R/R Ratio:** Minimum Risk/Reward ratio is **1:2** (Swing) and can go up to **1:3** (Intraday).
- **Stop Loss:** - **Dynamic:** Placed below/above the valid Swing Low/High or the Order Block on the *Execution Timeframe*.
  - **ATR Buffer:** Add 1x ATR of the *Execution Timeframe* to avoid noise wicks.
- **Session Logic (Intraday only):** Ignore signals generated outside London (08:00-11:00 UTC) or New York (13:00-17:00 UTC) sessions.

## Asset Class Adaptation (Stocks vs Crypto)
The system must handle both Asset Classes. Apply these specific logic variations:

### Crypto Specifics
- **Market Hours:** 24/7. No "Market Close" logic.
- **Data Continuity:** Do not remove weekend data.
- **Precision:** Prices must be handled with up to **8 decimal places** (Satoshis/Gwei).
- **Exchange:** Prefer Binance or Bybit data over Yahoo Finance for Intraday accuracy.

### Stock Specifics
- **Market Hours:** Mon-Fri (Exchange specific).
- **Gaps:** Overnight gaps are common and significant.
- **Precision:** Standard 2 decimal places.