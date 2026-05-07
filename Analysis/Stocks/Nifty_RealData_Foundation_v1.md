# Nifty 50 — Market Analysis Script

**Date:** April 2026  
**Type:** Project foundation — rewrite from memory to practice

---

## The Script

```python
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# download 1 year of Nifty 50 data
nifty = yf.download("^NSEI", period="1y")
print(nifty.head())
print(nifty.shape)
print(nifty.isnull().sum())

# daily returns
nifty['Return'] = nifty['Close'].pct_change()

# best and worst days — idxmax/idxmin give DATE, max/min give VALUE
# cannot chain: nifty['Return'].idxmax().max() — idxmax() returns a single date, not a Series
print("Best Day:", nifty['Return'].idxmax(), nifty['Return'].max())
print("Worst Day:", nifty['Return'].idxmin(), nifty['Return'].min())

# count up vs down days
up_days = (nifty['Return'] > 0).sum()
down_days = (nifty['Return'] < 0).sum()
print(f"Up Days = {up_days}, Down Days = {down_days}")

# rolling 30-day Sharpe ratio
risk_free = 0.065 / 252       # 6.5% annual rate converted to daily
excess_return = nifty['Return'] - risk_free
sharpe = excess_return.rolling(30).mean() / excess_return.rolling(30).std() * (252**0.5)
print(sharpe.tail(10))

# plot
sharpe.plot(title='Rolling 30-day Sharpe Ratio — Nifty 50')
plt.axhline(y=0, color='red', linestyle='--')   # reference line at zero
plt.xlabel('Date')
plt.ylabel('Sharpe Ratio')
plt.show()
```

---

## What Each Part Does

**`yf.download("^NSEI", period="1y")`** — pulls 1 year of OHLCV data for Nifty 50 from Yahoo Finance. Free, no API key needed.

**`pct_change()`** — calculates daily % return. Formula: (today - yesterday) / yesterday. First row = NaN (no previous row).

**`idxmax()` vs `max()`** — idxmax() returns the DATE of the max value. max() returns the VALUE itself. They are separate calls on the original Series — cannot be chained. `nifty['Return'].idxmax().max()` will throw an error because idxmax() returns a single date, not a Series.

**`(nifty['Return'] > 0).sum()`** — creates a True/False Series, then sums it. True = 1, False = 0. Counts how many days had positive returns.

**`risk_free = 0.065 / 252`** — converts annual risk-free rate to daily. India risk-free ≈ 6.5%. Divide by 252 trading days.

**`excess_return`** — how much more Nifty earned vs just putting money in a fixed deposit. This is what you're paid for taking market risk.

**`rolling(30).mean() / rolling(30).std()`** — average excess return divided by volatility over last 30 days. That's the raw Sharpe.

**`* (252**0.5)`** — multiply by √252 to annualise. Scales daily Sharpe to yearly so you can compare across investments.

**`axhline(y=0, color='red', linestyle='--')`** — draws a horizontal reference line at y=0. Above = Nifty beating fixed deposits. Below = fixed deposits better.

---

## What the Chart Showed (April 2026 run)

- Aug-Sep 2025 — Sharpe crashed to -6.5. Worst period of the year.
- Oct-Dec 2025 — Strong recovery, peaked near +5. Best performing period.
- Jan-Apr 2026 — Deteriorated again, deeply negative.
- May 2026 — Starting to recover toward zero.
- For most of the last year Nifty was below zero = Indian fixed deposits outperformed the index.

---

## Key Syntax Notes

```python
# idxmax and max are SEPARATE calls — never chain them
nifty['Return'].idxmax()   # date of max
nifty['Return'].max()      # value of max

# axhline — horizontal reference line
plt.axhline(y=0, color='red', linestyle='--')

# rolling window
series.rolling(30).mean()   # 30-day rolling average
series.rolling(30).std()    # 30-day rolling std deviation

# f-string formatting
print(f"Up Days = {up_days}, Down Days = {down_days}")
```

---

## This Script Is The Foundation Of Project 1

Every piece of the backtesting engine builds on this:

- Data download → same yfinance call
- Returns calculation → same pct_change()
- Performance metrics → Sharpe ratio formula is identical
- Plotting equity curves → same matplotlib setup

Rewrite this from memory every few days until it's instant.


Correlation breakdown — during market stress events like the April 2026 tariff shock, normally uncorrelated assets move together. Diversification across geographies fails exactly when you need it most. This is why quant risk models need stress testing, not just historical correlation.