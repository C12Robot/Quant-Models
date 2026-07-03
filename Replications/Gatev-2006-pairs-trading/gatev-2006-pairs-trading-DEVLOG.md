# DEVLOG — gatev-2006-pairs-trading

> Session 1 was logged as it happened. Later phases (rolling loop, VIX filter, final results) were built before I adopted a consistent DEVLOG habit — those entries are retrospective, reconstructed 2026-07-03, and thinner than they should be.

---

## Session 1 — Single window (formation + trading)

### What was built

Phase 1–2 of the plan: data download, pair formation, and trading logic for one 12-month formation (2000-01 → 2001-01) + 6-month trading (2001-01 → 2001-06) window.

- Universe: 50 hardcoded liquid US large caps (see decision below)
- Data: yfinance, 2000–2025, auto_adjust=True, Close prices
- Normalization: `prices / prices.iloc[0]` — all series start at 1.0
- Pair formation: `itertools.combinations` → 1,225 candidate pairs; distance = sum of squared deviations of normalized prices over formation window; pairs with <100 overlapping days skipped; top 20 by minimum distance selected
- Spread SD estimated on the formation window (per Gatev — thresholds fixed before trading)
- Trading: enter when spread breaks ±2 SD (short outperformer / long underperformer), exit when spread crosses zero; open positions effectively close at window end
- Returns: `positions × (return_A − return_B)`, compounded per pair, averaged across 20 pairs

### Key decisions

- **Hardcoded 50-ticker universe.** Wikipedia S&P 500 scrape via `pd.read_html` returned 403; `requests` with a User-Agent fetched the HTML but html5lib parsing broke on Python 3.14. Hardcoded 50 liquid names to unblock. Known cost: survivor-only, tech-heavy universe — the opposite of Gatev's utility-heavy CRSP top pairs. This decision is the root of the final divergence (see README).
- **Minimum 100 overlapping days per pair** before computing distance — avoids ranking pairs on thin data.

### Bugs hit and fixes

1. **`position == 0` written where `position = 0` was needed** in the exit branch — comparison instead of assignment, so positions never reset and all returns came out 0.0. Silent bug; found by inspecting per-pair outputs.
2. **`lower = 2 * std` missing the negative sign** — lower entry band was positive, long entries impossible to trigger correctly.
3. **NaN poisoning in distance calc** — without `.dropna()`, NaN subtraction propagated and `.sum()` over NaNs returned 0, making broken pairs look like perfect pairs (distance 0). Fixed by dropping rows where either stock has NaN first.
4. **`pairs.append(a, b, dist, std)` TypeError** — `list.append` takes one argument; wrapped in a tuple.
5. **`normalized['stock_a']` vs `normalized[stock_a]`** — quoted string looks for a column literally named "stock_a"; KeyError took a while to trace.
6. **`sort()` vs `sort_values()`** — `.sort()` no longer exists on DataFrames.

### Learned

- `itertools.combinations(tickers, 2)` for exhaustive pair generation
- `_` convention for throwaway loop variables in `iterrows()`
- Formation-period SD as the fixed threshold is what keeps the rule out-of-sample honest

### Session 1 result

Single window (trading Jan–Jun 2001, dotcom crash period): average return across top 20 pairs = **−10.38%**. Several pairs never triggered (0.0 return) — consistent with the committed-vs-employed capital distinction in the paper.

---

## Retrospective — rolling loop, VIX filter, final results (reconstructed 2026-07-03)

### What was built

- Rolling structure via `dateutil.relativedelta`: 12m formation + 6m trading, rolled forward 1 month per iteration across 2000–2025; per-window average pair returns collected into a return series
- VIX regime filter variant: skip windows where VIX at trading start < 20
- Performance stats: annualised return and Sharpe on the window return series

### Final results

|Variant|Annualised return|Sharpe|
|---|---|---|
|Base (no filter)|−4.62%|−0.74|
|VIX ≥ 20 filter|−3.95%|−0.55|

### Why negative vs Gatev's +11% (diagnosis)

- **Universe:** 50 survivor-only, tech-heavy tickers vs Gatev's ~5,000-stock survivorship-bias-free CRSP universe including delisted stocks
- **Search space:** 1,225 candidate pairs vs ~12.5M — four orders of magnitude less selection power; Gatev's edge lives in the extreme tail of pair quality
- **Sector mix:** 71% of Gatev's top-20 pairs were utilities; my universe has almost none
- yfinance cannot provide delisted tickers, so this is not fixable with free data

### Open items

- [ ] **Verify normalization scope in the rolling loop.** Session 1 normalized once globally (`prices.iloc[0]` of the full dataset). Gatev renormalizes within each formation window. If the rolling loop kept global normalization, distances and SD thresholds in later windows are scale-distorted and final results are affected. Confirm which the code does; fix and rerun if global. **Blocking for README numbers.**
- [ ] Undocumented sessions: bugs hit during the rolling-loop and VIX-filter builds were not logged and are unrecoverable. Lesson applied going forward: log same-day.
- Utility-universe rerun (add NEE, SO, DUK, AEP, EXC, SRE, D, PCG, ED, WEC): diagnostic only — would not close the search-space gap. WONTFIX unless revisiting the project.

### Status: PARKED (2026-07-03)

Parked by priority, not blocked by effort. Methodology fully implemented; results diverge for documented data reasons. Revisit condition: access to a survivorship-bias-free universe (CRSP/WRDS via university access, or a historical S&P 500 constituents list as a partial fix).