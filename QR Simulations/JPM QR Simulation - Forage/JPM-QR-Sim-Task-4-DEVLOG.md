# JPMorgan Forage — Quantitative Research Virtual Experience

## Task 4: FICO Score Bucketing via Dynamic Programming

---

### Background

Risk wants FICO scores converted into a fixed number of categorical buckets (ratings) for a mortgage default model, since the model architecture requires categorical inputs. The approach must generalize — given any target number of buckets, find the boundaries that best summarize the data. Lower rating = better credit score, per the task's explicit requirement. This is a quantization problem: minimize information loss when compressing a continuous range (FICO 300-850) into discrete categories, solvable via dynamic programming since the optimal split of the full range builds on optimal splits of sub-ranges.

**Objective function used:** log-likelihood. For a bucket with `n` borrowers and `k` defaults, `p = k/n` is the bucket's default rate. Log-likelihood `k·ln(p) + (n−k)·ln(1−p)` rewards buckets that are internally homogeneous (mostly-default or mostly-safe) and penalizes mixed buckets — maximized when `p` is close to 0 or 1, most negative when `p≈0.5`.

---

### Approach

1. **Group raw data by FICO score** — get per-score counts (`n`) and defaults (`k`) via `groupby`, rather than iterating over every individual borrower row repeatedly.
2. **Cumulative sums** (`cum_n`, `cum_k`) — allow computing `n, k` for any candidate bucket range in O(1) instead of re-summing each time.
3. **`bucket_score(start, end)`** — log-likelihood contribution of treating one range of scores as a single bucket.
4. **DP table `dp[j][i]`** — best total log-likelihood achievable using `j` buckets over the first `i` sorted unique scores. Built by trying every possible position for the last cut and keeping the best: `dp[j][i] = max over m of (dp[j-1][m] + bucket_score(m, i))`.
5. **Reconstruct boundaries** by walking back through `split[j][i]`, which records where each optimal cut occurred.
6. **Rating function** — maps a raw FICO score to a bucket, then reverses the rating so the highest-FICO bucket gets rating 1 (best), lowest gets rating 5 (worst), per the task's requirement.

---

### Results

**Best total log-likelihood (5 buckets): -4255.38**

**Reconstructed boundaries:**

|Rating|FICO Range|n (borrowers)|
|---|---|---|
|5 (worst)|408 – 520|301|
|4|521 – 580|1,407|
|3|581 – 640|3,438|
|2|641 – 696|3,197|
|1 (best)|697 – 850|1,657|

Sample sizes roughly bell-shaped (thin tails, fat middle) — consistent with FICO scores being roughly normally distributed across a real population, a sanity signal that the DP found sensible splits rather than degenerate ones.

**`fico_to_rating()` validated:** 444→5, 610→3, 800→1 — correct across low, mid, and high FICO ranges.

---

### Code (original version, before comparison)

```python
import pandas as pd
import numpy as np

fico = pd.read_csv(r"C:\Users\meena\Documents\testing\Loan_Data.csv")
fico_grouped = fico.groupby('fico_score')['default'].agg(['count', 'sum'])
fico_grouped['cum_n'] = fico_grouped['count'].cumsum()
fico_grouped['cum_k'] = fico_grouped['sum'].cumsum()

def bucket_score(start_idx, end_idx, cum_n, cum_k):
    n = cum_n.iloc[end_idx] - (cum_n.iloc[start_idx-1] if start_idx > 0 else 0)
    k = cum_k.iloc[end_idx] - (cum_k.iloc[start_idx-1] if start_idx > 0 else 0)
    if n == 0 or k == 0 or k == n:
        return 0
    p = k/n
    return k * np.log(p) + (n-k) * np.log(1-p)

scores = fico_grouped.index.tolist()
cum_n = fico_grouped['cum_n']
cum_k = fico_grouped['cum_k']
n_scores = len(scores)
n_buckets = 5

dp = [[-np.inf] * (n_scores + 1) for _ in range(n_buckets + 1)]
split = [[0] * (n_scores + 1) for _ in range(n_buckets + 1)]

dp[0][0] = 0

for j in range(1, n_buckets + 1):
    for i in range(1, n_scores + 1):
        for m in range(j - 1, i):
            score = dp[j-1][m] + bucket_score(m, i - 1, cum_n, cum_k)
            if score > dp[j][i]:
                dp[j][i] = score
                split[j][i] = m

print(dp[n_buckets][n_scores])

def fico_to_rating(score, boundaries):
    boundaries = [520, 580, 640, 696, 850]
    for i, b in enumerate(boundaries):
        if score <= b:
            return len(boundaries) - i
    return 1

final = fico_to_rating(score=900, boundaries=[520, 580, 640, 696, 850])
print(final)
```

