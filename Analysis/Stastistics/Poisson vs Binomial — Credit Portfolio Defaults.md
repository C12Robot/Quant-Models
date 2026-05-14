---

## tags: [quant, poisson, binomial, scipy, credit-risk, python, statistics] date: 2026-05-13 project: Quant 1 status: done
---

## Setup

- Portfolio: **1,000 bonds**
- Default probability per bond: **0.3%** (p = 0.003)
- λ = n × p = 1000 × 0.003 = **3 expected defaults**

---

## Code

```python
from scipy.stats import poisson, binom
import numpy as np
import matplotlib.pyplot as plt

lam = 1000 * 0.003   # λ = 3

# Key probabilities
P_5        = poisson.pmf(k=5, mu=lam)          # P(exactly 5 defaults)
P_0        = poisson.pmf(k=0, mu=lam)          # P(zero defaults)
P_more_10  = 1 - poisson.cdf(10, mu=lam)       # P(more than 10 defaults)

# Full distribution k=0 to 20
k_values     = np.arange(0, 21)
poisson_probs = poisson.pmf(k_values, mu=lam)
binom_probs   = binom.pmf(k_values, n=1000, p=0.003)

# Plot
plt.bar(k_values - 0.2, poisson_probs, width=0.4, label='Poisson', color='red')
plt.bar(k_values + 0.2, binom_probs,   width=0.4, label='Binomial', color='blue')
plt.xlabel('Number of Defaults')
plt.ylabel('Probability')
plt.title('Poisson vs Binomial — Credit Portfolio')
plt.legend()
plt.show()
```

---

## Standard Poisson Template

```python
from scipy.stats import poisson

lam = n * p                              # expected events

P_exact_k  = poisson.pmf(k=k, mu=lam)   # P(exactly k)
P_zero     = poisson.pmf(k=0, mu=lam)   # P(zero events) = e^(-λ)
P_more_k   = 1 - poisson.cdf(k, mu=lam) # P(more than k)
P_at_most_k = poisson.cdf(k, mu=lam)    # P(k or fewer)
```

---

## Results

|Metric|Value|
|---|---|
|λ (expected defaults)|3|
|P(exactly 5 defaults)|10.08%|
|P(zero defaults)|4.98%|
|P(more than 10 defaults)|0.029%|

---

## Key Observations

**Poisson ≈ Binomial** — bars almost perfectly overlap. Confirms:

- n = 1000 (large) ✅
- p = 0.003 (small) ✅
- n×p = 3 (manageable λ) ✅ → Poisson is a valid approximation

**Use Poisson when:** n > 20 and p < 0.05 **Use Binomial when:** n small or p moderate

---

## Finance Application

Same model applies to:

- Credit default portfolios (bonds, loans)
- Insurance claims in a period
- Trade failures in a settlement system
- Rare market events (flash crashes per year)

> [!TIP] Why Poisson for Credit Risk? A bank has thousands of loans. Each has tiny default probability. Tracking exact binomial is complex. Poisson gives same answer with just one parameter: λ = expected defaults.

---

