

> **CV Quant Project | Pine Script → Pandas Backtester**

---

## What This Project Is

A rigorous backtest of the **Opening Range Breakout (ORB)** strategy, enhanced with a **VIX-based regime filter** to identify _when_ ORB actually works — not just whether it works overall.

**Core research question:**

> _Does ORB generate statistically significant alpha only in high-volatility regimes?_

This is a real research question, not just a "run a backtest" exercise. The output is a conditional finding with proper statistical validation.

---

## Strategy: ORB (Opening Range Breakout)

### Rules

- **Opening Range**: Mark the high and low of the first 15-minute candle at market open
- **Bias**:
    - Price breaks **above** range → Long bias
    - Price breaks **below** range → Short bias
    - Price stays **inside** range → Wait
- **Entry**: After breakout, wait for price to **pull back and retest** the range boundary
- **Stop Loss**: 10 points below/above entry
- **Take Profit**: 20 points (1:2 Risk-Reward Ratio)
- **Daily Limits**: Max 3 trades per day

### Timeframe

- **Chart**: 5-minute candles
- **Opening Range Definition**: First 15-minute candle (pulled into 5-min chart via `request.security`)

---

## The Regime Filter (What Makes This Project Interesting)

ORB works best when the market is **moving with conviction** — not chopping sideways. The regime filter identifies those conditions.

### Filter: VIX-Based

- **High volatility regime** (VIX > threshold) → ORB signals are **active**
- **Low volatility regime** (VIX ≤ threshold) → ORB signals are **suppressed**

### Why VIX?

- High VIX = market fear/uncertainty = big directional moves = ORB thrives
- Low VIX = calm, range-bound market = ORB generates false breakouts
- This is a logical, economically motivated filter — not curve-fitting

### Alternative Filter (if VIX unavailable): ADX

- ADX > 25 → trending market → ORB active
- ADX ≤ 25 → ranging market → skip trade

---

## Asset & Data

|Phase|Asset|Data Source|
|---|---|---|
|Phase 1 (now)|SPY / Nifty 50|yfinance (free, unlimited)|
|Phase 2 (later)|ES Futures (E-mini S&P 500)|QuantConnect or broker feed|

**Why stocks first:** ES intraday futures data requires paid access. SPY uses identical logic and is free. Upgrade to ES later with minimal code changes.

---

## Build Phases

### Phase 1 — Pine Script (Visual Validation)

- Plot ORB range (rectangle) on TradingView 5-min chart
- Plot breakout + retest signals visually
- Add VIX/ADX regime filter overlay
- **Goal:** Confirm the logic _looks_ correct before coding

### Phase 2 — Pandas Backtester

- Replicate Pine Script logic in Python
- Run on SPY historical data via yfinance
- Output: trade log, equity curve

### Phase 3 — Regime Analysis

- Split all trades by regime (high vol vs low vol)
- Compare Sharpe, win rate, avg RR across regimes
- **This is the core finding**

### Phase 4 — Statistical Validation

- **Walk-forward analysis** — test on unseen data windows
- **Monte Carlo simulation** — add slippage + noise, run 1000 iterations
- **Out-of-sample test** — hold back last 20% of data from start

---

## Output Metrics

|Metric|Description|
|---|---|
|Sharpe Ratio|Risk-adjusted return|
|Max Drawdown|Worst peak-to-trough loss|
|Win Rate|% of trades profitable|
|Avg RR|Actual risk-reward achieved|
|Regime Breakdown|All above metrics split by high/low vol regime|

---

## CV Line (Target)

> _"Backtested Opening Range Breakout strategy on SPY/ES with VIX-based regime filter. Found statistically significant improvement in Sharpe ratio during high-volatility regimes. Validated with walk-forward analysis and Monte Carlo simulation."_

---

## Tech Stack

|Tool|Purpose|
|---|---|
|TradingView Pine Script|Visual validation|
|Python + Pandas|Core backtester|
|yfinance|Free stock data|
|Matplotlib / Plotly|Equity curve + charts|
|NumPy|Monte Carlo simulation|
|QuantConnect (later)|ES futures data|

---

## What You'll Learn Building This

1. What a market regime is and why it matters
2. How VIX predicts breakout success
3. Conditional backtesting — splitting results by market condition
4. Walk-forward analysis — why in-sample results lie
5. Monte Carlo — stress-testing a strategy against randomness
6. Pine Script basics → Python translation

---

## Current Status

- [x] Strategy rules defined
- [x] Research question locked in
- [x] Asset and data source decided
- [x] Build phases planned
- [ ] Pine Script — ORB range plot
- [ ] Pine Script — breakout + retest signals
- [ ] Pine Script — regime filter overlay
- [ ] Pandas backtester
- [ ] Regime analysis
- [ ] Statistical validation