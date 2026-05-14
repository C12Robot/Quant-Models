---

## tags: [hull, chapter-2, chapter-3, chapter-4, comprehensive, poisson, duration, FRA, monte-carlo, python, quant] date: 2026-05-14 project: Quant 1 status: done
---


## Setup

- Bond portfolio: **$8,000,000**, duration **4.2 years**, yield **6%** continuously compounded
- Corporate bonds: **800 bonds**, P(default) = **0.5%** each
- S&P 500 futures: **1,400**, contract size **$250**, portfolio β = **1.6**
- Zero rates: 1yr=3%, 2yr=3.5%, 3yr=4%, 4yr=4.5%, 5yr=5%
- FRA: receive **5.5%** fixed, pay LIBOR on **$2,000,000**, year 2→3

---

## Code

```python
import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt

# Part 1 — Compounding
Rc = 0.06
Annual   = 1 * (np.exp(Rc/1) - 1)
Quarterly = 4 * (np.exp(Rc/4) - 1)

# Part 2 — Poisson Credit Risk
lam = 800 * 0.005   # λ = 4
p_0        = poisson.pmf(k=0,  mu=lam)
p_exactly_4 = poisson.pmf(k=4, mu=lam)
p_more_10  = 1 - poisson.cdf(k=10, mu=lam)

k_values   = np.arange(0, 16)
prob_values = poisson.pmf(k_values, mu=lam)
plt.bar(k_values, prob_values, color='red', alpha=0.7)
plt.title('Poisson Distribution — Credit Portfolio')
plt.show()

# Part 3 — Forward Rates
F_1_2 = (0.035*2 - 0.03*1)  / 1   # = 4%
F_2_3 = (0.04*3  - 0.035*2) / 1   # = 5%
F_3_4 = (0.045*4 - 0.04*3)  / 1   # = 6%
F_4_5 = (0.05*5  - 0.045*4) / 1   # = 7%

# Part 4 — FRA Valuation
LIBOR = 2000000
FRA = LIBOR * (0.055 - F_2_3) * 1 * np.exp(-0.035*2)

# Part 5 — Duration
bond_port = 8000000
D = 4.2
Delta_B_100 = -bond_port * D * 0.01
Delta_B_50  = -bond_port * D * -0.005
D_star = D / (1 + 0.06/1)

# Part 6 — Monte Carlo Hedge
Portfolio     = 8000000
SP500_futures = 1400
Contract_size = SP500_futures * 250
beta          = 1.6
risk_free     = 0.055
N             = round(beta * (Portfolio / Contract_size))

scenarios_arr = np.random.normal(loc=SP500_futures, scale=SP500_futures*0.20/2, size=1000)
Hedged_1, Unhedged_1 = [], []

for scenario in scenarios_arr:
    futures_pnl   = N * 250 * (SP500_futures - scenario)
    index_return  = (scenario - SP500_futures) / SP500_futures
    capm          = risk_free + beta * (index_return - risk_free)
    unhedged      = Portfolio * (1 + capm)
    hedged        = unhedged + futures_pnl
    Hedged_1.append(hedged)
    Unhedged_1.append(unhedged)

Hedged_f   = np.array(Hedged_1)
Unhedged_f = np.array(Unhedged_1)
VaR_95     = np.percentile(Hedged_f, 5)
pass_rate  = (Hedged_f > 7500000).sum() / 10
```

---

## Results

### Part 1 — Compounding

|Rate|Value|
|---|---|
|Annual|6.18%|
|Quarterly|6.05%|

### Part 2 — Credit Risk (λ=4)

|Metric|Value|
|---|---|
|P(zero defaults)|1.83%|
|P(exactly 4)|19.54%|
|P(more than 10)|0.28%|

### Part 3 — Forward Rates

|Period|Forward Rate|
|---|---|
|1→2|4.00%|
|2→3|5.00%|
|3→4|6.00%|
|4→5|7.00%|

### Part 4 — FRA

```
Value = $18,648   (positive: RK=5.5% > RF=5%)
```

### Part 5 — Duration

|Scenario|ΔB|New Value|
|---|---|---|
|+100bp|-$336,000|$7,664,000|
|-50bp|+$168,000|$8,168,000|
|Modified D*|3.96|—|

### Part 6 — Monte Carlo

|Metric|Value|
|---|---|
|Mean|$9,143,974|
|Std|$1,508|
|VaR 95%|$9,141,477|
|Pass Rate (>$7.5M)|100%|

Hedge is extremely tight — std of only $1,508 vs unhedged spread of ~$300,000.

---

## Issues Found in Code

> [!WARNING] FRA Formula Error Used `T2-T1 = 2` instead of `1`. Year 2→3 is a 1-year period. Should be: `FRA = LIBOR × (RK - RF) × 1 × e^(-R2×T2)`

> [!WARNING] Vol in Monte Carlo Used `Vol_annualised = 0.02` (2%) but question stated 20%. Should be `0.20`. This is why hedged std was only $1,508 — unrealistically tight.

> [!WARNING] CAPM Sign Error `Total_index_return = risk_free - beta*(index_return - risk_free)` — wrong sign. Should be: `capm = risk_free + beta*(index_return - risk_free)`

> [!WARNING] Loop Variable `for scenarios in scenarios` — overwrites array. Always use `for scenario in scenarios_arr`.

---

## Links

- [[Hull Chapter 4 Part 5 Convexity Term Structure]]
- [[Hull Ch4 Practice CreditRisk Duration FRA v1]]
- [[Quant Formula Reference Sheet]]