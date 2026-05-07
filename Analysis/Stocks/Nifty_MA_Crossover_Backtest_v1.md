# Real Data Analysis — Session 1

**Date:** April 2026  
**Markets analysed:** Nifty 50, S&P 500  
**Type:** Foundation work for Project 1 backtesting engine

---

## What We Built

A complete market analysis pipeline from scratch:

1. Download real market data
2. Calculate daily returns and basic stats
3. Plot rolling Sharpe ratio
4. Build a moving average crossover strategy
5. Backtest the strategy vs buy & hold

---

## The Complete Script

```python
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# download and clean columns
nifty = yf.download("^NSEI", period="1y")
nifty = nifty.droplevel(1, axis=1)   # removes MultiIndex ticker level

# explore
print(nifty.head())
print(nifty.shape)
print(nifty.isnull().sum())

# daily returns
nifty['Return'] = nifty['Close'].pct_change()
print("Best Day:", nifty['Return'].idxmax(), nifty['Return'].max())
print("Worst Day:", nifty['Return'].idxmin(), nifty['Return'].min())

up_days = (nifty['Return'] > 0).sum()
down_days = (nifty['Return'] < 0).sum()
print(f"Up Days = {up_days}, Down Days = {down_days}")

# rolling Sharpe ratio
risk_free = 0.065 / 252
excess_return = nifty['Return'] - risk_free
sharpe = excess_return.rolling(30).mean() / excess_return.rolling(30).std() * (252**0.5)

sharpe.plot(title='Rolling 30-day Sharpe Ratio — Nifty 50')
plt.axhline(y=0, color='red', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Sharpe Ratio')
plt.show()

# moving average crossover
nifty['MA20'] = nifty['Close'].rolling(20).mean()
nifty['MA50'] = nifty['Close'].rolling(50).mean()
nifty['Signal'] = 0
nifty.loc[nifty['MA20'] > nifty['MA50'], 'Signal'] = 1

nifty['Close'].plot(label='Close', figsize=(12,5))
nifty['MA20'].plot(label='MA20')
nifty['MA50'].plot(label='MA50')
plt.legend()
plt.title('Nifty 50 — Moving Average Crossover')
plt.show()

# backtest
nifty['Strategy_Return'] = nifty['Signal'].shift(1) * nifty['Return']
nifty['Buy_Hold'] = (1 + nifty['Return']).cumprod()
nifty['Strategy'] = (1 + nifty['Strategy_Return']).cumprod()

print(f"Buy & Hold Return: {(nifty['Buy_Hold'].iloc[-1]-1) * 100:.2f}%")
print(f"Strategy Return: {(nifty['Strategy'].iloc[-1]-1) * 100:.2f}%")
```

---

## Key Technical Notes

**`droplevel(1, axis=1)`** — yfinance returns a MultiIndex with ticker name as second level. This removes it so columns are just `Close`, `High`, `Low` etc. Always add this after download.

**`Signal.shift(1)`** — shifts signal by 1 day. You can only act on yesterday's signal, not today's — you don't know today's MA crossover until market closes. Without shift(1) you'd be looking into the future (data leakage).

**`cumprod()`** — cumulative product. Compounds returns over time. (1 + r1) × (1 + r2) × ... = how $1 grew. Always use this for equity curves, not cumsum().

**`droplevel` must come before any column access** — if you try `nifty['Close']` before dropping the MultiIndex level, you get a KeyError.

---

## Results — Nifty 50 (1 year)

- Best day: May 12, 2025 — +3.82%
- Worst day: March 19, 2026 — -3.26%
- Up days: 128, Down days: 119
- Nifty lost -1.44% over the year — tariff crash wiped all gains

---

## Results — S&P 500 vs Nifty Comparison

- S&P had more up days (144 vs 128) and spent more time above zero Sharpe
- Both crashed simultaneously in April 2026 — Trump tariff shock
- S&P recovered faster — higher liquidity
- **Correlation breakdown** — normally uncorrelated markets moved together during the crisis

> Correlation breakdown: during market stress, diversification across geographies fails. Assets that normally move independently become highly correlated exactly when you need diversification most.

---

## Backtesting Results — MA Crossover

|Strategy|Period|Return|
|---|---|---|
|Buy & Hold|1 year|-1.44%|
|MA 20/50 crossover|1 year|-3.05%|
|MA 10/50 crossover|1 year|+2.67%|
|Buy & Hold|5 years|+64.98%|
|MA 50/200 (Golden Cross)|5 years|+24.19%|

**Key finding:** Buy & hold beat every MA crossover strategy over 5 years. In a strong bull market (Nifty 2020-2025), trend following underperforms because being out of the market even briefly costs returns.

---

## MA Crossover Logic

**Signal = 1 (bullish):** MA20 above MA50 — short term momentum stronger than long term **Signal = 0 (bearish):** MA20 below MA50 — short term momentum weaker

**Why it fails:**

- **Whipsaws** — choppy markets cause repeated false signals, each costing transaction fees
- **Lagging** — MAs react to past prices, always late. Exit after damage done, enter after recovery started
- **Bull market drag** — any time out of market in a bull run costs returns

**Timeframes:**

- 5/20 — very fast, very noisy
- 10/50 — fast, worked best on 1-year Nifty
- 20/50 — medium, standard
- 50/200 — slow, Golden Cross/Death Cross, needs 2+ years of data

---

## The Core Lesson

> _A strategy that looks logical on paper can lose money in practice. Backtesting exists to test before trusting with real capital. A strategy must beat buy & hold consistently across multiple market conditions — not just cherry-picked periods — to be worth trading. Otherwise just buy an index fund._

> _The best performing MA combination (10/50) over 1 year might be pure luck — overfitting. Always test on out-of-sample data before trusting any result._

---

## What Comes Next — Project 1

This session built the foundation. Project 1 adds:

- Max drawdown calculation
- Win rate (% of profitable trades)
- Sharpe ratio of the strategy itself
- Multiple assets and strategies
- Proper out-of-sample testing

The signal column, cumprod equity curve, and shift(1) logic are reused directly in Project 1.



