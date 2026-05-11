---

## tags: [hull, chapter-4, compounding, interest-rates, fixed-income, python, pandas] date: 2026-05-11 project: Quant 1 status: done
---
#  Compounding Exercise

## Question

$10,000 invested at 6% per annum for 5 years. Calculate terminal value under 4 compounding methods.

## Formulas

|Method|Formula|
|---|---|
|Annual|A(1 + R)^n|
|Quarterly (m=4)|A(1 + R/4)^(4n)|
|Monthly (m=12)|A(1 + R/12)^(12n)|
|Continuous|A × e^(R×n)|

## Code

```python
import pandas as pd
import numpy as np

Principal = 10000
n = 5
Rate_annual = 6/100

Annual_compounding    = Principal * (1 + Rate_annual)**n
Quarterly_compounding = Principal * (1 + Rate_annual/4)**(4*n)
Monthly_compounding   = Principal * (1 + Rate_annual/12)**(12*n)
Continuous_compounding = Principal * np.exp(Rate_annual * n)

Methods = ['Annual', 'Quarterly', 'Monthly', 'Continuous']
Values  = [Annual_compounding, Quarterly_compounding, Monthly_compounding, Continuous_compounding]

Final = pd.DataFrame({'Method': Methods, 'Terminal Value': Values})
print(Final)
```

## Output

|Method|Terminal Value|
|---|---|
|Annual|$13,382.26|
|Quarterly|$13,468.55|
|Monthly|$13,488.50|
|Continuous|$13,498.59|

## Key Insights

- More frequent compounding → higher terminal value
- Continuous compounding is the **upper bound** — no compounding frequency beats it
- Difference between monthly and continuous is tiny (~$10) — why continuous ≈ daily

## Mistake Made

Used `np.log(1 + R)` to convert rate then compounded for n=1 implicitly. **Fix:** Just use `np.exp(R × n)` directly — no conversion needed for continuous compounding.

