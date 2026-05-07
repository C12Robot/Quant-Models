

## The Logic — Step by Step

### Step 1 — Detect Trade Entries and Exits

```python
trades = nifty['Signal'].diff().fillna(0)
entry_days = nifty[trades == 1].index
exit_days = nifty[trades == -1].index
```

- `Signal` column contains `1` (in position) or `0` (out of position)
- `.diff()` detects **changes** in signal → `+1` means signal flipped from 0→1 (entry), `-1` means 1→0 (exit)
- `entry_days` and `exit_days` store the exact dates of each trade

> [!NOTE] Why `.diff()`? The signal column tells you _what position you're in_, not _when you entered_. `.diff()` gives you the transitions — which is when the actual trade happens.

---

### Step 2 — Loop Through Each Trade

```python
n_trades = min(len(entry_days), len(exit_days))

for i in range(n_trades):
    entry = entry_days[i]
    exit = exit_days[i]
    trade_return = (nifty.loc[exit, 'Close'] / nifty.loc[entry, 'Close']) - 1
```

- `min(...)` prevents index errors if the last trade is still open (no exit yet)
- `trade_return` = percentage gain/loss on that specific trade
- Formula: `(Exit Price / Entry Price) - 1`

> [!WARNING] Assumption This pairs entries and exits in order (1st entry → 1st exit, 2nd entry → 2nd exit). Works correctly only if signals don't overlap — which they shouldn't in a long-only strategy.

---

### Step 3 — Separate Wins from Losses

```python
    if trade_return > 0:
        wins += 1
        wins_list.append(trade_return)
    else:
        losses_list.append(trade_return)
```

- Positive return → Win → goes into `wins_list`
- Zero or negative → Loss → goes into `losses_list`
- Breakeven trades (return = 0) are counted as losses here

---

### Step 4 — Calculate All Metrics

```python
avg_win_size = np.mean(wins_list) * 100
avg_loss_size = np.mean(losses_list) * 100
RR = avg_win_size / abs(avg_loss_size)
win_rate = (wins / n_trades) * 100 if n_trades > 0 else 0
```

|Metric|Formula|What It Tells You|
|---|---|---|
|**Win Rate**|`wins / n_trades × 100`|% of trades that were profitable|
|**Avg Win Size**|`mean(wins_list) × 100`|Average gain per winning trade (%)|
|**Avg Loss Size**|`mean(losses_list) × 100`|Average loss per losing trade (%)|
|**Risk/Reward (RR)**|`avg_win / abs(avg_loss)`|How much you make vs lose per trade|

---

## Output

```python
print(f"Total Trades: {n_trades}")
print(f"Win rate: {win_rate:.2f}%")
print(f"Avg Win Size: {avg_win_size:.2f}%")
print(f"Avg Loss Size: {avg_loss_size:.2f}%")
print(f"RR : {RR:.2f}")
```

---

## How to Read These Numbers

> [!TIP] The Expectancy Formula A strategy is profitable in the long run if: `(Win Rate × Avg Win) > (Loss Rate × Avg Loss)`
> 
> Example: 40% win rate with RR of 2.5 is **better** than 60% win rate with RR of 0.8

|RR|Win Rate Needed to Break Even|
|---|---|
|1.0|50%|
|1.5|40%|
|2.0|33%|
|3.0|25%|

---

## What to Watch Out For

> [!WARNING] Common Issues
> 
> - **Low n_trades** — if total trades < 30, the stats aren't statistically reliable
> - **Survivorship bias** — this only works on historical data; future signals may not match
> - **Slippage not accounted for** — real trades have spread + impact costs; the actual returns will be slightly lower
> - **avg_loss_size near 0** — if losses are tiny, RR inflates artificially; always sanity check both numbers

---

