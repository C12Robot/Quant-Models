---

## tags: [quant, bayesian, beta-distribution, win-rate, scipy, python, pandas] date: 2026-05-11 project: Quant 1 status: done
---
# Bayesian Win Rate Analysis — Trading Strategy

## Question

Strategy has 14 wins, 6 losses after 20 trades. Use Bayesian updating to estimate true win rate and show how confidence grows with more data.

---

## Code

```python
from scipy.stats import beta
import numpy as np
import matplotlib.pyplot as plt

# Beta(a, b) where a = wins+1, b = losses+1
prior          = beta(1, 1)       # uniform — no data
posterior_20   = beta(15, 7)      # 14W 6L
posterior_100  = beta(71, 31)     # 70W 30L
posterior_1000 = beta(701, 301)   # 700W 300L

x = np.linspace(0, 1, 1000)

# Stats
mean              = posterior_20.mean()
ci_low, ci_high   = posterior_20.interval(0.95)
p_above_60        = 1 - posterior_20.cdf(0.60)

# Plot
plt.plot(x, prior.pdf(x),          label='Prior (no data)')
plt.plot(x, posterior_20.pdf(x),   label='After 20 trades')
plt.plot(x, posterior_100.pdf(x),  label='After 100 trades')
plt.plot(x, posterior_1000.pdf(x), label='After 1000 trades')
plt.xlabel('Win Rate')
plt.ylabel('Probability Density')
plt.legend()
plt.show()
```

---

## Results

|Trades|Mean Win Rate|95% CI|CI Width|P(>60%)|
|---|---|---|---|---|
|20|68%|48% → 85%|37%|80%|
|100|~70%|~61% → ~78%|~17%|~98%|
|1000|70%|67% → 73%|6%|100%|

---

## Key Concepts

**Beta Distribution:**

```
Beta(a, b) where a = wins + 1, b = losses + 1
Mean = a / (a + b)
```

**Key methods:**

```python
posterior.mean()           # expected win rate
posterior.interval(0.95)   # 95% credible interval
posterior.cdf(0.60)        # P(win rate ≤ 60%)
posterior.pdf(x)           # probability density at x (for plotting)
```

---

## Key Insights

> [!WARNING] Small Sample Danger After 20 trades, CI spans 48%-85% — 37% wide. You cannot distinguish a 50% win rate strategy from an 85% win rate strategy. Never trust backtest metrics on fewer than 100 trades.

> [!TIP] How Many Trades Do You Need?
> 
> - 20 trades → basically useless statistically
> - 100 trades → reasonable estimate (±17%)
> - 1000 trades → high confidence (±3%) Rule of thumb: 200+ trades minimum before trusting any strategy metric.

> [!NOTE] Prior Choice Uniform prior Beta(1,1) = "I have no idea about win rate." If you have domain knowledge (e.g. most strategies have 40-60% win rate) you can use an informative prior like Beta(5,5) which peaks at 50%.

---
