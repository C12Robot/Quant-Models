# Project 1 — Dev Log

> Internal notes. Not for CV. Updated as project evolves.

---

## What The Code Does

Downloads SPY 5-min data, marks the first 15-min candle at market open as the ORB zone (high to low), then scans every candle after 9:45 AM for breakouts above or below that zone. Each breakout fires a long or short trade with a fixed TP and SL. Results are collected, merged with VIX data to test regime filtering, and validated with Monte Carlo simulation.

---

## Key Decisions

**Why SPY instead of ES futures** yfinance doesn't provide pre-market intraday data for SPY, and ES futures require a paid data subscription. SPY regular session data is free and mirrors ES closely enough for strategy validation.

**Why pandas over a backtesting framework (Backtrader, Zipline)** Building from scratch shows the methodology clearly on a CV. Frameworks hide the logic. Also gives full control over trade execution rules.

**Why TP=$2, SL=$1** Original ES futures values (TP=20pts, SL=10pts) don't translate to SPY dollar moves. SPY typically moves $3-7 on a normal day — $20 TP was never getting hit. Scaled down to $2/$1 to keep 1:2 RR while matching SPY's actual intraday range.

**Why VIX as regime filter** High VIX = market expects big moves = breakouts follow through. Low VIX = choppy, mean-reverting = ORB fails. Standard industry logic, not curve-fitted.

**Why Alpaca over yfinance** yfinance caps 5-min intraday data at 60 days. Alpaca free tier gives 7+ years of historical 5-min data. Switched to Alpaca for proper walk-forward validation.

**Alpaca integration — how it's set up** Used `alpaca-py` SDK (not the older `alpaca-trade-api`). Only the Market Data API is needed — no trading or broker account required, just a free Alpaca account with API keys. Data is fetched via `StockHistoricalDataClient` with a `StockBarsRequest`. Timeframe syntax is `TimeFrame(5, TimeFrameUnit.Minute)` — not `TimeFrame.Minute * 5` which throws a TypeError.

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

**Why .env for API keys** Never hardcode API keys in source code — they'd get pushed to GitHub and exposed publicly. Used `python-dotenv` to load keys from a `.env` file. `.env` is listed in `.gitignore` at repo root which covers all subfolders — no need to add it per folder.

**Why VIX stays on yfinance even after switching to Alpaca** VIX is daily data, not intraday — yfinance's 60-day cap only applies to intraday (5-min etc) data. Daily data has no such limit, so VIX download via yfinance works fine for the full 2018-2026 range. No need to pull VIX from Alpaca.

---

## Libraries

|Library|Why|
|---|---|
|pandas|Core data manipulation and backtesting engine|
|yfinance|Initial data source (replaced by Alpaca)|
|alpaca-py|7+ years of free 5-min SPY historical data|
|numpy|Monte Carlo simulation, array operations|
|matplotlib|Equity curve and drawdown distribution charts|
|python-dotenv|Keeps API keys out of the codebase|

---

## Bugs & Fixes

**MultiIndex from Alpaca** Alpaca returns a MultiIndex (symbol, timestamp). Fixed with `data.reset_index(level='symbol', drop=True)`.

**Column name conflict after merge** Both `trade_data` and `orb_Zone` had `High` and `Low` columns. Merge created `High_x`/`High_y` automatically. Renamed `High_y` → `orb_high`, `Low_y` → `orb_low`. Accidentally named `orb_Zone` columns `High_y`/`Low_y` manually at one point which broke the rename — reverted to clean `High`/`Low` names.

**Timezone mismatch on VIX merge** VIX data from yfinance is timezone-naive. Used `tz_localize("America/New_York")` not `tz_convert` — because there was no existing timezone to convert from, just needed to assign one.

**`trades_per_day` date bug in short loop** Short loop was checking `trades_per_day.get(date, 0)` but `date` was still holding the last value from the long loop. Fixed by adding `date = idx.date()` at the start of the short loop.

**`for...else` misindented** The `else` block for expired trades was indented inside the inner `for` loop instead of at the same level. Caused an expired trade to be appended on every single candle that didn't hit TP/SL, inflating trade count massively.

**Empty `future_long` on last candle of day** Signal firing on the last candle of the day left no future candles to scan. `iloc[-1]` threw an IndexError on empty DataFrame. Fixed with `if future_long.empty: continue`.

**Signals = 0 after switching to Alpaca** After replacing yfinance with Alpaca, long and short trade counts both came back 0. Root cause — `orb_Zone` DataFrame columns were manually named `High_y`/`Low_y` instead of clean `High`/`Low`. The merge then couldn't create `High_x`/`High_y` properly, so the rename to `orb_high`/`orb_low` failed silently. Signal lines threw `KeyError: 'orb_high'`. Fixed by reverting `orb_Zone` column names to `High` and `Low` and letting the merge handle the `_x`/`_y` suffix automatically.

**Indentation bug in `ORB_backtest` (repeat of earlier mistake)** Same root cause as the original `for...else` bug — all logic after the `trades_per_day` daily-limit check (`is_long`, `entry_price`, `tp`, `sl`, `future`, `tp_hit`, `sl_hit`, the final `results.append`) was nested one level too deep, sitting inside the `if trades_per_day.get(date, 0) >= 3: continue` block instead of after it. This meant most of the function body never ran. Fixed by de-indenting everything to align with the `if` check, not inside it.

