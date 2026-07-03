# Faber — A Quantitative Approach to Tactical Asset Allocation

**Author:** Mebane Faber (Cambria) **Year:** 2007 (notes based on the 2013 updated version, data through ~2012) **Link:** https://ssrn.com/abstract=962461

---

## What it's about

A simple, mechanical trend-following model: hold each asset class when its monthly price is above its 10-month SMA, move to cash (T-bills) when below. Applied across five global asset classes with equal weights. The claim: equity-like returns with bond-like volatility and drawdown — risk reduction with no cost to return.

---

## Why drawdowns matter (the framing)

- A 75% decline requires a 300% gain to break even — ≈ compounding at 10% for 15 years
- Avoiding large drawdowns matters more for compound returns than maximising average returns
- 2008 showed diversification alone fails: virtually all asset classes fell together

**Bond context (2000–2011):** compound return 7.07% (4.5% real), but future bond return ≈ starting yield, which fell below 2% — forward returns capped

**CAPE reference points (mean-reverting, historical average ~16):**

|CAPE|Context|
|---|---|
|~13|2009 bottom — generational buying opportunity|
|~23|2011 — near fair value|
|~30|1929 pre-Depression|
|~44|2000 dotcom peak|

---

## The model

### Universe (5 asset classes, equal weight)

|Asset Class|Index|
|---|---|
|US Stocks|S&P 500|
|Foreign Stocks|MSCI EAFE|
|Real Estate|NAREIT|
|Commodities|GSCI|
|Bonds|US 10-Year Treasury|

Benchmarks: T-bills (cash / risk-free), CPI (inflation).

### Rules

```
BUY:  monthly close > 10-month SMA → 100% long that asset
SELL: monthly close < 10-month SMA → 100% cash (90-day T-bill)
```

- Signals evaluated and executed at month-end close
- Total-return series (dividends included), monthly frequency
- Same parameters for every asset class — no per-asset optimisation
- Price-based only, fully mechanical, no discretion

---

## Key results

### S&P 500: timing vs buy & hold (from 1901)

|Metric|Buy & Hold|Timing|
|---|---|---|
|Average return|11.26%|11.22%|
|Compound return|9.32%|10.18%|

Same average return, +86bp compound — the entire edge comes from lower volatility. Volatility drag destroys compounding; timing wins by avoiding major bear markets, despite underperforming in roughly half of individual years.

### GTAA portfolio vs equal-weight buy & hold

|Metric|Buy & Hold|GTAA Timing|
|---|---|---|
|Max drawdown|~46%|< 10%|
|Volatility|double-digit|single-digit|
|Down years since 1973|multiple|1 (< −1%)|

Post-2005: outperformed in only 3 of 7 years, yet beat B&H by ~2%/yr with far lower drawdown.

---

## Practical considerations

- **Turnover:** ~70%/yr vs ~20% for B&H → ~50bp additional tax haircut; best in tax-deferred accounts
- **Tax structure of signals:** losses tend to be short-term (quick stop-outs), gains tend to be long-term (trends held) — relatively favourable
- **Behavioral edge:** mechanical rules remove emotional decision-making — arguably the biggest real-world advantage

---

## Core conclusion

> A non-discretionary trend-following model acts as a risk-reduction technique with no adverse impact on return.

The point is not maximising returns — it's surviving the drawdowns that destroy most investors. Future compound returns are dominated by volatility avoidance, not return chasing.

---

## Key terms

- **GTAA** — Global Tactical Asset Allocation: shifting exposure across global asset classes by rule, not stock picking
- **10-month SMA** — simple moving average of monthly closes; ≈ 200-day SMA at monthly frequency
- **Volatility drag** — gap between average and compound return caused by variance
- **CAPE** — cyclically adjusted P/E (Shiller); mean-reverting valuation gauge
- **Total return series** — price + dividends reinvested