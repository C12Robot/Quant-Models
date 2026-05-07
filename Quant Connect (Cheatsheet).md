# QuantConnect Cheatsheet

**Last updated: May 2026**

---

## Setup & Boilerplate

```python
from AlgorithmImports import *

class MyStrategy(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2024, 1, 1)
        self.SetEndDate(2026, 1, 1)
        self.SetCash(50000)
        self.spy = self.AddEquity("SPY", Resolution.Minute)
        self.qqq = self.AddEquity("QQQ", Resolution.Minute)
        self.tlt = self.add_equity("TLT", Resolution.Minute)
        self.SetWarmup(100)  # always add warmup before OnData

    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return  # safety net — don't trade during warmup
```

> **Method names:** QuantConnect uses PascalCase (`Initialize`, `OnData`). Some newer API methods use snake_case (`set_holdings`, `add_equity`). Both work — just be consistent within a project.

---

## Adding Assets & Indicators

```python
# Equities
self.spy = self.AddEquity("SPY", Resolution.Minute)
self.qqq = self.AddEquity("QQQ", Resolution.Minute)

# Futures
self.es = self.AddFuture(Futures.Indices.SP500EMini, Resolution.Minute)

# Indicators — attach to asset symbol
self.sma30 = self.SMA(self.spy.Symbol, 30)   # 30-day Simple Moving Average
self.rsi15 = self.RSI(self.spy.Symbol, 15)   # 15-period RSI
```

> Indicators must be declared in `Initialize()`, not `OnData()`.

---

## Placing Orders

```python
# Buy N shares
self.MarketOrder(self.spy.Symbol, 1)         # buy 1 share
self.MarketOrder(self.spy.Symbol, -1)        # sell/short 1 share

# Allocate % of portfolio
self.set_holdings(self.spy.Symbol, 0.33)     # 33% of portfolio
self.set_holdings(self.spy.Symbol, 1)        # 100% of portfolio

# Sell everything
self.Liquidate()                             # liquidate all positions
self.liquidate(self.spy.Symbol)              # liquidate specific asset
```

---

## Entry & Exit Logic

```python
def OnData(self, data: Slice):
    if self.IsWarmingUp:
        return

    # Entry — price above MA
    if not self.Portfolio.Invested:
        if self.spy.Price > self.sma30.Current.Value:
            self.MarketOrder(self.spy.Symbol, 1)
            self.Debug(f"Buy: Price {self.spy.Price} > MA {self.sma30.Current.Value}")

    # Exit — price below MA
    if self.Portfolio.Invested:
        if self.spy.Price < self.sma30.Current.Value:
            self.Liquidate()
            self.Debug(f"Sell: Price {self.spy.Price} < MA {self.sma30.Current.Value}")
```

> **Why check `Portfolio.Invested` before liquidating?** Waste of resources to liquidate when you have nothing. Also prevents errors.

---

## Stop Loss & Take Profit

```python
if self.Portfolio.Invested:
    avg_price = self.Portfolio[self.spy.Symbol].AveragePrice

    # Stop Loss — exit if down 10%
    if self.spy.Price < avg_price * 0.90:
        self.Liquidate()
        self.Debug("Stop Loss triggered")

    # Take Profit — exit if up 30%
    if self.spy.Price > avg_price * 1.30:
        self.Liquidate()
        self.Debug("Take Profit triggered")
```

**Alternative — built-in StopMarketOrder:**

```python
self.StopMarketOrder(self.spy.Symbol, -1, self.spy.Price * 0.90)
# quantity = -1 (sell), price = 90% of current price
```

> Manual comparison (method 1) is more flexible — you can add custom logic. Built-in StopMarketOrder is simpler but less controllable.

---

## Plotting

```python
# plot indicator alongside price
self.Plot("SPY Chart", "MA30", self.sma30.Current.Value)
self.Plot("SPY Chart", "Price", self.spy.Price)
```

> Both series must share the same chart name ("SPY Chart") to appear on the same chart.

---

## Logging Orders

```python
def OnOrderEvent(self, orderEvent):
    order = self.Transactions.GetOrderById(orderEvent.OrderId)
    self.Log(f"{self.Time}: {order.Type}: {orderEvent}")
```

|Part|What It Does|
|---|---|
|`OnOrderEvent`|Fires automatically on every order status change|
|`orderEvent`|Contains fill price, status (filled/cancelled), quantity|
|`GetOrderById`|Fetches full order details by ID|
|`order.Type`|Market, Limit, Stop, etc.|

---

## Custom Bar (Consolidator)

```python
def Initialize(self):
    ...
    self.sma30 = None  # declare as None first
    self.LastTradeTime = None
    self.currentbar = None
    self.Consolidate(self.spy.Symbol, timedelta(minutes=30), self.OnDataConsolidated)

def OnDataConsolidated(self, bar):
    self.currentbar = bar
    self.Plot("30 min Chart", "Close", self.currentbar.Close)

    # create MA if not exists, else update it
    if self.sma30 is None:
        self.sma30 = self.SMA(self.spy.Symbol, 30)
    else:
        self.sma30.Update(bar.EndTime, bar.Close)

    if self.sma30.IsReady:
        ma_value = self.sma30.Current.Value
        close = self.currentbar.Close

        # prevent trading more than once per bar
        if self.LastTradeTime is not None:
            if bar.EndTime - self.LastTradeTime < timedelta(minutes=30):
                return

        if close > ma_value:
            self.set_holdings(self.spy.Symbol, 1)
            self.Debug("Buy Signal")
            self.LastTradeTime = bar.EndTime

        if close < ma_value:
            self.liquidate(self.spy.Symbol)
            self.Debug("Sell Signal")
            self.LastTradeTime = bar.EndTime
```

> **Why `timedelta(minutes=30)` guard?** Custom bar fires every 30 mins. Without the guard, a single bar could trigger multiple trades if conditions stay true across ticks.

---

## Warmup

```python
self.SetWarmup(100)  # in Initialize() — look at 100 bars before trading

def OnData(self, data: Slice):
    if self.IsWarmingUp:
        return  # skip all logic during warmup
```

> Always warmup by at least the longest indicator period. If SMA30, warmup at least 30 bars.

---

## Logging vs Debug

|Method|Where It Shows|
|---|---|
|`self.Log(...)`|Logs tab in backtest results|
|`self.Debug(...)`|Cloud Terminal (real-time during backtest)|

> Use `self.Debug()` while building — you see output immediately. Switch to `self.Log()` for final results.

---

## Key Patterns Reference

|Pattern|Code|
|---|---|
|Current indicator value|`self.sma30.Current.Value`|
|Check if indicator ready|`self.sma30.IsReady`|
|Current bar time|`self.Time` (always UTC)|
|Asset price|`self.spy.Price`|
|Portfolio invested|`self.Portfolio.Invested`|
|Average buy price|`self.Portfolio[self.spy.Symbol].AveragePrice`|
|Number of shares held|`self.Portfolio[self.spy.Symbol].Quantity`|

---

## Common Mistakes

|Mistake|Fix|
|---|---|
|`def initialize` lowercase|`def Initialize` — QuantConnect needs exact name|
|`def on_data`|`def OnData` — same|
|Indicator in `OnData()`|Declare indicators in `Initialize()` only|
|No warmup|Always add `self.SetWarmup(N)`|
|No `IsWarmingUp` check|Add `if self.IsWarmingUp: return` at top of `OnData`|
|`self.Log()` not showing|Check Logs tab, not Cloud Terminal — use `self.Debug()` instead|
|`FutureChains` empty|Add `SetFilter()` to futures subscription|