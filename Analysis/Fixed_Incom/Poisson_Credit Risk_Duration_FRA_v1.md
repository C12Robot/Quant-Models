---

## tags: [hull, chapter-4, poisson, duration, forward-rates, FRA, python, quant, practice] date: 2026-05-13 project: Quant 1 status: done
---

## Setup

- Bond portfolio: **$10,000,000**, duration **3.5 years**, yield **5%**
- 500 corporate bonds, default probability **0.4%** each
- Zero rates: 1yr=4%, 2yr=4.5%, 3yr=5%, 4yr=5.5%
- FRA: receive 6%, pay LIBOR on $1,000,000, year 1→2

---

## Code

```python
import numpy as np
from scipy.stats import poisson
import matplotlib.pyplot as plt

# Part 1 — Poisson Credit Risk
lam = 500 * 0.004   # λ = 2 expected defaults
p_0       = poisson.pmf(k=0, mu=lam)
p_3       = poisson.pmf(k=3, mu=lam)
p_above_8 = 1 - poisson.cdf(k=8, mu=lam)

k_values     = np.arange(0, 16)
poisson_prob = poisson.pmf(k_values, mu=lam)

plt.bar(k_values, poisson_prob, color='red', alpha=0.7)
plt.xlabel('Defaults (k)')
plt.ylabel('Probability')
plt.title('Poisson Distribution — Credit Portfolio')
plt.show()

# Part 2 — Duration & Price Sensitivity
Portfolio = 10000000
D         = 3.5
delta_B_50  = -Portfolio * D * 0.005    # +50bp
delta_B_25  = -Portfolio * D * -0.0025  # -25bp
D_star      = D / (1 + 0.05/2)          # modified duration (m=2)

# Part 3 — Forward Rates
F_1_2 = (0.045*2 - 0.04*1) / 1    # = 5%
F_2_3 = (0.05*3  - 0.045*2) / 1   # = 6%
F_3_4 = (0.055*4 - 0.05*3) / 1    # = 7%

# Part 4 — FRA Valuation
LIBOR = 1000000
FRA   = LIBOR * (0.06 - F_1_2) * 1 * np.exp(-0.045 * 2)
```

---

## Results

### Part 1 — Credit Risk

|Metric|Value|
|---|---|
|λ (expected defaults)|2|
|P(zero defaults)|13.53%|
|P(exactly 3 defaults)|18.04%|
|P(more than 8 defaults)|0.024%|

### Part 2 — Duration

|Scenario|ΔB|New Portfolio Value|
|---|---|---|
|+50bp yield rise|-$175,000|$9,825,000|
|-25bp yield fall|+$87,500|$10,087,500|
|Modified Duration D*|3.4146|—|

### Part 3 — Forward Rates

|Period|Forward Rate|
|---|---|
|Year 1→2|5.00%|
|Year 2→3|6.00%|
|Year 3→4|7.00%|

Upward sloping zero curve → forward rates > zero rates ✅

### Part 4 — FRA

```
FRA value = $9,139
```

Positive because RK (6%) > RF (5%) — receiving above-market rate → profitable.

---

## Key Formulas Used

```python
# Poisson
poisson.pmf(k, mu=lam)          # P(exactly k)
1 - poisson.cdf(k, mu=lam)      # P(more than k)

# Duration
ΔB = -B × D × Δy               # price change
D* = D / (1 + y/m)              # modified duration

# Forward Rate
RF = (R2×T2 - R1×T1) / (T2-T1)

# FRA Value (receive fixed)
VFRA = L × (RK - RF) × (T2-T1) × e^(-R2×T2)
```

[[Poisson_Credit Risk_Duration_FRA_v1 (Ch-4)]]