**Output:** `-4255.377391458947`, then `1` (from the `score=900` test — see note below on why this test case is flawed).

---

### JPM's official sample answer (full)

```python
import pandas as pd
from math import log
import os

cwd = os.getcwd()
print("Current working directory: {0}".format(cwd))
print("os.getcwd() returns an object of type {0}".format(type(cwd)))

# copy the filepath
os.chdir("________")
df = pd.read_csv('loan_data_created.csv')

x = df['default'].to_list()
y = df['fico_score'].to_list()
n = len(x)
print(len(x), len(y))

default = [0 for i in range(851)]
total = [0 for i in range(851)]

for i in range(n):
    y[i] = int(y[i])
    default[y[i]-300] += x[i]
    total[y[i]-300] += 1

for i in range(0, 551):
    default[i] += default[i-1]
    total[i] += total[i-1]

import numpy as np

def log_likelihood(n, k):
    p = k/n
    if (p==0 or p==1):
        return 0
    return k*np.log(p) + (n-k)*np.log(1-p)

r = 10
dp = [[[-10**18, 0] for i in range(551)] for j in range(r+1)]

for i in range(r+1):
    for j in range(551):
        if (i==0):
            dp[i][j][0] = 0
        else:
            for k in range(j):
                if (total[j]==total[k]):
                    continue
                if (i==1):
                    dp[i][j][0] = log_likelihood(total[j], default[j])
                else:
                    if (dp[i][j][0] < (dp[i-1][k][0] + log_likelihood(total[j]-total[k], default[j]-default[k]))):
                        dp[i][j][0] = log_likelihood(total[j]-total[k], default[j]-default[k]) + dp[i-1][k][0]
                        dp[i][j][1] = k

print(round(dp[r][550][0], 4))

k = 550
l = []
while r >= 0:
    l.append(k+300)
    k = dp[r][k][1]
    r -= 1
print(l)
```

---

### Comparing the two & the adjustment made

**Real bug I found in my own final test, only visible by comparing carefully against JPM's structure:** I tested `fico_to_rating(score=900, boundaries=...)` — but FICO scores only go up to 850 (confirmed by the dataset itself and by FICO's own definition). `900` isn't a value that can exist in real data, yet the function silently returned `1` without any error or warning, because it happens to fall through every boundary check. JPM's dense-array approach (`range(851)`, i.e. indices 0-850) implicitly bounds valid input by array size — an out-of-range score would simply never have been aggregated into their `default`/`total` arrays in the first place, surfacing the problem earlier, at data-loading time, rather than silently at prediction time.

**Adjustment made:** added explicit input validation to `fico_to_rating()`, since my structure (a plain function taking any integer) doesn't get this protection for free the way JPM's fixed-size array does:

```python
def fico_to_rating(score, boundaries):
    if not (300 <= score <= 850):
        raise ValueError(f"FICO score {score} out of valid range (300-850)")
    for i, b in enumerate(boundaries):
        if score <= b:
            return len(boundaries) - i
    return 1

# Corrected test cases — all within valid FICO range
print(fico_to_rating(444, [520, 580, 640, 696, 850]))  # 5
print(fico_to_rating(610, [520, 580, 640, 696, 850]))  # 3
print(fico_to_rating(800, [520, 580, 640, 696, 850]))  # 1
```

