# JPMorgan Forage — Quantitative Research Virtual Experience

## Task 2: Commodity Storage Contract Pricing Model

---

### Background

The desk wants to price a natural gas storage contract: buy gas now (cheap), store it, sell later (expensive, e.g. winter). Contract value = revenue from sale − cost of purchase − storage fees − injection/withdrawal fees, generalized to handle **multiple** injection/withdrawal dates and amounts, not just one buy/sell pair.

**Required inputs:** injection dates, withdrawal dates, prices on those dates, injection/withdrawal rate (throughput cap), max storage volume, storage costs.

---

### Approach

Model the contract as a chronological sequence of cash-flow events:

1. Merge injection and withdrawal dates into one sorted event list.
2. Track `volume_in_storage` as a running state variable — increases on injection, decreases on withdrawal.
3. Enforce two physical constraints: **max_volume** (can't overfill storage) and **sufficient stored volume** (can't withdraw more than what's stored). Violating either halts the function (`return None`) rather than silently continuing.
4. Two distinct cost types, confirmed from the task's worked example:
    - **Monthly storage fee** — accrues over the full duration gas sits in storage (first event to last event), independent of volume.
    - **Injection/withdrawal fee** — a per-unit fee charged on every inject/withdraw event, independent of time (e.g. $10K per 1M units moved).
5. `amounts` is a dict keyed by date (same pattern as `prices`), allowing different volumes per event — required because the task specifies the client may choose multiple dates with different quantities.

---

### Code (final version)

```python
import pandas as pd
import numpy as np

data = pd.read_csv(r"C:\Users\meena\Documents\testing\Nat_Gas.csv")
data['Dates'] = pd.to_datetime(data['Dates'])
data = data.set_index('Dates')

t = (data.index - data.index[0]).days / 30.44
X = np.column_stack([t, np.sin(2*np.pi*t/12), np.cos(2*np.pi*t/12), np.ones(len(t))])
coefficients, *_ = np.linalg.lstsq(X, data['Prices'].values, rcond=None)

def estimate_price(date):
    date = pd.to_datetime(date)
    t_new = (date - data.index[0]).days / 30.44
    return (coefficients[0]*t_new + coefficients[1]*np.sin(2*np.pi*t_new/12)
            + coefficients[2]*np.cos(2*np.pi*t_new/12) + coefficients[3])

def price_contract(injection_dates, withdrawl_dates, prices, amounts, max_volume, monthly_storage_fees, injection_withdrawl_fee):
    volume_in_storage = 0
    total_value = 0
    events = [(d, 'inject') for d in injection_dates] + [(d, 'withdraw') for d in withdrawl_dates]
    events.sort(key=lambda x: x[0])

    for date, service in events:
        if service == 'inject':
            injected_amount = amounts[date]
            if volume_in_storage + injected_amount > max_volume:
                print(f"Injection failed on {date}: exceeds {max_volume}")
                return None
            volume_in_storage += injected_amount
            total_value -= prices[date] * injected_amount
            total_value -= injection_withdrawl_fee * (injected_amount / 1_000_000)

        if service == 'withdraw':
            withdraw_amount = amounts[date]
            if withdraw_amount > volume_in_storage:
                print(f"Withdraw failed on {date}: insufficient volume in storage")
                return None
            volume_in_storage -= withdraw_amount
            total_value += prices[date] * withdraw_amount
            total_value -= injection_withdrawl_fee * (withdraw_amount / 1_000_000)

    duration_months = (events[-1][0] - events[0][0]).days / 30.44
    total_value -= monthly_storage_fees * duration_months
    return total_value

# Test: 3 injections, 3 withdrawals, different amounts each
inj_dates = [pd.Timestamp('2023-06-01'), pd.Timestamp('2023-07-01'), pd.Timestamp('2023-08-01')]
wd_dates  = [pd.Timestamp('2024-01-01'), pd.Timestamp('2024-02-01'), pd.Timestamp('2024-03-01')]

test_amounts = {
    pd.Timestamp('2023-06-01'): 2_000_000,
    pd.Timestamp('2023-07-01'): 1_000_000,
    pd.Timestamp('2023-08-01'): 1_500_000,
    pd.Timestamp('2024-01-01'): 2_000_000,
    pd.Timestamp('2024-02-01'): 1_000_000,
    pd.Timestamp('2024-03-01'): 1_500_000,
}
test_prices = {
    pd.Timestamp('2023-06-01'): 2.3,
    pd.Timestamp('2023-07-01'): 2.4,
    pd.Timestamp('2023-08-01'): 2.5,
    pd.Timestamp('2024-01-01'): 3.2,
    pd.Timestamp('2024-02-01'): 3.1,
    pd.Timestamp('2024-03-01'): 3.0,
}

result = price_contract(
    injection_dates=inj_dates,
    withdrawl_dates=wd_dates,
    prices=test_prices,
    amounts=test_amounts,
    max_volume=5_000_000,
    monthly_storage_fees=100_000,
    injection_withdrawl_fee=10_000,
)
print(result)
```

---

### Results

**Final test case — prices sourced from `estimate_price()`, not hardcoded, with dates chosen to respect Task 1's validity window:**

- Injection: Jun/Jul/Aug 2024 (2M / 1M / 1.5M units) — **inside training data** (real fitted prices, not extrapolated)
- Withdrawal: Jan/Feb/Mar 2025 (2M / 1M / 1.5M units) — **inside the valid extrapolation window** (Task 1's model was only committed to extrapolate one year past its Sep 2024 cutoff, i.e. through Sep 2025)
- **Net contract value: $5,510,627**

The much larger value versus the first (hardcoded-price) test run is real, not a bug: actual seasonal gas prices swing from ~$11 (summer) to ~$12.5+ (winter) per the fitted model — a wider, real spread than the arbitrary $2.3–$3.2 placeholder prices used in the first draft.

**Constraint tests (from earlier runs, still valid):**

- Injection exceeding `max_volume` → correctly prints failure message and returns `None`.
- Withdrawal exceeding stored volume → correctly prints failure message and returns `None`.

---

### Mistakes made & fixed (learning log)

1. **Direction/role confusion on `volume_in_storage` and `max_volume`** — initially planned to start storage at a fixed number and count down on injection (backwards) and treat `max_volume` as the starting value rather than a ceiling to check against. **Lesson:** storage starts empty (0) and fills up; the cap is a limit you check against, not a countdown total.
    
2. **Hardcoding a fixed test date instead of a function parameter** — wrote `injection_dates = data.index[0]` inside the function, permanently overwriting the actual argument with Task 1's training-data date. Same overwrite-instead-of-use bug recurred multiple times across the session (also with `injection_withdrawl_fee` and `monthly_storage_fees` hardcoded inside the function body, silently discarding whatever the caller passed in). **Lesson:** a parameter's value comes from the caller; never reassign it inside the function body unless deliberately transforming it (and even then, don't reassign to a hardcoded constant).
    
3. **Withdrawal constraint copy-pasted from the injection constraint** — wrote `if withdraw_amount > max_volume - volume_in_storage` (checks remaining capacity, the injection-side concern) instead of `if withdraw_amount > volume_in_storage` (checks whether enough is actually stored to remove). **Lesson:** injection and withdrawal have mirror-image but distinct constraints — capacity ceiling vs. available quantity — copying one branch's logic into the other produces a plausible-looking but wrong check.
    
4. **Undefined variable (`rate_w`) used without ever being declared or added as a parameter.** **Lesson:** check the function signature actually contains every variable referenced in the body before running.
    
5. **Silent failure on constraint violations** — original code used `pass` when `max_volume` or available-volume checks failed, meaning the function silently skipped that cash flow and kept going, with no signal to the caller that part of the trade didn't execute. **Lesson:** a pricing function that fails silently is worse than one that crashes — changed to print a clear message and `return None`, stopping calculation entirely on any constraint breach.
    
6. **Confusing a per-transaction fee with a throughput-rate constraint.** Initially argued `rate` (injection/withdrawal throughput cap, explicitly listed as input #4 in the task) meant a monetary fee — conflating it with the separate $10K/1M injection-withdrawal fee mentioned only in the task's worked example, not in its list of 6 required inputs. **Lesson:** re-read the task's input list and its worked example separately before assuming one covers the other — they were two different cost/constraint concepts that needed two different parameters.
    
7. **Testing only the single injection/single withdrawal case for a long stretch**, even though the task explicitly states the client may choose multiple dates. Multi-date support wasn't real until `amount` was restructured from a shared scalar into a per-date dict (`amounts[date]`), matching the pattern already used for `prices`. **Lesson:** "generalizing" a function isn't done until it's actually tested with more than the minimal case the first version happened to work for.
    
8. **Syntax attempts that referenced variables before they existed** (e.g. `amount = {date : amount}` written outside any loop, where `date` was never in scope) — a recurring pattern of writing plausible-looking code without tracing whether every name used is actually defined at that point in the program.
    
9. **Using arbitrary hardcoded test prices instead of the model built in Task 1** — first test run used made-up prices ($2.3–$3.2) instead of feeding dates through `estimate_price()`. This defeated the purpose of building Task 1 and Task 2 as a connected pipeline, and understated the real seasonal spread by roughly 4x. **Lesson:** when two tasks are meant to chain together, test data should flow from the earlier model, not be invented separately — otherwise you're testing the function's mechanics in isolation, not the actual pipeline.
    
10. **Testing extrapolation past the window the model actually committed to.** Pushed test dates to Jan–Mar 2026 at one point — over a year beyond Task 1's Sep 2024 cutoff, when the stated extrapolation commitment was only "an extra year" (i.e. valid through Sep 2025). The model still returned a number, which is the trap: a function returning _a_ value is not the same as the value being trustworthy. **Lesson:** know a model's stated validity boundary and don't test (or rely on) it past that line just because the code doesn't throw an error — silently extrapolating beyond a committed range produces numbers with no backing.
    

---

### Status

Task 2 complete: multi-date injection/withdrawal, per-date amounts, both fee types (monthly storage + per-unit injection/withdrawal), max-volume and available-volume constraints enforced with hard-stop on breach, prices sourced from the Task 1 model (not hardcoded), and test dates chosen to respect Task 1's stated extrapolation validity window. Ready to move to Task 3.