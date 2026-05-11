---

## tags: [pine-script, ORB, ES, MES, strategy, project-1, tradingview] date: 2026-05-11 project: Project 1 — ES ORB Strategy status: working — needs refinement
---
# ES ORB Strategy — Pine Script v1

## Strategy Rules

- **Rectangle:** Mark high/low of 12:00 UTC candle (6:30 PM IST during DST)
- **NY Open:** 13:30 UTC (7:00 PM IST during DST)
- **Long entry:** NY open bar closes 5+ points above rectHigh
- **Short entry:** NY open bar closes 5+ points below rectLow
- **SL:** 10 points | **TP:** 20 points (1:2 RR)
- **Backtest from:** January 1, 2024

---

## Code

```pine
//@version=6
strategy("ES ORB strategy", overlay=true, default_qty_type=strategy.fixed, default_qty_value=1)

var float rectHigh = na
var float rectLow  = na

// Mark rectangle at 12:00 UTC (6:30 PM IST during DST)
isRectBar = hour(time, "UTC") == 12 and minute(time) == 0

if isRectBar
    rectHigh := high
    rectLow  := low

plot(rectHigh, color=color.green, linewidth=2, title="Rect High")
plot(rectLow,  color=color.red,   linewidth=2, title="Rect Low")

// NY open at 13:30 UTC (7:00 PM IST during DST)
isNYOpen = hour(time, "UTC") == 13 and minute(time) == 30
bgcolor(isNYOpen ? color.new(color.yellow, 80) : na)

// Date filter
startDate  = timestamp("2024-01-01")
inDateRange = time >= startDate

// Entry conditions — 5 point breakout filter
isLong  = isNYOpen and close > rectHigh + 5 and not na(rectHigh)
isShort = isNYOpen and close < rectLow  - 5 and not na(rectLow)

// Orders
if isLong and strategy.position_size == 0
    strategy.entry("Long",  strategy.long)
    strategy.exit("Exit Long",  "Long",  loss=10, profit=20)

if isShort and strategy.position_size == 0
    strategy.entry("Short", strategy.short)
    strategy.exit("Exit Short", "Short", loss=10, profit=20)

// Signal markers
plotshape(isLong,  style=shape.triangleup,   location=location.belowbar, color=color.green, size=size.normal, title="Long Signal")
plotshape(isShort, style=shape.triangledown, location=location.abovebar, color=color.red,   size=size.normal, title="Short Signal")
```

---

## Backtest Results (MES, 15-min, 2024-2026)

|Metric|Value|
|---|---|
|Total Trades|167|
|Win Rate|41.32%|
|Profit Factor|1.408|
|Avg Win|$25.00|
|Avg Loss|$12.50|
|Total P&L|+$500|
|Max Drawdown|$100|
|Longs Win Rate|45.98%|
|Shorts Win Rate|36.25%|

---

## DST Note

|Period|NY Open IST|NY Open UTC|
|---|---|---|
|Mar–Nov (DST)|7:00 PM IST|13:30 UTC|
|Nov–Mar (Standard)|8:00 PM IST|14:30 UTC|

> Always use UTC in code — adjust for DST manually when switching seasons.

---

## Key Observations

- 41% win rate > 33% break-even threshold for 1:2 RR ✅
- Longs outperform shorts — NY morning bias is bullish
- 5-point filter reduces false breakouts significantly
- Sharpe ratio from TradingView is unreliable — calculate in pandas

---

