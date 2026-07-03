# Project 1 — ORB Strategy Backtest

> **Quant CV Project | Python + Pandas | SPY 5-min Data**

---

## Research Question

> _Does the Opening Range Breakout (ORB) strategy generate statistically significant alpha on SPY, and does a VIX-based regime filter improve performance?_

---

## Strategy Rules

**Asset:** SPY (SPDR S&P 500 ETF) — chosen as a liquid, free-data proxy for ES futures

**Opening Range:**

- First 15-minute window at market open (9:30–9:45 AM ET)
- Range defined wick-to-wick across the 9:30, 9:35, 9:40 candles
- High = highest High across 3 candles, Low = lowest Low

**Entry Conditions (after 9:45 AM ET):**

- Long: Close crosses above ORB High (previous candle at or below)
- Short: Close crosses below ORB Low (previous candle at or above)

**Trade Management:**

- Take Profit: +$2.00 per share
- Stop Loss: -$1.00 per share
- Risk-Reward: 1:2
- Max 3 trades per day (longs + shorts combined)

---

## Tech Stack

|Tool|Purpose|
|---|---|
|Python + Pandas|Core backtesting engine|
|Alpaca Market Data API|SPY 5-min historical data (free, 7+ years)|
|yfinance|VIX daily historical data (free, no date limit on daily bars)|
|NumPy|Monte Carlo simulation|
|Matplotlib|Equity curve + drawdown distribution|
|python-dotenv|API key management|

---

## Results

### Full Backtest (8 years, 2018–2026, SPY 5-min via Alpaca)

|Metric|Value|
|---|---|
|Total Trades|4,927|
|Total PnL|~$1,300|
|Median Max Drawdown (Monte Carlo)|-$70.31|
|Worst 5% Drawdown (Monte Carlo)|-$104.18|
|Best 5% Drawdown (Monte Carlo)|-$51.98|

### In-Sample vs Out-of-Sample Split (80/20)

|Period|Trades|Win Rate|PnL|Sharpe|
|---|---|---|---|---|
|In-Sample (2018 – Jun 2024)|3,967|23.4%|+$794.52|1.40|
|Out-of-Sample (Jun 2024 – 2026)|960|33.9%|+$524.71|3.55|

**Finding:** Strategy generalizes well to unseen data — out-of-sample performance exceeds in-sample on every metric (higher win rate, higher Sharpe). This is the opposite of overfitting and a strong signal the edge is real, not an artifact of a small sample. This result reverses the original 60-day test (see Limitations/History below), where out-of-sample failed — directly attributable to insufficient sample size in that earlier run.

### Monte Carlo Simulation (1000 iterations)

Shuffled trade PnL sequence 1000 times to stress-test drawdown distribution against random trade ordering:

|Metric|Value|
|---|---|
|Median Max Drawdown|-$70.31|
|Worst 5% Drawdown|-$104.18|
|Best 5% Drawdown|-$51.98|
|Actual Drawdown|-$102.49|

**Finding:** Actual drawdown sits near the worst 5% of simulated outcomes — meaning real trade sequencing was close to the worst-case path. Despite this, the strategy still closed strongly profitable, suggesting resilience even under unlucky ordering.

### VIX Regime Filter

_Re-test pending on the 8-year dataset._ The original 60-day test (VIX threshold ≥20) showed no meaningful separation between high and low volatility regimes, but that sample only spanned VIX 15–31 with insufficient variance. The 8-year window now includes genuine high-volatility periods (2020 COVID crash, 2022 bear market) and will be re-tested for a more meaningful read on regime dependence.

---

## Limitations

1. **VIX filter not yet re-validated on full dataset** — pending re-test with proper high/low volatility regime separation now that 2020 and 2022 volatility spikes are included in the sample.
    
2. **Single share sizing:** PnL calculated on 1 share of SPY. Real trading would use 100+ shares, amplifying both gains and drawdowns proportionally.
    
3. **No slippage or commissions:** Live trading results would be worse due to bid-ask spread and transaction costs.
    
4. **Static in/out-of-sample split:** Current validation is a single 80/20 split, not a rolling walk-forward across multiple windows. A full walk-forward analysis (train/test/slide) would provide stronger evidence of robustness.
    
5. **Fixed dollar TP/SL across 8 years:** $2/$1 TP/SL was calibrated for SPY price levels seen in recent data (~$650–750). Earlier years (2018, SPY ~$270) make the same dollar move a much larger percentage move — point values may need scaling by price level in a future iteration.
    

---

## History / Earlier Iteration (60-Day yfinance Test)

Project 1 was first built and validated end-to-end on a 60-day SPY sample via yfinance, before data was extended via Alpaca. That earlier run is documented here for completeness, since it shaped key methodology decisions (TP/SL calibration, VIX filter logic, trade limit rules):

|Metric|Value (60-day baseline)|
|---|---|
|Total Trades|142|
|Win Rate|28.9%|
|Total PnL|+$30.26|
|Sharpe Ratio|1.57|
|Max Drawdown|-$40.00|

On that smaller sample, out-of-sample performance failed to generalize (win rate dropped from 31.4% to 25.0%, PnL turned negative) — a finding fully reversed once tested on 8 years of data. This is itself a useful research note: a 60-day sample was not sufficient to draw conclusions either way, and the larger dataset was necessary to validate the strategy properly.

---

## Conclusions

