---

## tags: [quant, prop-firm, monte-carlo, MES, ORB, python, simulation] date: 2026-05-11 project: Project 1 — ES ORB Strategy status: done
---
# Prop Firm Challenge Simulator — ORB Strategy

## Challenge Parameters

- **Account:** $25,000
- **Target:** +$1,500 (balance ≥ $26,500)
- **Max Drawdown:** -$1,000 (balance ≤ $24,000)
- **Time limit:** 20 trading days (1 month)
- **Contracts:** 10 MES
- **Daily limits:** Max 3 wins OR 2 losses → stop for the day

## Strategy Stats (from Pine Script backtest)

- Win rate: **41.32%**
- Avg win: $25 × 10 MES = **$250**
- Avg loss: $12.50 × 10 MES = **$125**
- RR: **1:2**

---

## Code

```python
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

win_rate    = 0.4132
win_amount  = 250
loss_amount = 125

results = []

for sim in range(1000):
    balance = 25000
    failed  = False

    for day in range(20):
        wins    = 0
        losses  = 0
        day_pnl = 0

        while wins < 3 and losses < 2:
            trade = np.random.random()
            if trade < win_rate:
                wins    += 1
                day_pnl += win_amount
            else:
                losses  += 1
                day_pnl -= loss_amount

        balance += day_pnl

        if balance >= 26500:   # target hit → stop early
            break
        if balance <= 24000:   # max drawdown hit → fail
            failed = True
            break

    results.append(balance)

results = np.array(results)
Passed = (results >= 26500).sum()
Failed = (results <= 24000).sum()

print(f"Pass Rate         : {Passed/10:.2f}%")
print(f"Fail Rate         : {Failed/10:.2f}%")
print(f"Inconclusive      : {(1000 - Passed - Failed)/10:.2f}%")
print(f"Avg Final Balance : {results.mean():.2f}")
print(f"Min Balance       : {results.min():.2f}")
print(f"Max Balance       : {results.max():.2f}")

sns.kdeplot(results, fill=True)
plt.axvline(26500, color='green', linestyle='--', label='Target')
plt.axvline(24000, color='red',   linestyle='--', label='Max Drawdown')
plt.legend()
plt.title('Prop Firm Challenge — Final Balance Distribution')
plt.xlabel('Final Balance ($)')
plt.show()
```

---

## Results

|Metric|Value|
|---|---|
|Pass Rate|66.8%|
|Fail Rate|~0%|
|Inconclusive|33.2%|
|Avg Final Balance|$26,133|
|Min Balance|$23,875|
|Max Balance|$27,125|

---

## Chart Interpretation

Two humps in the KDE distribution:

- **Left hump (~$24,000)** — failed simulations, hit max drawdown
- **Right hump (~$26,750)** — passed simulations, hit target
- Gap between = inconclusive (ran out of 20 days)

---

## Key Insights

> [!NOTE] Why Fail Rate is Near Zero Daily loss limit (max 2 losses = -$250/day) acts as a natural circuit breaker. Even in bad streaks, you can only lose $250/day → takes 4 consecutive max-loss days to hit drawdown. Very unlikely with 41% win rate.

> [!WARNING] Real World Adjustment 66.8% pass rate assumes perfect execution. Subtract 5-10% for:
> 
> - Commissions ($1-2 per MES per side)
> - Slippage (especially at NY open)
> - Emotional mistakes (cutting winners early, holding losers) **Realistic pass rate: ~58-62%**

> [!TIP] Improving Pass Rate
> 
> - Increase to 4 wins / 3 losses daily limit → more trades per day
> - Trade ES (1 contract) instead of MES (10) → same notional, lower commission ratio
> - Add session filter — only trade on days with clear trend (VIX < 20)

---

## Loop Structure

```
1000 Monte Carlo simulations
    └── 20 trading days each
            └── while loop: trades until 3 wins OR 2 losses
                    └── each trade: random() vs win_rate → win or loss
```

---

[[ES_Orb_Pinescript_v1]]