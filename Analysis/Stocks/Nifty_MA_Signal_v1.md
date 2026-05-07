# Moving Average Crossover — Nifty 50 Analysis

**Date:** April 2026  
**Type:** Project log — foundation for Project 1 backtesting engine

---

## The Code

```python
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

nifty = yf.download("^NSEI", period="1y")

# moving averages
nifty['MA20'] = nifty['Close'].rolling(20).mean()
nifty['MA50'] = nifty['Close'].rolling(50).mean()

# signal — 1 = buy, 0 = sell
nifty['Signal'] = 0
nifty.loc[nifty['MA20'] > nifty['MA50'], 'Signal'] = 1

# plot
nifty['Close'].plot(label='Close', figsize=(12,5))
nifty['MA20'].plot(label='MA20')
nifty['MA50'].plot(label='MA50')
plt.legend()
plt.title('Nifty 50 — Moving Average Crossover')
plt.show()
```

---

## The Logic

**MA20 above MA50** → recent prices higher than longer term average → short term momentum stronger → bullish → stay in

**MA20 below MA50** → recent prices weaker than longer term average → bearish → get out

---

## What the Chart Showed (April 2026 run)

- May–Jan 2026 — MA20 consistently above MA50, market in uptrend, bullish signal throughout
- Feb–Mar 2026 — MA20 crossed below MA50, bearish signal — this was the warning before the tariff crash
- Apr 2026 — Trump tariff shock. Price crashed hard, MA20 fell sharply, MA50 still declining
- May 2026 — Price recovering but MA20 still below MA50 — signal still bearish, not confirmed recovery yet

A trader following this signal would have:

- Been in from May 2025 to Feb 2026 — caught the entire uptrend
- Exited around Feb-March 2026 — avoided most of the crash
- Still out as of April 2026 — MA20 still below MA50

---

## Limitations of MA Crossover

**1. Whipsaws** — in choppy/sideways markets the MAs cross back and forth with no real trend. False signals every few days, each costing transaction fees. Visible in July-Aug 2025 on the chart.

**2. Lagging indicator** — MAs are based on past prices so they always react late. By the time MA20 crosses below MA50, significant damage already done. Never catches exact tops or bottoms.

**3. Strong news events** — tariff shocks, geopolitical events cause price to drop so fast the MA signal is useless. Crossover happens after most of the damage.

**4. Timeframe dependent** — 20/50 works for medium term. For short term use 5/20. For long term use 50/200 (Golden Cross / Death Cross — famous market signals).

---

## Comparing Nifty vs S&P 500

- S&P 500 spent more time above zero Sharpe — genuinely rewarding risk-takers in mid-2025
- Nifty barely above zero in same period — Indian fixed deposits outperformed the index
- Both crashed simultaneously in April 2026 tariff shock — **correlation breakdown**
- S&P recovered faster — US markets have higher liquidity

**Correlation breakdown** — assets that normally have low correlation become highly correlated during market stress. Diversification across geographies fails exactly when you need it most. Core risk management problem in quant finance.

---

## Key Concepts Learned

**MA Crossover** — simple trend following signal. Works in trending markets, fails in choppy markets. Must be backtested before trusting with real capital.

**Whipsaw** — when price oscillates around the MA causing repeated false signals. Kills returns through transaction costs.

**Golden Cross** — MA50 crosses above MA200 → long term bullish signal **Death Cross** — MA50 crosses below MA200 → long term bearish signal

---

## Next Step — Backtest It

Calculate actual returns from following the signal vs just holding Nifty. That's Project 1.

The signal column is already built — `nifty['Signal'] = 1` when bullish, `0` when bearish. Next step: multiply signal by next day's return to get strategy returns.