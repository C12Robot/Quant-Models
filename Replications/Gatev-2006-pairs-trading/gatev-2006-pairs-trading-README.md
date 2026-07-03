# Gatev, Goetzmann & Rouwenhorst (2006) — Pairs Trading

Independent replication of the distance-method pairs trading strategy from the original methodology; results compared against the paper's published findings, with divergence fully attributed.

**Paper:** Gatev, Goetzmann & Rouwenhorst (2006). _Pairs Trading: Performance of a Relative Value Arbitrage Rule._ Review of Financial Studies. [SSRN 141615](https://ssrn.com/abstract=141615)

**Status:** Methodology fully implemented and closed. Extended work parked pending survivorship-bias-free data (see Limitations).

---

## The paper's claim

Rank all stock pairs by the sum of squared deviations between normalized price paths over a 12-month formation window; trade the closest pairs for 6 months, entering when the spread exceeds 2 formation-period standard deviations (long the loser, short the winner) and exiting when prices cross. On CRSP data 1962–2002, the top 20 pairs earned ~11% annualised excess return — market-neutral, robust to transaction costs, and not explained by simple mean reversion.

## What I built

Python/pandas implementation of the full methodology:

- **Universe:** 50 hardcoded liquid US large caps (see Limitations for why)
- **Data:** yfinance daily closes, 2000–2026, auto-adjusted
- **Formation:** 12 months; prices normalized to the formation window's first row (formation and trading periods share one base, keeping SD thresholds on a consistent scale); pairs ranked by minimum sum of squared spread deviations via exhaustive `itertools.combinations`; top 20 selected; pairs with <100 overlapping days excluded
- **Trading:** 6 months; enter at ±2 formation-period SD, exit at spread zero-crossing; positions lagged one day to eliminate same-day lookahead
- **Rolling:** windows rolled forward monthly, 2000–2026; only windows whose full 18 months fit inside available data are run (rule fixed before running)
- **Variants:** base, and a VIX regime filter (skip windows where VIX < 20 at trading start)

## Results

|Variant|Windows|Annualised return|Sharpe*|
|---|---|---|---|
|Base|300|+1.43%|0.25|
|VIX ≥ 20 only|112|+3.80%|0.55|

*Sharpe is computed on overlapping 6-month windows rolled monthly (adjacent windows share 5 of 6 months) and is inflated relative to Gatev's non-overlapping monthly aggregation. Reported for internal comparison, not as a headline statistic.

The VIX result is conditional, not a superior strategy: it measures per-window returns _given_ a high-volatility regime, with 188 calendar windows skipped. Read as a regime observation, it confirms the paper's sub-period finding that pairs profits concentrate in volatile eras — my per-window returns spike visibly around 2008–2009, exactly where Gatev's framework predicts.

## Why +1.4% instead of the paper's ~11%

The gap is a data problem, quantified:

- **Universe:** 50 surviving, tech-heavy large caps vs Gatev's ~5,000-stock CRSP universe that is survivorship-bias-free (includes delisted stocks). yfinance cannot provide delisted tickers at any price — every stock available today is a survivor.
- **Search space:** 1,225 candidate pairs vs ~12.5 million. The strategy's edge lives in the extreme tail of pair quality; four orders of magnitude less selection power means my "top 20" pairs are far looser than his.
- **Sector mix:** 71% of Gatev's top-20 pairs were utilities — regulated, co-moving, clean-signal stocks. My universe contains almost none.
- **Era:** my sample (2000–2026) sits mostly in the post-1989 regime where the paper itself documents sharply decayed returns (0.38%/month vs 1.18% pre-1989).

Directionally, the replication behaves as the paper predicts for this data: positive but small returns, concentrated in high-volatility periods, decaying in the recent era.

An earlier version of this replication reported −4.6% annualised; the negative sign traced to two implementation bugs (global normalization distorting pair ranking across windows, and same-day signal lookahead), documented and fixed in the DEVLOG. The corrected result is positive.

## Known limitations

- Survivor-only universe (unfixable with free data; revisit condition: CRSP/WRDS access or a historical index-constituents list)
- Overlapping-window statistics (Gatev's non-overlapping monthly aggregation not implemented)
- No transaction costs; the paper estimates ~162 bp per round-trip, which at this return level would consume most of the base variant's edge
- Committed vs employed capital distinction not implemented — returns are per selected pair regardless of whether it traded

## Repository contents

```
├── README.md
├── DEVLOG.md          # session log + retrospective; bug history incl. superseded results
├── notes.md           # condensed paper notes
├── src/
│   └── pairs_backtest.py
└── results/
    ├── window_returns_base.csv
    ├── window_returns_vix_filtered.csv
    ├── summary_base.csv
    ├── summary_vix_filtered.csv
    └── pairs_base.png
```

## How to run

```bash
pip install pandas numpy yfinance matplotlib python-dateutil
python src/pairs_backtest.py
```

Set `USE_VIX_FILTER` at the top of the script to switch variants. Data downloads from Yahoo Finance at runtime; numbers drift slightly as the sample extends.