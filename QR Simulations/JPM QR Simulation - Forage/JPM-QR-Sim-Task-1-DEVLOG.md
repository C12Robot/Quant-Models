# JPMorgan Forage — Quantitative Research Virtual Experience

## Task 1: Natural Gas Price Estimation & Extrapolation

---

### Background

A commodity trading desk wants to price natural gas storage contracts. The available market data is only monthly snapshots (end-of-month price) — too coarse to price contracts accurately, and it doesn't extend far enough into the future for longer-term storage deals. The task: build a model that can estimate the gas price on **any** date — interpolating within the historical range and extrapolating up to a year beyond it — capturing the seasonal pattern that drives gas prices (higher in winter demand months, lower in summer).

**Data:** 48 monthly snapshots, 31 Oct 2020 → 30 Sep 2024, one price per month-end.

---

### Approach

Priced move ≈ **long-term trend + seasonal cycle**. A straight line (trend alone) can't capture the winter-peak/summer-dip pattern visible in the raw data, so the model combines:

- **`t`** — time in months since the first data point (captures the upward trend)
- **`sin(2πt/12)` and `cos(2πt/12)`** — a 12-month periodic pair. Using both (not just one) lets the fit find the seasonal wave's actual phase and amplitude — a single sine has a fixed peak position, but combining sin and cos with independent coefficients (`b·sin + c·cos`) can reconstruct a wave peaking wherever the real data peaks, without having to guess in advance whether gas prices top out in January or March.
- **A constant (intercept)** — vertical shift, so the fit doesn't get forced through zero.

These four terms are combined into one design matrix and fit in a single linear regression (`np.linalg.lstsq`), which finds the 4 coefficients that minimize total squared error between the model and the actual 48 prices.

---

### Code

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

data = pd.read_csv("Nat_Gas.csv")
data['Dates'] = pd.to_datetime(data['Dates'])
data = data.set_index('Dates')

# Build regressors: trend (t), seasonal (sin, cos), intercept
t = (data.index - data.index[0]).days / 30.44
X = np.column_stack([t, np.sin(2*np.pi*t/12), np.cos(2*np.pi*t/12), np.ones(len(t))])
coefficients, *_ = np.linalg.lstsq(X, data['Prices'].values, rcond=None)

def estimate_price(date):
    date = pd.to_datetime(date)
    t_new = (date - data.index[0]).days / 30.44
    return (coefficients[0]*t_new
            + coefficients[1]*np.sin(2*np.pi*t_new/12)
            + coefficients[2]*np.cos(2*np.pi*t_new/12)
            + coefficients[3])

# Validation checks — actual vs predicted
for d in ['2021-06-30', '2024-06-30', '2024-01-31']:
    print(d, "actual:", data.loc[d, 'Prices'], "| predicted:", estimate_price(d))

# Visualize: actual data + fitted/extrapolated curve (1 year past last observation)
plt.figure(figsize=(10,5))
plt.plot(data.index, data['Prices'], label='Actual')

future_dates = pd.date_range(data.index[0], data.index[-1] + pd.DateOffset(years=1), freq='D')
fitted = [estimate_price(d) for d in future_dates]
plt.plot(future_dates, fitted, label='Fitted + Extrapolated', linestyle='--')
plt.legend()
plt.show()
```

---

### Results

**Fitted coefficients** `[t, sin, cos, intercept]`:

```
[0.04570129, 0.68925774, -0.02557104, 10.13118661]
```

- `t` coefficient ≈ 0.0457/month → ~0.55/year upward trend, consistent with the raw data climbing from ~10 to ~12.8 over 4 years.
- Sizeable `sin` term confirms a real seasonal swing; small `cos` term means the wave is close to (but not exactly) sine-phase-aligned.
- Intercept 10.13 lines up with the actual Oct 2020 starting price.

**Validation — actual vs. predicted:**

|Date|Actual|Predicted|Error|
|---|---|---|---|
|2021-06-30|10.0|9.92|0.08|
|2024-06-30|11.5|11.56|0.06|
|2024-01-31|12.6|12.60|0.02|

All three checks within ~0.8% error — the model is well-calibrated across a summer trough, a summer mid-point, and a winter peak (the sharpest point on the chart), so it isn't just fitting the easy parts of the curve.

**Plot:** Actual (solid) vs. fitted+extrapolated (dashed) — visually the fitted curve tracks the seasonal pattern closely and extends smoothly one year past the last data point (Sep 2024 → Sep 2025), completing the extrapolation requirement.

---

### Mistakes made & fixed (learning log)

1. **Overwrote input arguments instead of transforming them** — happened twice: once assigning `data = pd.to_datetime(data['Dates'])` (destroyed the whole dataframe, keeping only dates) instead of `data['Dates'] = pd.to_datetime(data['Dates'])`; then again inside `estimate_price()`, initially writing `date = pd.to_datetime(data['Dates'])` instead of `date = pd.to_datetime(date)` — ignoring the actual function argument. **Lesson:** always transform the input you were given, not a different variable that happens to share a similar name.
    
2. **Operator precedence bug in date math** — wrote `data.index - data.index[0].day / 30.44`, which computes `.day/30.44` (just a day-of-month number) before subtracting, instead of `(data.index - data.index[0]).days / 30.44`. **Lesson:** parenthesize the subtraction before dividing — Python evaluates `.day`/division before the subtraction unless forced otherwise.
    
3. **Inconsistent seasonal period** — wrote `cos(2*np.pi*t_new)` in one draft, missing the `/12` that was present on the matching `sin` term. Mismatched periods would have broken the wave shape used for prediction even though the fit itself (trained on the correct `/12` version) was fine. **Lesson:** when a formula is reused across training and prediction, keep every term — including easy-to-miss `/12`-style constants — identical in both places.
    
4. **Date exact-match failure in validation** — `data.loc['2024-01-30']` threw an error because the actual snapshot was recorded on `2024-01-31` (January has 31 days). **Lesson:** `.loc` requires an exact index match; month-end dates vary by month length, so don't assume the 30th when checking a monthly snapshot — check the real date or use `.asof()`/nearest-match lookups.
    
5. **Defined the function inside the loop** — `estimate_price()` was initially declared inside the `for` loop used to test it, meaning it got redefined on every iteration for no reason and risked being unusable outside that scope. **Lesson:** define reusable functions once, outside any loop that calls them.
    
6. **Skipped direct numeric validation in favor of "the plot looks right"** — initially treated a visually plausible fitted curve as sufficient. A plot can hide small but real errors; the actual proof came from comparing `estimate_price()` output to the literal CSV value on specific dates (see Results table above), which is what actually confirmed the model works.
    

---

### Status

Task 1 complete and validated. Ready to move to Task 2 of the JPM Forage QR simulation.