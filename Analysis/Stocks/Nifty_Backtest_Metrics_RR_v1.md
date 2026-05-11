# Backtesting Metrics — MA Crossover Strategy

**Date:** April 2026  
**Extends:** Real Data Analysis Session 1

---

## New Metrics Added

```python
# max drawdown — largest peak to trough decline
rolling_max = nifty['Buy_Hold'].cummax()
drawdown = (nifty['Buy_Hold'] - rolling_max) / rolling_max
max_drawdown_bh = drawdown.min()

rolling_max_s = nifty['Strategy'].cummax()
drawdown_s = (nifty['Strategy'] - rolling_max_s) / rolling_max_s
max_drawdown_s = drawdown_s.min()

# Sharpe ratio of strategy itself
strategy_sharpe = (nifty['Strategy_Return'].mean() / nifty['Strategy_Return'].std()) * (252**0.5)

print(f"Max Drawdown Buy&Hold: {max_drawdown_bh*100:.2f}%")
print(f"Max Drawdown Strategy: {max_drawdown_s*100:.2f}%")
print(f"Strategy Sharpe: {strategy_sharpe:.2f}")


```

---

## Results (1 year, MA 20/50)

|Metric|Buy & Hold|MA Strategy|
|---|---|---|
|Return|-0.97%|-3.26%|
|Max Drawdown|-15.18%|-5.87%|
|Sharpe|negative|-0.62|

---

## The Key Insight

Strategy lost more in total return but had much smaller drawdown — only 5.87% vs 15.18%.

Why? The strategy exited the market before the April 2026 tariff crash and avoided the worst drawdown. It traded better downside protection for worse overall returns.

**Returns alone don't tell the full story.** A strategy with lower returns but significantly lower drawdown might be preferable for risk-averse investors or institutions that cannot tolerate large drawdowns.

This is why quants use multiple metrics — not just returns.

---

## How Max Drawdown Works

```python
rolling_max = equity_curve.cummax()   # track the peak at each point
drawdown = (equity_curve - rolling_max) / rolling_max  # % below peak
max_drawdown = drawdown.min()   # worst point = most negative value
```

cummax() tracks the highest point reached so far. Drawdown measures how far below that peak you currently are. The minimum of that series = max drawdown.

---

## The Lesson

> _Three metrics every backtest must report: return, max drawdown, Sharpe ratio. Return tells you how much you made. Max drawdown tells you how much pain you had to endure. Sharpe tells you if the return was worth the risk. A strategy with great returns but 50% drawdown is unusable for most investors — they'd panic sell at the bottom._

