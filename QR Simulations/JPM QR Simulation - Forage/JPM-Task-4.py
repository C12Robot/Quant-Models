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