**`return results` indented inside the `for` loop** `return` was placed inside the `for idx, row in signals.iterrows()` loop instead of at the function level after it. This caused the function to return after processing only the first signal of the day instead of all signals. Fixed by moving `return results` to align with the `for` loop, not nested inside it.

**`.append()` instead of `.extend()` when collecting daily results** Used `all_results.append(day_results)` where `day_results` is itself a list — this created a list of lists (`[[...], [...], ...]`) instead of one flat list of trade dicts. `pd.DataFrame()` couldn't parse the nested structure, raising `TypeError: object of type 'NoneType' has no len()`. Fixed with `all_results.extend(day_results)`, which unpacks each day's list into the parent list individually.

**`future['High']` / `future['Low']` KeyError (repeat)** Same column-naming issue as before — `future` is sliced from the merged `trade_data`, so the candle's own High/Low are `High_x`/`Low_x`, not `High`/`Low`. Hit again when writing the vectorized `tp_hit`/`sl_hit` lines. Fixed by using `High_x`/`Low_x`.

**`trades_df['date']` computed from `all_results` instead of `trades_df`** After building `trades_df = pd.DataFrame(all_results)`, the next line mistakenly called `.dt.date` on `all_results` (still a plain list) instead of on `trades_df['entry_time']`. Raised `TypeError: list indices must be integers or slices, not str`. Fixed by referencing `trades_df['entry_time']`.

**Sharpe identical for in-sample and out-sample (recurring)** The walk-forward print loop calculates `sharpe_forward` correctly per period but the print statement referenced the old global `sharpe` variable instead, so both periods displayed the same number. Fixed by printing `sharpe_forward`. After the fix: in-sample Sharpe 1.40, out-sample Sharpe 3.55 — genuinely different and far more informative.

**Cutoff date needs rescaling with new data range** The in/out-of-sample cutoff (`2026-05-09`) was set for the old 60-day window. After switching to 8 years of Alpaca data (2018–2026), this cutoff no longer reflected an 80/20 split. Updated to `2024-06-01` to give ~6.5 years in-sample / ~1.5 years out-of-sample.

---

## Performance Issues

**`iterrows()` is slow on large datasets** On 60 days (~140 trades) it was fine. On 8 years (~4000+ signals) it's too slow — nested loops scanning forward through thousands of candles per signal. Original 60-day approach took 16 minutes on 8 years of data and still failed.

**Fix implemented: day-by-day grouping + vectorized hit detection**

Replaced the two separate long/short `iterrows()` loops (which scanned every future candle one at a time per signal) with a single `ORB_backtest()` function called once per trading day via `trade_data.groupby('date')`. This cuts the outer loop from "every signal" (~4900) down to "every trading day" (~2000), and replaces the inner candle-by-candle scan with vectorized boolean operations.

Inside `ORB_backtest`, for each signal still uses `iterrows()` but only over that day's 2-3 signals max, not the whole future window. The actual TP/SL search is vectorized:

```python
tp_hit = future['High_x'] >= tp if is_long else future['Low_x'] <= tp
sl_hit = future['Low_x'] <= sl if is_long else future['High_x'] >= sl
hit = tp_hit | sl_hit

if not hit.any():
    # neither hit - expired trade, exit at last close
    last_price = future['Close'].iloc[-1]
else:
    first_hit_idx = hit.idxmax()  # first True in a boolean series = first hit
    if tp_hit.loc[first_hit_idx]:
        result = 'win'
    else:
        result = 'loss'
```

Key trick: `idxmax()` on a boolean Series returns the index of the first `True` value (since `True == 1` is the max). This replaces the inner candle-by-candle loop entirely — pandas finds the first hit in one vectorized operation instead of Python iterating row by row.

Long and short are now handled by one unified function instead of two duplicated loops, using a ternary (`x if is_long else y`) to branch direction-specific logic (TP/SL sign, which column to check).

**Result:** full 8-year run (2018-2026, ~4900 signals) completes in a reasonable time instead of timing out / taking 16+ minutes.

---

## Results After Vectorization (8-Year Dataset, 2018-2026)

|Metric|Full Period|In-Sample (2018-2024)|Out-Sample (2024-2026)|
|---|---|---|---|
|Trades|4927|3967|960|
|Win Rate|—|23.4%|33.9%|
|Total PnL|~$1300|$794.52|$524.71|
|Sharpe|—|1.40|3.55|

Monte Carlo (1000 sims): median drawdown -$70, worst 5% -$104, actual drawdown -$102 (near worst-case but still net profitable).

Notably — out-of-sample outperformed in-sample on every metric. Opposite of the 60-day test, where out-of-sample failed. Strong signal the edge is real, not an artifact of the original small sample.

---

## Things To Revisit

- VIX filter re-test with proper high-volatility periods (VIX 30+ now available in 8-year dataset — 2020 crash, 2022 bear market)
- Walk-forward analysis with rolling windows (currently just one static in/out split)
- Add slippage and commission estimate to PnL
- Test on ES futures data when paid data access available
- Investigate why win rate is lower (23-34%) despite strong Sharpe/PnL — likely large win/loss asymmetry doing the work, worth checking distribution of wins vs losses beyond just averages