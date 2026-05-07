---

## tags: [quant, multi-asset, monte-carlo, options, hedging, pandas, seaborn, matplotlib] date: 2026-05-07 project: Quant 1 status: done
---

# 📊 Multi-Asset Quant Analysis Engine

## Assets & Data

- Nifty 50, S&P 500, Gold, Bitcoin, ES Futures — 2 years daily via yfinance
- SPX Options chain — CBOE CSV (June 2026 expiry)

---

## Final Code

```python
import pandas as pd
import numpy as np
import seaborn as sns
import yfinance as yf
import matplotlib.pyplot as plt

# Download all 5 assets
tickers = ["^NSEI", "^GSPC", "GC=F", "BTC-USD", "ES=F"]
data = yf.download(tickers, period="2y")['Close']
data.columns = ['Nifty', 'SP500', 'Gold', 'BTC', 'ES']
returns = data.pct_change().dropna()

# Section 1 — Correlation heatmap + rolling volatility
sns.heatmap(returns.corr(), annot=True, cmap='coolwarm')
rolling_vol = returns.rolling(30).std() * (252**0.5)
rolling_vol.plot(figsize=(12,5), title='Rolling 30 Day Volatility')
plt.ylabel('Volatility')
plt.show()

# Section 2 — Drawdown
cumulative_returns = (1 + returns).cumprod()
drawdown = (cumulative_returns - cumulative_returns.cummax()) / cumulative_returns.cummax()
max_drawdown = drawdown.min()
for col in max_drawdown.index:
    print(f"{col} Max Drawdown: {max_drawdown[col]*100:.2f}%")
drawdown.plot(figsize=(12,5), title='Drawdown for 5 Assets')
plt.show()

# Section 3 — Options IV (CBOE CSV)
idk = pd.read_csv('june_2026.csv', skiprows=3)
expirations = idk['Expiration Date'].dropna().unique()[0]
idk_exp = idk[idk['Expiration Date'] == expirations].copy()
idk_exp = idk_exp.dropna(subset=['Strike', 'IV', 'IV.1'])
idk_exp['Strike'] = pd.to_numeric(idk_exp['Strike'], errors='coerce')
idk_exp = idk_exp.dropna(subset=['Strike'])
atm = idk_exp['Strike'].median()
atm_strike = idk_exp['Strike'].iloc[(idk_exp['Strike'] - atm).abs().argsort()[:1]].values[0]
plt.figure(figsize=(12,5))
plt.plot(idk_exp['Strike'], idk_exp['IV'], label='Calls IV', color='red')
plt.plot(idk_exp['Strike'], idk_exp['IV.1'], label='Puts IV', color='blue')
plt.axvline(x=atm_strike, color='black', linestyle='--', label=f'ATM: {atm_strike}')
plt.title('IV Analysis')
plt.legend()
plt.xlabel('Strike')
plt.ylabel('IV')
plt.show()

# Section 4 — Hedge Simulator + Monte Carlo
es_spot = data['ES'].dropna().iloc[-1]
es_vol = returns['ES'].std() * np.sqrt(252)
futures_price = es_spot
beta = 1.5
portfolio = 5050000
contract_size = futures_price * 250
N_contracts = round(beta * (portfolio / contract_size))

hedged_1, unhedged_1 = [], []
scenarios = np.random.normal(loc=es_spot, scale=es_spot*0.135, size=1000)
for scenario in scenarios:
    futures_pnl = (futures_price - scenario) * 250 * N_contracts
    unhedged = portfolio * (1 + beta * ((scenario - futures_price) / futures_price))
    hedged = unhedged + futures_pnl
    hedged_1.append(hedged)
    unhedged_1.append(unhedged)

hedged_values = np.array(hedged_1)
unhedged_values = np.array(unhedged_1)
print(f"Hedged std: {hedged_values.std():.2f}")
print(f"Unhedged std: {unhedged_values.std():.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12,5))
ax1.hist(hedged_values, bins=50, alpha=0.7, color='orange')
ax1.set_title('Hedged Returns')
ax2.hist(unhedged_values, bins=50, alpha=0.7, color='red')
ax2.set_title('Unhedged Returns')
plt.tight_layout()
plt.show()

# Section 5 — Summary Table
Total_return = (data.ffill().iloc[-1] / data.ffill().iloc[0]) - 1
Annualised_vol = returns.std() * np.sqrt(252)
trading_days = len(returns)
A_return = Total_return * (252 / trading_days)
Sharpe = (A_return - 0.04) / Annualised_vol
final_data = pd.DataFrame({
    'Total Return': Total_return,
    'Annualised Vol': Annualised_vol,
    'Annualised Return': A_return,
    'Max Drawdown': max_drawdown,
    'Sharpe Ratio': Sharpe
})
pd.set_option('display.max_columns', None)
print(final_data)
```

