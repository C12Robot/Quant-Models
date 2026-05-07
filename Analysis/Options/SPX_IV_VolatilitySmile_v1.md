---

## tags: [quant, options, IV, volatility-smile, CBOE, python, pandas] date: 2026-05-06 project: Quant 1 status: done
---

# 📘 Section 3 — SPX Options IV & Volatility Smile

## Concept

**Implied Volatility (IV)** — market's expectation of future volatility, backed out from option prices. Higher IV = market expects bigger moves.

**Volatility Smile** — IV plotted across strikes. In theory should be flat. In reality:

- OTM puts have higher IV (demand for downside protection)
- ATM has lowest IV
- OTM calls slightly higher
- Result: U-shaped curve

**Key columns from CBOE chain:**

|Column|Meaning|
|---|---|
|`Strike`|Price at which option can be exercised|
|`IV`|Implied volatility for calls|
|`IV.1`|Implied volatility for puts|
|`Delta`|Option price sensitivity to $1 move in underlying|
|`Gamma`|Rate of change of delta|
|`Bid/Ask`|Market maker prices|
|`Volume`|Contracts traded today|
|`Open Interest`|Total open contracts|

---

## Data Source

- **CBOE delayed quotes** → SPX options chain CSV
- `skiprows=3` — skips CBOE header rows before actual data

---

## Code

```python
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("june_2026.csv", skiprows=3)

# pick first expiration
expirations = df['Expiration Date'].dropna().unique()[0]
df_exp = df[df['Expiration Date'] == expirations].copy()

# clean data
df_exp = df_exp.dropna(subset=['Strike', 'IV', 'IV.1'])
df_exp['Strike'] = pd.to_numeric(df_exp['Strike'], errors='coerce')
df_exp = df_exp.dropna(subset=['Strike'])

# ATM = median strike
atm = df_exp['Strike'].median()
atm_strike = df_exp['Strike'].iloc[
    (df_exp['Strike'] - atm).abs().argsort()[:1]
].values[0]

# plot
plt.figure(figsize=(12, 5))
plt.plot(df_exp['Strike'], df_exp['IV'], label='Calls IV', color='blue')
plt.plot(df_exp['Strike'], df_exp['IV.1'], label='Puts IV', color='orange')
plt.axvline(x=atm_strike, color='red', linestyle='--', label=f'ATM: {atm_strike}')
plt.title(f'SPX Volatility Smile — Expiry: {expirations}')
plt.xlabel('Strike')
plt.ylabel('Implied Volatility (%)')
plt.legend()
plt.tight_layout()
plt.show()
```

---

## Key Code Concepts

**`skiprows=3`** — CBOE CSV has metadata in first 3 rows. Skip them to get clean column headers.

**`dropna(subset=[...])`** — removes rows where specific columns are NaN. Needed because CBOE chain has blank rows between sections.

**`pd.to_numeric(errors='coerce')`** — converts Strike column to float. `errors='coerce'` turns unparseable values into NaN instead of crashing.

**`argsort()[:1]`** — sorts by distance from ATM price, takes index of the closest strike. Returns ATM strike automatically.

**`df['Strike'].median()`** — used as ATM proxy when actual spot price is unknown from the CSV.

---

## Limitations Encountered

- CBOE near-expiry CSV (1 day to expiry) had only 6 strikes → straight line instead of smile
- Need 2-4 weeks to expiry for 50+ strikes and proper U-shape
- yfinance options API broken in current version (use CBOE CSV instead)

> [!NOTE] Why the Smile Matters Flat IV = Black-Scholes world (theoretical). Smile = real world. OTM puts are expensive because funds buy them as insurance. This creates the skew. Understanding the smile is essential for options pricing and trading.

---

## Next Steps

- [ ] Download expiry 2-4 weeks out from CBOE for proper smile shape
- [ ] Add volume as bar chart below IV plot
- [ ] Plot IV surface (strike vs expiry vs IV) — 3D chart
- [ ] Connect to Section 4 — use ATM IV as volatility input for Monte Carlo

---
