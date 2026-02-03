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
- **Setup Timeframe:** 1 Hour (H1) or 4 Hours (H4).
- **Execution/Refinement Timeframe (Crypto):** 15 Minutes (M15) or 5 Minutes (M5).
    *   *Note:* Use these lower timeframes ONLY for precise entry (e.g., waiting for MSS inside an H1 POI). Do not use for bias generation.
    *   *Noise Warning:* Avoid M1 unless specifically scalping; M5/M15 provides the best signal-to-noise ratio for snipping.
- **Target:** Capture volatility within the daily range or precise entry into a D1 trend.

## Smart Money Concepts (SMC) Implementation
Prioritize these concepts for entry precision:
- **FVG (Fair Value Gap):** Must be detected on the *Execution Timeframe*.
- **Market Structure Shift (MSS):** Wait for a candle close creating a CHoCH (Change of Character) on the *Execution Timeframe* aligned with *Bias Timeframe*.
- **Premium vs Discount:** Only Buy in Discount zones (equilibrium < 50%), only Sell in Premium zones (equilibrium > 50%).

## Risk Management (NON-NEGOTIABLE)
- **R/R Ratio:** Minimum Risk/Reward ratio is **1:2** (Swing) and can go up to **1:3** (Intraday).
- **Stop Loss:** 
    - **Dynamic:** Placed below/above the valid Swing Low/High or the Order Block on the *Execution Timeframe*.
    - **ATR Buffer:** Add 1x ATR of the *Execution Timeframe* to avoid noise wicks.
- **Session Logic (Intraday only):** Ignore signals generated outside London (08:00-11:00 UTC) or New York (13:00-17:00 UTC) sessions.

## Asset Class Logic

### Crypto (Active)
- **Market Hours:** 24/7. No "Market Close" logic.
- **Data Continuity:** Do not remove weekend data.
- **Precision:** Prices must be handled with up to **8 decimal places** (Satoshis/Gwei).
- **Exchange:** Prefer Binance or Bybit data over Yahoo Finance for Intraday accuracy.

### Stocks & Forex (Reserved for Future)
- *Note:* Logic for these asset classes will be implemented in future modules implementing the generic `Asset` interface.
- **Stocks:** Handle Mon-Fri market hours and overnight gaps.
- **Forex:** Handle high leverage and tick data specifics.