---

## Results

### Correlation Heatmap

- SP500 vs BTC: **0.99** (suspicious — likely data alignment issue)
- Nifty vs SP500: **0.44** (moderate)
- Gold vs all: **0.13-0.18** (low — good diversifier)
- ES vs Nifty: **-0.05** (slight negative)

### Max Drawdowns

- Nifty: **-49.57%** (India-Pakistan conflict 2026)
- SP500: **-18.81%**
- BTC: **-17.76%**
- Gold: **-12.21%**
- ES: **-11.76%**

### Summary Table

|Asset|Total Return|Ann. Vol|Max Drawdown|Sharpe|
|---|---|---|---|---|
|Nifty|29.9%|43%|-49.6%|0.41|
|SP500|41.8%|16.5%|-18.8%|1.61|
|Gold|104.9%|22.4%|-12.2%|3.24|
|BTC|NaN|16.7%|-17.8%|NaN|
|ES|9.1%|13.5%|-11.8%|0.19|

### Monte Carlo Hedge

- N* contracts: **1** (portfolio too small relative to ES contract size)
- Hedged std: **$209,294**
- Unhedged std: **$1,062,250**
- Hedge reduced risk by **5×**

---

## Mistakes & Lessons

> [!WARNING] Mistakes Made
> 
> - Used `idk(...)` instead of `idk[...]` — DataFrame is not callable, always use square brackets for filtering
> - Calculated `std()` on price data instead of returns — always `returns.std()` for volatility
> - Put `mean()`, `std()` inside loop — aggregate stats always go **outside** the loop
> - Used `252/252` for annualised return — should be `252/trading_days`
> - Forgot to add `futures_pnl` to `unhedged` for hedged value — hedge did nothing
> - Wrong `N_contracts` formula — must use `contract_size = price × 250`, not position size

> [!NOTE] Key Concepts Learned
> 
> - `returns.corr()` → correlation matrix for heatmap
> - `cummax()` → running peak, used for drawdown calculation
> - `ffill()` → forward fill missing values before calculating returns
> - `argsort()[:1]` → finds index of closest value (used for ATM strike)
> - `pd.to_numeric(errors='coerce')` → converts to float, turns bad values to NaN
> - `data.columns = [...]` → rename MultiIndex columns after yfinance download
> - Loop variable reuse (`for scenarios in scenarios`) → overwrites original array, use different name like `for scenario in scenarios`

> [!TIP] Build Pattern For any multi-asset analysis:
> 
> 1. Download → clean columns → calculate returns
> 2. Correlation + volatility (Section 1)
> 3. Drawdown (Section 2)
> 4. Options/external data (Section 3)
> 5. Simulation (Section 4)
> 6. Summary table (Section 5)

---

## Next Steps

- [ ] Fix BTC NaN — use `ffill()` on returns too
- [ ] Get proper SPX options chain (2-4 weeks expiry) for real vol smile
- [ ] Add VaR: `np.percentile(hedged_values, 5)`
- [ ] Apply same framework to ES ORB Strategy backtest
- [ ] Add walk-forward analysis on top of Monte Carlo

---

## Links
