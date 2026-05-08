---

## tags: [quant, practice, post-report, pandas, debugging] date: 2026-05-08 session: Multi-Asset Analysis (Nifty, Gold, Bitcoin) status: done
---
# 📋 Practice Post-Report — Multi-Asset Analysis

## What Was Built
#8th_May_2026
5-section analysis on Nifty 50, Gold, Bitcoin (2 years daily):

1. Weekly best/worst returns
2. Rolling Sharpe + Rolling Correlation
3. Drawdown curves + max drawdown dates
4. Monthly seasonality bar chart
5. Summary table

---

## Mistakes & Struggles

### 1. `ffill()` Placement

**Wrong:**

```python
returns = Data_1.dropna().pct_change()
```

**Right:**

```python
Data_1 = Data_1.ffill()
returns = Data_1.pct_change().dropna()
```

ffill() must come before pct_change() — fill gaps in price data first, then calculate returns. dropna() comes after pct_change() to remove the first NaN row.

---

### 2. Series vs Single Value — strftime() Error

**Wrong:**

```python
print(f"Best: {Data_weekly.idxmax().strftime('%B %Y')}")
# idxmax() on DataFrame returns a Series — can't call strftime on Series
```

**Right:**

```python
for col in Data_weekly.columns:
    print(f"{col}: {Data_weekly[col].idxmax().strftime('%B %Y')}")
# Data_weekly[col].idxmax() returns a single date — strftime works
```

> Always ask: "Is this a Series or a single value?" before calling any method.

---

### 3. Wrong Variable in Sharpe Formula

**Wrong:**

```python
Sharpe = (Avg_Return - 0.065) / Annualised_vol
# Avg_Return is a 12×3 monthly DataFrame — wrong shape
```

**Right:**

```python
A_return = Total_Return * (252 / trading_days)
Sharpe = (A_return - 0.065) / Annualised_vol
# A_return is annualised return — correct shape (Series with one value per asset)
```

---

### 4. plt.show() Blocking Execution

Charts block code execution until the window is closed manually.

**Fix:** Always close chart window before code continues. Or add:

```python
plt.show()
plt.close()  # releases the plot
```

---

### 5. Rolling Correlation → Wrong Chart Type

**Wrong:**

```python
sns.heatmap(returns_rolling)  # rolling corr is a time Series, not a matrix
```

**Right:**

```python
plt.plot(returns_rolling)  # line plot for time-varying data
```

> Heatmap = static correlation matrix (`returns.corr()`). Line plot = rolling/time-varying correlation.

---

## What Came Naturally ✅

- Drawdown formula (`cummax()` logic)
- Sharpe formula structure
- `groupby(index.month)` for seasonality
- Summary table DataFrame structure
- `resample('W').last()` for weekly data

---

## Focus For Next Session

- Loop pattern: `for col in df.columns` — use whenever operating on multiple assets
- Always ask before calling any method: **"Series or single value?"**
- `ffill()` → `pct_change()` → `dropna()` — memorise this order
- `plt.show()` then `plt.close()` when plotting mid-script

---

