> **Note:** This project was completed before I adopted a session-by-session DEVLOG habit. This is a single retrospective entry reconstructing the build. Future projects log as they go.

---

## Retrospective — written 2026-07-02

### What was built

Python/pandas replication of Faber's GTAA model:

- Universe: SPY, EFA, VNQ, GSG, TLT — equal weight (20% each)
- Signal: monthly close > 10-month SMA → long; below → cash
- Cash rate: assumed flat 4% annual (0.04/12 monthly) instead of actual T-bill series
- Rebalance: monthly, month-end close
- Signals shifted by 1 month to avoid lookahead bias
- Benchmark: equal-weight buy & hold of the same 5 assets
- Metrics: CAGR, Sharpe, annualised vol, max drawdown, worst year
- Data: yfinance, `period="max"`, effective sample ~2006–2025 (limited by GSG inception after dropna)

### Key decisions

- **Flat 4% cash rate instead of real T-bill data.** Simplification; overstates/understates cash return depending on era. Acceptable for a first pass, should be replaced with ^IRX or BIL total return in a revisit.
- **dropna() on the joined price panel** — sample starts where the youngest ETF (GSG, 2006) begins. This means my sample (2006–2025) differs from Faber's (1973–2012), so results are comparable in character, not in numbers.
- **Signal computed on price vs SMA of prices**, not total-return index vs its SMA. Faber uses total return series; my Close prices via auto-adjust approximate this but it's not identical.

### Bugs hit and fixes

1. **B&H CAGR computed from a single return, not the equity curve.** `CAGR_bh = (Buy_Hold_return.iloc[-1])**(12/n_months) - 1` raised the _last monthly return_ to a power instead of using `Buy_Hold_return_curve.iloc[-1]`. Produced a nonsense −23.5% CAGR that initially went into my results table. Fix: use the cumulative curve. **Lesson: sanity-check outputs against intuition — equal-weight B&H over 19 years cannot be −23.5% annualised.**
2. **Sharpe formula bracketing.** First version computed `mean / (std * sqrt(12))` instead of `(mean/std) * sqrt(12)` — annualisation multiplied the wrong term.
3. **Duplicated metrics code** for strategy vs benchmark drifted out of sync — this is how bug (1) survived. Refactored into a single `get_metrics(returns, curve)` function applied to both.

### Open items / known limitations

- [ ] **Rerun and regenerate results table with fixed CAGR_bh** — table in earlier drafts used the buggy number. README must use post-fix numbers only.
- [x] **Fragile column renaming:** `data.columns = ['EFA','GSG','SPY','TLT','VNQ']` assumes yfinance returns tickers alphabetically. If ordering changes, every series is silently mislabeled. Fix: select by ticker name, never positionally.
- [x] Replace flat 4% cash assumption with actual T-bill series.
- [x] Export results/monthly_returns.csv and results/summary.csv (currently print-only).

### Observations from the backtest

- 2008: strategy moved to cash before the collapse; drawdown stayed single-digit while B&H lost ~46%.
- 2020 COVID: shallower dip, faster recovery.
- 2022–2025 bull run: strategy lags — consistent with Faber's note that timing underperforms in strong uptrends.
- GSG is a persistent drag on untimed equal-weight B&H since 2006; timing's edge partly comes from sidestepping commodity drawdowns.

### Divergence from paper

Sample period (2006–2025 vs 1973–2012), instruments (ETFs vs indices), and cash assumption differ — direction of results matches Faber (lower vol, lower drawdown, competitive compound return), magnitudes are not directly comparable.