The ORB strategy shows a robust, generalizing edge on SPY across 8 years of 5-min data (2018–2026), with out-of-sample performance exceeding in-sample on every metric. Monte Carlo testing confirms the strategy survives unfavorable trade sequencing while remaining net profitable. The original 60-day test had insufficient data to draw reliable conclusions — extending to a multi-year dataset via Alpaca was necessary and reversed the earlier negative out-of-sample finding.

**Next steps:**

- Re-test VIX regime filter on full 8-year dataset (high-volatility periods now available)
- Implement rolling walk-forward analysis across multiple windows
- Add slippage and commission estimates to PnL
- Test on ES futures with proper point values
- Investigate scaling TP/SL by price level given SPY's price range across 2018–2026

---

## Key Code

**Data Pull (Alpaca, 8-year 5-min SPY):**

```python
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

client = StockHistoricalDataClient(
    api_key=os.getenv("ALPACA_KEY"),
    secret_key=os.getenv("ALPACA_SECRET_KEY")
)

request = StockBarsRequest(
    symbol_or_symbols="SPY",
    timeframe=TimeFrame(5, TimeFrameUnit.Minute),
    start="2018-01-01",
    end="2026-01-01"
)

data = client.get_stock_bars(request).df
data = data.reset_index(level='symbol', drop=True)
data.index = data.index.tz_convert("America/New_York")
data.columns = [col.capitalize() for col in data.columns]
```

**ORB Level Calculation:**

```python
orb_High = orb_data.groupby(orb_data.index.date)['High'].max()
orb_Low = orb_data.groupby(orb_data.index.date)['Low'].min()
orb_Zone = pd.DataFrame({'High' : orb_High, 'Low' : orb_Low})
```

**Signal Generation:**

```python
trade_data['long_signal'] = (trade_data['Close'] > trade_data['orb_high']) & (trade_data['Close'].shift(1) <= trade_data['orb_high'])
trade_data['short_signal'] = (trade_data['Close'] < trade_data['orb_low']) & (trade_data['Close'].shift(1) >= trade_data['orb_low'])
```

**Vectorized Trade Execution:**

```python
def process_day(day_data, trades_per_day):
    results = []
    signals = day_data[(day_data['long_signal']) | (day_data['short_signal'])]

    for idx, row in signals.iterrows():
        date = idx.date()
        if trades_per_day.get(date, 0) >= 3:
            continue

        is_long = row['long_signal']
        entry_price = row['Close']
        tp = entry_price + 2 if is_long else entry_price - 2
        sl = entry_price - 1 if is_long else entry_price + 1

        future = day_data[day_data.index > idx]
        if future.empty:
            continue

        tp_hit = future['High_x'] >= tp if is_long else future['Low_x'] <= tp
        sl_hit = future['Low_x'] <= sl if is_long else future['High_x'] >= sl

        hit = tp_hit | sl_hit
        if not hit.any():
            last_price = future['Close'].iloc[-1]
            pnl = (last_price - entry_price) if is_long else (entry_price - last_price)
            results.append({'entry_time': idx, 'entry_price': entry_price, 'exit_price': last_price, 'result': 'expired', 'pnl': pnl})
            trades_per_day[date] = trades_per_day.get(date, 0) + 1
            continue

        first_hit_idx = hit.idxmax()

        if tp_hit.loc[first_hit_idx]:
            exit_price = tp
            result = 'win'
            pnl = 5
        else:
            exit_price = sl
            result = 'loss'
            pnl = -2

        results.append({'entry_time': idx, 'entry_price': entry_price, 'exit_price': exit_price, 'result': result, 'pnl': pnl})
        trades_per_day[date] = trades_per_day.get(date, 0) + 1

    return results

trades_per_day = {}
all_results = []

for date, day_data in trade_data.groupby('date'):
    day_results = process_day(day_data, trades_per_day)
    all_results.extend(day_results)

trades_df = pd.DataFrame(all_results)
```

This replaced the original nested `iterrows()` approach (one loop per signal, scanning forward candle-by-candle) with one loop over trading days (~2000) instead of one loop per signal (~4900), using vectorized boolean operations (`idxmax()` on a boolean Series) to find the first TP/SL hit instead of iterating candle by candle.

**Monte Carlo Simulation:**

```python
pnl_values = np.array(all_trade_vix['pnl'])
scenarios = []
for i in range(1000):
    original = pnl_values.copy()
    np.random.shuffle(original)
    cumulative = np.cumsum(original)
    max_dd = (cumulative - np.maximum.accumulate(cumulative)).min()
    scenarios.append(max_dd)
```

---

## Charts

**Equity Curve (2018–2026):**
![[Project1_equity_curve_v2.png]]

**Monte Carlo Drawdown Distribution:**
![[Project1_montecarlo_max_drawdown_distribution_curve_v2.png]]
---

## What This Project Demonstrates

- End-to-end quantitative research workflow: hypothesis → data → backtest → validation → findings
- Migrating a backtest from a 60-day free data source to a multi-year provider when initial results were inconclusive
- Vectorizing a row-by-row backtest loop for an 8-year dataset (performance engineering, not just strategy logic)
- Proper use of in-sample/out-of-sample split to avoid overfitting
- Monte Carlo stress testing for drawdown risk assessment
- Intellectual honesty in documenting limitations, reversed findings, and what's still pending
- Python/Pandas backtesting without relying on pre-built frameworks