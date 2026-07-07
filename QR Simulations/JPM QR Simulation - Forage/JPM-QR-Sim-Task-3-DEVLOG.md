# JPMorgan Forage — Quantitative Research Virtual Experience

## Task 3: Loan Default Prediction & Expected Loss Model

---

### Background

The retail banking arm is seeing higher-than-expected personal loan defaults. The risk team needs a prototype model that predicts probability of default (PD) from borrower characteristics, then converts that into expected loss — so capital reserves can be sized appropriately. Given a recovery rate of 10%, expected loss = PD × (1 − recovery rate) × loan exposure.

**Data:** 10,000 borrower rows — `credit_lines_outstanding`, `loan_amt_outstanding`, `total_debt_outstanding`, `income`, `years_employed`, `fico_score`, and the target `default` (0/1). `customer_id` excluded (identifier, not predictive).

---

### Approach

This is a classification problem, structurally different from Tasks 1-2 (which were deterministic regression/arithmetic) — it requires training on labeled historical data, then evaluating generalization before trusting the model on new borrowers.

1. **Split features (`X`) from target (`Y`)** — 6 real predictors, `default` as target.
2. **Train/test split (80/20)** — hold out data the model never sees during training, to measure genuine generalization rather than memorization.
3. **Scale features** — `StandardScaler`, since raw features sit on wildly different numeric ranges (income in tens of thousands vs. years_employed in single digits), which was causing the logistic regression solver to fail to converge.
4. **Fit logistic regression** — predicts log-odds of default as a linear combination of features, squashed through a sigmoid into a 0-1 probability.
5. **Evaluate on held-out test data** — accuracy and AUC (AUC preferred since default is imbalanced, ~18.5% positive class).
6. **Wrap into a single-borrower function** — `credit_risk()` takes raw borrower inputs, applies the _same_ fitted scaler, gets PD from the _same_ fitted model, and computes expected loss.

---

### Code (final version)

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

loans = pd.read_csv(r"C:\Users\meena\Documents\testing\Loan_Data.csv")

X = loans[['credit_lines_outstanding','loan_amt_outstanding', 'total_debt_outstanding', 'income', 'years_employed', 'fico_score']]
Y = loans['default']
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression()
model.fit(X_train_scaled, Y_train)

y_predict = model.predict(X_test_scaled)
y_probability = model.predict_proba(X_test_scaled)[:, 1]

print(f"Accuracy of Model:", accuracy_score(Y_test, y_predict))
print(f"AUC:", roc_auc_score(Y_test, y_probability))

def credit_risk(credit_lines_outstanding, loan_amt_outstanding, total_debt_outstanding, income, years_employed, fico_score):
    input_data = [[credit_lines_outstanding, loan_amt_outstanding, total_debt_outstanding, income, years_employed, fico_score]]
    input_scaled = scaler.transform(input_data)
    pd_estimate = float(model.predict_proba(input_scaled)[:, 1][0])
    expected_loss = float(pd_estimate * (1 - 0.1) * loan_amt_outstanding)
    return pd_estimate, expected_loss

