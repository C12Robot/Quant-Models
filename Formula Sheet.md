# Quant Formula Reference Sheet

**Last updated: May 2026**

---

## 1. Returns

```python
returns = data.pct_change().dropna()
log_returns = np.log(data / data.shift(1)).dropna()
cumulative = (1 + returns).cumprod()
total_return = (data.iloc[-1] / data.iloc[0]) - 1
trading_days = len(returns)
annualised_return = total_return * (252 / trading_days)
```

---

## 2. Volatility

```python
daily_vol = returns.std()
annualised_vol = returns.std() * np.sqrt(252)
rolling_vol = returns.rolling(30).std() * np.sqrt(252)
```

> 252 = trading days in a year. Always annualise by multiplying daily std by √252.

---

## 3. Sharpe Ratio

```python
risk_free_daily = 0.065 / 252
excess_return = returns - risk_free_daily
rolling_sharpe = excess_return.rolling(20).mean() / excess_return.rolling(20).std() * np.sqrt(252)
sharpe = (annualised_return - 0.065) / annualised_vol
```

> Sharpe > 1 = good. Sharpe > 2 = very good. Sharpe < 0 = worse than risk-free.

---

## 4. Drawdown

```python
cumulative = (1 + returns).cumprod()
drawdown = (cumulative - cumulative.cummax()) / cumulative.cummax()
max_drawdown = drawdown.min()
max_drawdown_date = drawdown.idxmin()
```

> Always calculate drawdown on cumulative returns, not raw returns.

---

## 5. Rolling Correlation

```python
# Static — for heatmap
corr_matrix = returns.corr()
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm')

# Rolling — for line plot
rolling_corr = returns['Asset1'].rolling(30).corr(returns['Asset2'])
plt.plot(rolling_corr)
```

> Static corr → heatmap. Rolling corr → line plot.

---

## 6. Win Rate & Risk/Reward

```python
wins   = [r for r in trade_returns if r > 0]
losses = [r for r in trade_returns if r <= 0]

win_rate = len(wins) / len(trade_returns) * 100
avg_win  = np.mean(wins) * 100
avg_loss = np.mean(losses) * 100
RR       = avg_win / abs(avg_loss)

# Expectancy — positive = profitable strategy
expectancy = (win_rate/100 * avg_win) + ((1 - win_rate/100) * avg_loss)
```

---

## 7. Hedge Calculations

```python
# Minimum Variance Hedge Ratio
h = correlation * (std_spot / std_futures)

# Optimal contracts (tailed hedge)
N = round(h * (V_A / V_F))
# V_A = position_size × spot_price
# V_F = contract_size × futures_price

# Equity portfolio hedge
N = round(beta * (portfolio / (futures_price * contract_multiplier)))

# Change beta from β to β*
contracts_short = round((beta - beta_target) * (portfolio / V_F))
contracts_long  = round((beta_target - beta) * (portfolio / V_F))

# Hedge effectiveness
effectiveness = correlation ** 2
```

---

## 8. Monte Carlo

```python
scenarios = np.random.normal(loc=spot_price, scale=spot_price * vol, size=1000)

# Stats always OUTSIDE the loop
hedged_values = np.array(hedged_list)
mean  = hedged_values.mean()
std   = hedged_values.std()
VaR95 = np.percentile(hedged_values, 5)
wins  = (hedged_values > unhedged_values).sum()
win_rate = wins / 1000 * 100
```

---

## 9. Seasonality

```python
avg_monthly = returns.groupby(returns.index.month).mean()
import calendar
avg_monthly.index = [calendar.month_abbr[m] for m in avg_monthly.index]
avg_monthly.plot(kind='bar', figsize=(12,5))
```

---

## 10. Summary Table Template

```python
total_return   = (data.ffill().iloc[-1] / data.ffill().iloc[0]) - 1
annualised_vol = returns.std() * np.sqrt(252)
trading_days   = len(returns)
annualised_ret = total_return * (252 / trading_days)
sharpe         = (annualised_ret - 0.065) / annualised_vol
max_dd         = drawdown.min()

summary = pd.DataFrame({
    'Total Return'     : total_return,
    'Annualised Vol'   : annualised_vol,
    'Annualised Return': annualised_ret,
    'Sharpe Ratio'     : sharpe,
    'Max Drawdown'     : max_dd
})
pd.set_option('display.max_columns', None)
print(summary)
```

---

## 11. Signal & Backtest

```python
data['Signal'] = 0
data.loc[MA20 > MA50, 'Signal'] = 1
crossovers = data[data['Signal'].diff() == 1]

# Always shift(1) — can't act on today's signal until tomorrow
data['Strategy_Return'] = data['Signal'].shift(1) * data['Return']
data['Equity_Curve']    = (1 + data['Strategy_Return']).cumprod()
```

---

## 12. Trading Days Reference

|Period|Trading Days|
|---|---|
|1 week|5|
|1 month|21|
|1 quarter|63|
|1 year|252|

---

## 13. Common Conversions

```python
daily_rate  = annual_rate / 252         # annual → daily
annual_vol  = daily_vol * np.sqrt(252)  # daily vol → annual

# IST → UTC
# 6:30 PM IST = 13:00 UTC  (rectangle candle)
# 8:00 PM IST = 14:30 UTC  (NY open)
```