# Faber (2007) — A Quantitative Approach to Tactical Asset Allocation

Independent replication of Mebane Faber's GTAA model from the original methodology; results validated against the paper's published findings.

**Paper:** Faber, M. (2007, updated 2013). _A Quantitative Approach to Tactical Asset Allocation._ Journal of Wealth Management. [SSRN 962461](https://ssrn.com/abstract=962461)

---

## The paper's claim

A simple trend-following rule — hold each asset class when its monthly close is above its 10-month SMA, otherwise sit in T-bills — applied across five global asset classes delivers equity-like returns with bond-like volatility and drawdown. The edge comes from avoiding deep bear markets, not from return maximisation: lower volatility drag lifts compound returns even when average returns match buy-and-hold.

## What I built

Python/pandas backtest of the full GTAA portfolio:

- **Universe:** SPY, EFA, VNQ, GSG, TLT (US equities, international equities, real estate, commodities, bonds), equal-weighted 20% sleeves
- **Signal:** monthly close > 10-month SMA → long the asset; below → cash at the actual 13-week T-bill rate (^IRX), not a flat assumption
- **Execution:** month-end close; signals shifted one month to eliminate lookahead bias
- **Benchmark:** equal-weight buy-and-hold of the same five assets over the identical sample
- **Sample:** May 2007 – June 2026 (230 months), constrained by GSG inception and 10-month SMA warm-up; incomplete final months excluded automatically

## Results

|Metric|GTAA Strategy|Buy & Hold|
|---|---|---|
|CAGR|5.15%|5.30%|
|Sharpe|**0.56**|0.36|
|Annualised volatility|**6.8%**|12.8%|
|Max drawdown|**−9.7%**|−45.9%|
|Worst year|**−3.8%**|−27.4%|

**Headline:** the strategy matched buy-and-hold's compound return with roughly half the volatility and a fifth of the maximum drawdown — Sharpe 0.56 vs 0.36. This reproduces the character of Faber's result: trend timing is a risk-reduction technique, not a return-enhancement one. Consistent with the paper, timing lags during sustained bull runs (2022–2025) and earns its keep in 2008- and 2020-style drawdowns, where the model moved to cash before the worst of the declines.

![Equity curves](https://claude.ai/chat/results/equity_curves.png)

## Divergence from the paper

Direction of results matches Faber; magnitudes are not directly comparable:

- **Sample period:** 2007–2026 vs Faber's 1973–2012. My window is one structural regime (post-GFC, low-rate, US-led bull); his spans multiple.
- **Instruments:** ETF closes (auto-adjusted) vs the paper's index total-return series.
- **Cash rate:** ^IRX 13-week T-bill yield vs the paper's 90-day T-bill total return.
- **Costs:** transaction costs and taxes excluded, as in the paper's base case (~70% annual turnover would reduce net results modestly).

## Repository contents

```
├── README.md
├── DEVLOG.md          # dated build log: decisions, bugs, fixes
├── notes.md           # condensed paper notes
├── src/
│   └── gtaa_backtest.py
└── results/
    ├── summary.csv
    ├── monthly_returns.csv
    └── equity_curves.png
```

## How to run

```bash
pip install pandas numpy yfinance matplotlib
python src/gtaa_backtest.py
```

Downloads data from Yahoo Finance at runtime; outputs regenerate into `results/`. Numbers will drift slightly as the sample extends with new months.