
---

## Code Breakdown

### Class Definition

```python
class ES_ORB_Strategy(QCAlgorithm):
```

- Inherits from `QCAlgorithm` — QuantConnect's base class for all strategies
- All strategy logic goes inside this class

---

### Initialize() — Setup Phase

```python
def initialize(self):
    self.set_start_date(2024, 1, 1)
    self.set_end_date(2026, 1, 1)
    self.set_cash(50000)
    self.future = self.AddFuture("ES", Resolution.Minute)
```

|Line|What It Does|
|---|---|
|`set_start_date(2024, 1, 1)`|Backtest starts Jan 1, 2024|
|`set_end_date(2026, 1, 1)`|Backtest ends Jan 1, 2026 (2 years of data)|
|`set_cash(50000)`|Starting capital = $50,000|
|`AddFuture("ES", Resolution.Minute)`|Subscribe to ES contract at 1-minute resolution|

> [!NOTE] Why Minute Resolution? ORB needs to detect the exact 6:30 PM IST candle and track intraday breakouts. Daily bars are too coarse.

---

### OnData() — Per-Bar Execution

```python
def OnData(self, data):
    for chain in data.FutureChains.Values:
        for contract in chain:
            self.Log(f"Price : {contract.LastPrice}, Time : {self.Time}")
            return
```

**What happens every minute:**

1. Loop through all available ES contract chains
2. For each contract, grab its last price
3. Log it with timestamp
4. `return` — stop processing (so we don't spam logs)

> [!WARNING] Current State This **only logs data**. No trades placed yet. Pure data inspection to confirm the feed works.

---

## Data Flow

```
QuantConnect Server
    ↓
ES Minute Data (OHLCV)
    ↓
OnData() called every minute
    ↓
Log: "Price: 5234.50, Time: 2024-01-15 20:30:00"
    ↓
Backtest Results (no trades yet)
```

---

## Next Steps

Replace `OnData()` with actual ORB logic:

```python
def OnData(self, data):
    # 1. Detect 6:30 PM IST candle (mark rectangle high/low)
    # 2. At 8:00 PM IST NY open:
    #    - Check if price above/below/inside rectangle
    #    - Set bias (long/short/wait)
    # 3. On retest of boundary → place trade
    # 4. Exit on TP (20 pts) or SL (10 pts)
    # 5. Track daily P&L — stop at 3 wins or 2 losses
```

---

## Key QuantConnect Patterns

|Pattern|What It Does|
|---|---|
|`self.Log()`|Print to cloud terminal|
|`self.Time`|Current bar timestamp|
|`contract.LastPrice`|Latest close price|
|`for chain in data.FutureChains.Values:`|Loop through all contracts|
|`self.AddFuture()`|Subscribe to a future|

---

## Syntax Notes

- Method names are **lowercase** in QuantConnect (not Python standard)
- `self.Time` is always in **UTC** — convert to IST if needed (`self.Time + timedelta(hours=5, minutes=30)`)
- `return` in loop = stop processing this bar immediately

---

## Status

✅ Data connection working ⏳ ORB logic — next ⏳ Entry/exit rules — after that ⏳ Monte Carlo + walk-forward — final

---

## Links

- [[Quant 1]] — main roadmap
- [[Opening Range Breakout Strategy]] — strategy rules
- QuantConnect docs: `QCAlgorithm` class reference