Probability, expected_loss = credit_risk(credit_lines_outstanding=5, loan_amt_outstanding=1958.92873, total_debt_outstanding=8228.753, income=26648.44, years_employed=2, fico_score=572)
print(f"Probability of Default: {Probability*100}%")
print(f"Expected Loss: ${expected_loss:,.2f}")
```

---

### Why X_train / X_test are both needed even though only `model` and `scaler` appear in `credit_risk()`

Three separate jobs share one trained model, and it's easy to conflate them:

- **`X_train` / `Y_train`** — used once, to fit `scaler` and `model`. Their job ends there; they never appear again.
- **`X_test` / `Y_test`** — used once, to _prove_ the fitted model generalizes to data it never saw (the 0.9955 accuracy / 0.9999 AUC numbers). This is the evidence that justifies trusting the model at all — without it, there's no basis for claiming the model works on new borrowers, only that it fits the training data (which could just mean memorization).
- **`credit_risk()`** — a third, independent use of the _already-trained_ `model` and `scaler` on a brand-new borrower who isn't in either split.

If the train/test split were skipped entirely and the model fit on all 10,000 rows, `credit_risk()` would return identical numbers — the split doesn't change the final function's behavior. Its entire value is upstream: generating the evidence that the model is trustworthy before wrapping it into production use.

---

### Libraries and functions used — what each does

- **`train_test_split`** (`sklearn.model_selection`) — shuffles and splits `X`/`Y` into train/test subsets. `test_size=0.2` → 20% held out for testing, 80% for training. `random_state=42` fixes the random shuffle so the split is reproducible across runs (42 has no special meaning — any fixed integer works identically, it's just a common convention).
    
- **`StandardScaler`** (`sklearn.preprocessing`) — rescales each feature to mean 0, std 1. `.fit_transform(X_train)` learns the mean/std from training data and applies the transform in one step. `.transform(X_test)` (no `fit`) reuses the _training_ set's mean/std on test data — critical: the scaler must never re-fit on test data, or test-set information leaks into the transformation, undermining the evaluation's validity.
    
- **`LogisticRegression`** (`sklearn.linear_model`) — fits a binary classifier: predicts log-odds as a linear combination of features, passed through a sigmoid (`1/(1+e^-z)`) to produce a probability in [0,1]. `.fit(X_train_scaled, Y_train)` finds the coefficients that best separate the two classes.
    
- **`.predict()`** vs **`.predict_proba()`** — `predict()` returns hard 0/1 labels using a 0.5 threshold. `predict_proba()` returns the actual probability for both classes as a 2-column array; `[:, 1]` selects the probability of class 1 (default) specifically.
    
- **`accuracy_score`** (`sklearn.metrics`) — fraction of exact label matches. **`roc_auc_score`** — measures ranking quality across all thresholds, not just 0.5; more informative than accuracy alone given the ~18.5%/81.5% class imbalance in this dataset.
    

---

### Results

**Model performance (held-out test set, 2,000 rows):**

- Accuracy: **0.9955**
- AUC: **0.9999565**

**Sanity check on the near-perfect AUC** — this level of separation is unusual for real-world credit data and was verified, not assumed, using a correlation check against the target:

|Feature|Correlation with default|
|---|---|
|`credit_lines_outstanding`|**0.863**|
|`total_debt_outstanding`|**0.759**|
|`fico_score`|−0.325|
|`years_employed`|−0.285|
|`loan_amt_outstanding`|0.099|
|`income`|0.016|

Group means confirmed genuine (not leaked) separability: defaulters average 4.6 credit lines outstanding (minimum 2) vs. non-defaulters averaging 0.74 (75th percentile only 1) — a near-clean split on this one feature alone. `income` turned out to be almost useless for prediction here (correlation 0.016), despite being an intuitive risk factor. Confirmed this is a synthetic teaching dataset deliberately constructed to be highly separable, not a data leakage bug.

**`credit_risk()` validated on two extremes:**

|Test profile|credit_lines|total_debt|PD|Expected Loss|
|---|---|---|---|---|
|Near-identical to a real non-defaulter row (0 credit lines)|0|$3,915|~2.4×10⁻¹¹ (~0%)|~$0|
|Near-identical to a real defaulter row (5 credit lines)|5|$8,229|**99.99998%**|**$1,763.04**|

Both align with the correlation analysis — the model correctly swings from near-certain non-default to near-certain default across the dataset's strongest risk signal.

---

### Mistakes made & fixed (learning log)

1. **Dropping to only 2 of 6 available predictors initially** (`credit_lines_outstanding`, `loan_amt_outstanding` only) without deliberate justification. **Lesson:** don't arbitrarily narrow the feature set on a first pass — use all reasonable predictors unless there's a specific reason (e.g. multicollinearity, known irrelevance) to exclude one.
    
2. **Solver convergence warning** (`lbfgs failed to converge`) — caused by unscaled features sitting on wildly different numeric ranges (income in the tens of thousands vs. years_employed in single digits). **Lesson:** logistic regression (and most gradient-based solvers) need standardized inputs; this isn't optional polish, it directly affects whether the fit even completes properly.
    
3. **Import typo** — `StandardScalar` instead of `StandardScaler`. **Lesson:** the class does scaling, not math ("scalar"); read error messages for exact naming rather than assuming a library/import problem when it's a spelling mistake.
    
4. **Re-fitting the scaler on test data** (`X_test_scaled = scaler.fit_transform(X_test)` instead of `scaler.transform(X_test)`) — this makes the test set scaled by its own statistics rather than the training distribution's, a subtle reverse-leakage that undermines the validity of the evaluation even though it doesn't throw an error. **Lesson:** `fit_transform` belongs on training data only; every subsequent use of the same transformer must be `transform` alone, reusing parameters learned once.
    
5. **Confusing a warning for an error** — reported "same error" when the actual output showed results printing correctly alongside a harmless `UserWarning` (missing feature names passed to a fitted scaler). **Lesson:** read the full output before concluding something failed; a warning does not halt execution the way an exception does.
    
6. **Reacting to a near-perfect AUC (0.9999) as if it were simply good news**, without first checking whether it indicated data leakage. Verified via a groupby/correlation check that the separability was genuine (driven by `credit_lines_outstanding` and `total_debt_outstanding` being extremely strong, deliberately-constructed signals in this synthetic dataset), not a bug. **Lesson:** a suspiciously good result is a prompt to verify, not a result to trust immediately — same instinct that flagged the ORB backtest's high out-of-sample Sharpe ratio earlier in this session.
    
7. **Losing track of why `X_train`/`X_test` matter** after they stopped appearing directly in the final `credit_risk()` function. **Lesson:** a train/test split's value is in the _evidence it produces_ (generalization proof), not in whether those variable names get reused later in the pipeline — the split's job is done once the model is fit and evaluated.
    

---

### Comparison against JPMorgan's official sample answer

**Features JPM used that we didn't:**

- `debt_to_income` = `total_debt_outstanding / income`
- `payment_to_income` = `loan_amt_outstanding / income`
- Dropped raw `income`, `loan_amt_outstanding`, `total_debt_outstanding` in favor of these two ratios, plus kept `credit_lines_outstanding`, `years_employed`, `fico_score` as-is.

**Why this is a real improvement, not just a different choice:** [Certain] Raw dollar figures don't mean the same thing across different income levels — $20K of debt is a minor concern for a $150K earner and a crisis for a $30K earner. A ratio captures that relationship directly; a raw-value model can only approximate it indirectly through interaction effects it isn't explicitly given. This likely explains why our correlation check found `income` alone nearly useless (0.016 correlation with default) — its predictive power was probably hiding inside a ratio the raw-feature model never got to see.

**What our version did better:**

1. [Certain] **We performed a train/test split; JPM's sample fit on 100% of the data with no held-out evaluation.** Their `y_pred = clf.predict(df[features])` checks the model against the same rows it trained on — this can't detect overfitting and overstates confidence in the reported error rate/AUC. Our 0.9955/0.9999 metrics are measured on genuinely unseen data, which is the more defensible methodology.
2. [Certain] **We verified the near-perfect AUC wasn't data leakage** via an explicit correlation/groupby check. JPM's sample doesn't address this at all — it reports the metric without questioning whether it's suspiciously high.
3. [Likely] **Our `credit_risk()` wrapper is a complete, testable function** (takes raw borrower inputs, returns PD + expected loss). JPM's sample stops at printing coefficients and an error rate — it doesn't wrap the model into a reusable prediction function or compute expected loss at all, despite that being the task's explicit final deliverable.

**What JPM's version did better:**

1. [Certain] **Ratio feature engineering** (above) — a genuinely stronger feature set, not just a stylistic choice.
2. [Likely] **Explicit solver tuning** (`solver='liblinear', tol=1e-5, max_iter=10000`) sidesteps the convergence problem via solver choice rather than requiring a separate scaling step — arguably more elegant, since ratio features already sit on comparable scales and don't need `StandardScaler` at all.

---

### Updated code — incorporating JPM's ratio features

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score

loans = pd.read_csv(r"C:\Users\meena\Documents\testing\Loan_Data.csv")

# Ratio features (JPM's approach) instead of raw dollar figures
loans['debt_to_income'] = loans['total_debt_outstanding'] / loans['income']
loans['payment_to_income'] = loans['loan_amt_outstanding'] / loans['income']

features = ['credit_lines_outstanding', 'debt_to_income', 'payment_to_income', 'years_employed', 'fico_score']
X = loans[features]
Y = loans['default']

# Keep our train/test split — JPM's sample skipped this, we don't
X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

# Ratio features are already comparable in scale — no StandardScaler needed,
# matching JPM's solver-tuning approach instead
model = LogisticRegression(solver='liblinear', tol=1e-5, max_iter=10000)
model.fit(X_train, Y_train)

y_predict = model.predict(X_test)
y_probability = model.predict_proba(X_test)[:, 1]

print("Accuracy of Model:", accuracy_score(Y_test, y_predict))
print("AUC:", roc_auc_score(Y_test, y_probability))

def credit_risk(credit_lines_outstanding, loan_amt_outstanding, total_debt_outstanding, income, years_employed, fico_score):
    debt_to_income = total_debt_outstanding / income
    payment_to_income = loan_amt_outstanding / income
    input_data = [[credit_lines_outstanding, debt_to_income, payment_to_income, years_employed, fico_score]]
    pd_estimate = float(model.predict_proba(input_data)[:, 1][0])
    expected_loss = float(pd_estimate * (1 - 0.1) * loan_amt_outstanding)
    return pd_estimate, expected_loss

Probability, expected_loss = credit_risk(credit_lines_outstanding=5, loan_amt_outstanding=1958.92873, total_debt_outstanding=8228.753, income=26648.44, years_employed=2, fico_score=572)
print(f"Probability of Default: {Probability*100}%")
print(f"Expected Loss: ${expected_loss:,.2f}")
```

Note: this version keeps our train/test split and expected-loss wrapper (our stronger points) while adopting JPM's ratio features and solver tuning (their stronger points) — not a wholesale swap, a merge of both approaches' best parts. Not yet run — worth executing and comparing the new AUC/accuracy against the original raw-feature version before deciding which to keep in the final submission.

---

Task 3 complete: logistic regression trained and evaluated (Accuracy 0.9955, AUC 0.9999), separability verified as genuine via correlation analysis (not leakage), `credit_risk()` function wraps PD + expected loss for any new borrower, validated on both a near-certain-safe and near-certain-default profile. Ready to move to Task 4.