**Other structural differences, not bugs — genuine design forks (already covered, kept here for completeness):**

||My approach|JPM's sample|
|---|---|---|
|Data structure|`groupby` on 374 real unique scores|Dense array over all 851 possible scores (300-850), most empty|
|Bucket count|Parameter (`n_buckets`) — genuinely general, matching the task's own requirement|Hardcoded `r=10` — less general despite the task explicitly asking for a general approach|
|Degenerate-range handling|Avoided naturally (never iterate over unpopulated score positions)|Explicit `if total[j]==total[k]: continue` guard needed, a direct consequence of the dense-array structure|
|Input validation|Added after finding the `score=900` gap (see above)|Implicit via fixed array bounds — invalid scores never enter the data in the first place|

---

### Mistakes made & fixed (learning log)

1. **Label indexing vs. positional indexing confusion** — `cum_n[end_idx]` looked up a FICO _score value_ equal to `end_idx` (e.g. literally score "19"), rather than the 19th position in the data — threw `KeyError`. **Lesson:** pandas `Series[]` does label-based lookup by default; `.iloc[]` is required for positional lookup, and conflating the two silently produces wrong results or crashes depending on whether the label happens to exist.
    
2. **Copy-paste index-variable bug in the DP loop** — wrote `for i in range(1, n_buckets + 1)` instead of `range(1, n_scores + 1)`, meaning the DP table only ever filled its first 5 columns (matching `n_buckets`) instead of all 374 needed positions. Everything past index 5 silently stayed at its `-inf` initialization value. **Lesson:** when two loop variables represent conceptually different quantities (buckets vs. scores) but are both small integers, a copy-paste typo between them doesn't throw an error — it just silently computes the wrong thing, which is more dangerous than a crash.
    
3. **Printing `dp[n_buckets][score]`** using a leftover loop variable (`score`, a log-likelihood float) as an array index instead of the intended final column (`n_scores`). **Lesson:** reused variable names across nested scopes are a common source of quietly wrong final output — check what a variable actually holds at the point it's used, not just what it was named for elsewhere in the function.
    
4. **`return 1` placed inside the for-loop instead of after it**, in the first draft of `fico_to_rating()` — this caused the function to return `1` prematurely on the very first iteration where the score didn't match the first boundary, rather than continuing to check subsequent boundaries. Because the first test case happened to be a low score that matched immediately, this bug wasn't caught until testing a mid-range score explicitly. **Lesson:** a bug that only manifests on certain input values (not all) is more dangerous than one that always crashes — test multiple representative cases (low, mid, high) before trusting a conditional/loop structure, not just the first one that happens to work.
    
5. **Never independently verified the DP recurrence conceptually before implementing it** — followed the structural hint closely without first confirming a from-scratch understanding of _why_ `dp[j][i] = max over m of (dp[j-1][m] + bucket_score(m,i))` is the correct recurrence (optimal substructure: the best j-bucket split up to position i must contain, as a sub-problem, the best (j-1)-bucket split up to wherever the last cut happens). **Lesson:** getting working code via hints is not the same as being able to derive or explain the approach cold in an interview — flagged as a genuine gap to close with dedicated review time, separate from having working code.
    

---

### Status

Task 4 complete: DP-based FICO bucketing (5 buckets, log-likelihood -4255.38), boundaries reconstructed and sanity-checked against expected sample-size distribution, rating function validated across low/mid/high FICO scores, and compared against JPM's official sample answer — own approach found to be more general (parameterized bucket count) and more efficient (grouped real data vs. dense array over all possible scores). This was the final task of the JPM Forage Quantitative Research Virtual Experience Program — **program complete**, certificate obtained and added to LinkedIn (July 7, 2026).

**Genuine gap remaining, not closed by task completion:** the DP recurrence was implemented successfully via structural hints but not yet independently re-derived from scratch. Before using this as interview material, revisit and explain the recurrence without referring back to this doc — that's the actual bar, not just having working code.