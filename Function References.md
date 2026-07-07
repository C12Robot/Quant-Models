# Function Reference — pandas / numpy / sklearn

_Built from real bugs hit during JPM Forage QR simulation, not a generic list. Add to this as new functions actually get used — don't pre-load functions you haven't needed yet._

---

## pandas

### `pd.read_csv(path)`

**Logic:** loads a CSV into a DataFrame. **Gotcha:** Windows paths need `r"..."` (raw string) — backslashes are escape characters otherwise. **Where used:** every task, first line.

### `df['col'] = pd.to_datetime(df['col'])`

**Logic:** converts a column of date-strings into actual datetime objects, enabling date arithmetic. **Gotcha:** `df = pd.to_datetime(df['col'])` (no bracket on the left) destroys the whole DataFrame, keeping only dates. Always assign back to the same column, don't overwrite the frame. **Where used:** Task 1, Task 2.

### `df.set_index('col')`

**Logic:** makes a column the DataFrame's index instead of a plain column — enables date-based lookups like `df.loc['2024-01-01']`. **Where used:** Task 1.

### `.iloc[]` vs `[]` / `.loc[]`

**Logic:** `.iloc[n]` = positional lookup (the nth row, regardless of index labels). `[]`/`.loc[]` = label-based lookup (looks for an index value literally equal to what's in the brackets). **Gotcha (biggest recurring bug this session):** `series[19]` tries to find index label `19` — if the index is FICO scores or dates, not row numbers, this throws `KeyError` even though row 19 clearly exists. Use `.iloc[19]` for "the 19th item," reserve `[]`/`.loc[]` for "the item labeled X." **Where used:** Task 1 (date lookups), Task 4 (cum_n/cum_k indexing) — hit this exact bug in both.

### `df.groupby('col')['target'].agg(['count','sum'])`

**Logic:** groups rows by unique values in `col`, then computes aggregate stats per group. `count` = rows per group, `sum` = sum of `target` per group (useful for 0/1 columns — sum = count of 1s). **Where used:** Task 3 (correlation check), Task 4 (per-FICO-score default counts).

### `.cumsum()`

**Logic:** running total — each row becomes the sum of itself plus everything before it. **Why it matters:** lets you get the total (n or k) for any range `[a,b]` via `cumsum[b] - cumsum[a-1]`, in O(1), instead of re-summing raw rows every time. **Where used:** Task 2 (implicitly, duration calc), Task 4 (cum_n, cum_k for bucket_score).

---

## numpy

### `np.column_stack([arr1, arr2, ...])`

**Logic:** stacks separate 1D arrays as columns into one 2D matrix. Each input array = one column; order matters, determines which regression coefficient maps to which regressor. **Where used:** Task 1 — building the design matrix (trend, sin, cos, intercept) for the regression.

### `np.linalg.lstsq(X, y, rcond=None)`

**Logic:** solves least-squares regression — finds coefficients minimizing `||X@coeffs - y||²`. Returns 4 things; only the first (coefficients) is usually needed, so `coeffs, *_ = np.linalg.lstsq(...)` discards the rest. **Where used:** Task 1 — fitting trend + seasonal model.

### `np.sin()`, `np.cos()`, `np.log()`, `np.exp()`

**Logic:** standard math functions, vectorized (apply elementwise to whole arrays, not just single numbers). **Gotcha:** `np.log(0)` = `-inf`, breaks calculations — always guard degenerate cases (e.g. `p==0 or p==1` before taking `log(p)`). **Where used:** Task 1 (seasonal terms), Task 4 (log-likelihood).

### `np.ones(n)`

**Logic:** array of `n` ones — used as the "intercept" column in a regression design matrix (multiplying by a constant coefficient shifts the whole fit up/down). **Where used:** Task 1.

---

## sklearn

### `train_test_split(X, y, test_size=0.2, random_state=42)`

**Logic:** randomly shuffles and splits data into train/test subsets, so model evaluation happens on data it never saw during fitting — the only way to check if a model actually generalizes vs. just memorized. **Gotcha:** `random_state` value is arbitrary (42 has no special meaning — pop-culture convention), just needs to be fixed for reproducibility. **Where used:** Task 3.

### `StandardScaler()`

**Logic:** rescales each feature to mean 0, std 1. Needed when features sit on very different numeric scales (income in 10,000s vs. years_employed in single digits) — otherwise some solvers fail to converge. **Gotcha (real bug hit):** `.fit_transform()` on train data (learns + applies scaling), but `.transform()` only on test data — never `fit_transform` on test, or the test set gets scaled by its own statistics instead of the training distribution's, silently invalidating the evaluation. **Where used:** Task 3.

### `LogisticRegression()`

**Logic:** fits a binary classifier — predicts log-odds as a linear combination of features, squashed through sigmoid into a 0-1 probability. **When to use over alternatives:** default starting point for any binary (0/1) target. Move to `DecisionTreeClassifier`/`RandomForestClassifier` only if logistic regression's accuracy/AUC is clearly weak, signaling a non-linear boundary. **Where used:** Task 3.

### `.predict()` vs `.predict_proba()`

**Logic:** `.predict()` returns hard 0/1 labels (0.5 threshold). `.predict_proba()` returns actual probabilities for both classes as a 2-column array — `[:, 1]` selects P(class=1). **Where used:** Task 3.

### `accuracy_score(y_true, y_pred)` / `roc_auc_score(y_true, y_proba)`

**Logic:** `accuracy_score` = fraction of exact label matches. `roc_auc_score` = ranking quality across all thresholds, not just 0.5 — more informative when classes are imbalanced. **Where used:** Task 3.

---

## Decision guide: which model type, given the target variable

|Target variable looks like...|Use|
|---|---|
|A continuous number (price, dollar amount)|`LinearRegression` / `np.linalg.lstsq`|
|Binary (0/1) and roughly linearly separable|`LogisticRegression` — always start here|
|Binary but boundary looks non-linear (logistic underperforms)|`DecisionTreeClassifier` → `RandomForestClassifier`|
|No target column at all (unlabeled grouping)|`KMeans`|
|Too many correlated features|`PCA` (dimensionality reduction)|

**Rule of thumb:** always start with the simplest model matching the target's shape. Only escalate complexity when the simple model's metrics (accuracy/AUC/R²) are demonstrably weak — don't reach for a fancier tool preemptively.

---

## Adjacent libraries — not yet used, worth knowing exist

- `matplotlib.pyplot` — `.plot()`, `.legend()`, `.show()` (already used, Task 1-2 plots)
- `scipy.stats` — probability distributions, hypothesis tests
- `statsmodels` — regression with full statistical output (p-values, confidence intervals) — often preferred over sklearn in banking/finance contexts for interpretability over raw prediction accuracy