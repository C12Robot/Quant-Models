---

## tags: [quant, hull, chapter-3, chapter-4, compounding, hedge, bayesian, monte-carlo, python] date: 2026-05-11 project: Quant 1 status: done
---
# Combined Exercise — Compounding + Hedge + Bayesian

## Setup

- Portfolio: **$5,000,000**, β = **1.4**
- Bond yield: **6%** continuously compounded
- Risk-free: **4%** per annum
- S&P 500 futures: **1,200**, contract size **$250**
- Vol: **15%** annualised

---

## Code

```python
import pandas as pd
import numpy as np
from scipy.stats import beta
import matplotlib.pyplot as plt

Portfolio      = 5000000
p_beta         = 1.4
SP500_future   = 1200
Contract_size  = SP500_future * 250
vol_annualised = 0.15
Rc             = 0.06   # continuous rate
risk_free_rate = 0.04

# Part 1 — Rate Conversion
R_annual    = 1 * (np.exp(Rc/1) - 1)
R_quarterly = 4 * (np.exp(Rc/4) - 1)

# Part 2 — Bond Pricing
PV = (3*np.exp(-0.04*0.5) + 3*np.exp(-0.045*1.0) +
      3*np.exp(-0.05*1.5) + 1003*np.exp(-0.06*2.0))

# Part 3 — Hedge + Monte Carlo
N = round(p_beta * (Portfolio / Contract_size))
scenarios_arr = np.random.normal(loc=SP500_future, scale=SP500_future*(vol_annualised/2), size=1000)

Hedged_1, Unhedged_1 = [], []
for scenario in scenarios_arr:
    futures_pnl  = N * 250 * (SP500_future - scenario)   # short hedge
    index_return = (scenario - SP500_future) / SP500_future
    capm         = risk_free_rate + p_beta * (index_return - risk_free_rate)
    unhedged     = Portfolio * (1 + capm)
    hedged       = unhedged + futures_pnl
    Hedged_1.append(hedged)
    Unhedged_1.append(unhedged)

Hedged_f   = np.array(Hedged_1)
Unhedged_f = np.array(Unhedged_1)

# Part 4 — Bayesian (30 trades: 20W, 10L)
prior     = beta(1, 1)
posterior = beta(21, 11)
x         = np.linspace(0, 1, 1000)
ci_low, ci_high = posterior.interval(0.95)
p_above_55 = 1 - posterior.cdf(0.55)
```

---

## Results

### Part 1 — Compounding Conversion

```
Annual rate:    6.18%
Quarterly rate: 6.05%
```

Formula: `Rm = m × (e^(Rc/m) - 1)`

### Part 2 — Bond Price

```
Present Value: $898.17
```

2-year bond, $1000 face, 5% semiannual coupon, discounted at zero rates: 0.5yr=4%, 1yr=4.5%, 1.5yr=5%, 2yr=6%

### Part 3 — Monte Carlo Hedge

```
N* contracts: 23
Mean:         $4,919,693
Std:          $7,655
VaR 95%:      $4,906,391
Win Rate:     50%
```

Hedged std ($7.6k) vs unhedged ($~750k) — hedge reduced risk dramatically.

### Part 4 — Bayesian Win Rate (30 trades)

```
Mean win rate: 66%
95% CI:        49% → 81%
P(>55%):       89.45%
```

---

## Key Mistakes to Avoid

> [!WARNING]
> 
> - `for scenarios in scenarios` overwrites array — always use `for scenario in scenarios_arr`
> - Quarterly rate must be annualised: `4 × (e^(Rc/4) - 1)` not just `e^(Rc/4) - 1`
> - `p_above_55 = 1 - posterior.cdf(0.55)` not `posterior.cdf(0.55)` — cdf gives P(≤x), need 1-cdf for P(>x)

---

