# Gatev, Goetzmann & Rouwenhorst (2006) — Pairs Trading: Performance of a Relative Value Arbitrage Rule

**Authors:** Evan Gatev (Boston College), William Goetzmann & K. Geert Rouwenhorst (Yale) **Year:** 2006 (first draft 1998) **Data:** CRSP daily stock data, 1962–2002 **Link:** https://ssrn.com/abstract=141615

> My replication, its results, and why they diverge from the paper live in this folder's README.

---

## What it's about

Find two stocks whose prices historically move together. When the spread widens, short the winner and buy the loser; if history repeats, prices converge and the arbitrageur profits. Gatev tests this on 40 years of US data: the top 20 pairs earned ~11% annualised excess return — market-neutral, surviving transaction costs, holding up out-of-sample.

The deeper question: should this be possible in an efficient market? Their answer — the profit is compensation for enforcing the Law of One Price.

The paper doesn't just show pairs trading works; it proves the profits are **not** explained by simple mean reversion, bankruptcy risk, bid-ask bounce, or short-selling costs. Robustness is the contribution.

---

## Key ideas

### Law of One Price (LOP)

Two assets with identical payoffs in every state should have identical prices. Pairs trading is a near-LOP bet: the stocks aren't identical but are close substitutes, so their prices should move together — when they don't, bet on reversion.

### Cointegrated prices

The theoretical justification. If two stocks share common non-stationary factors (industry, macro exposure), each price is a random walk but the _spread_ is mean-reverting:

`p_it = Σ β_il · p_lt + ε_it` — the error term ε reverts to zero, so divergences are temporary.

### Data-snooping discipline

> "The danger in data-snooping refinements outweighs the potential insights gained."

The 2-standard-deviation entry was defined _before_ seeing results and tested once. Same principle as Faber: fix the rule first, or you're fitting noise.

### Why do prices diverge at all?

1. **Liquidity shocks / limits of arbitrage (Shleifer–Vishny):** arbitrageurs hit margin calls or capital constraints and are forced to unwind before mispricings correct — their forced selling _creates_ divergence.
2. **Bid-ask bounce:** microstructure noise — the "winner" tends to sit at the ask, the "loser" at the bid, so part of the apparent divergence is just the spread.

---

## Methodology

### Pairs formation (12-month window)

1. All liquid CRSP stocks (no zero-trading days)
2. Build cumulative total-return index (dividends reinvested), normalized
3. For each stock, find the partner minimising the **sum of squared deviations** between normalized price paths
4. Rank pairs by distance — trade top 5, top 20, pairs 101–120

### Trading period (6 months)

- **Entry:** spread exceeds 2 standard deviations (SD estimated in formation period)
- **Exit:** prices cross (spread reverts through zero)
- No convergence by period end → close at last price; delisted stock → close at delisting return
- Position: long underperformer, short outperformer → market-neutral; profit comes only from spread convergence

### Rolling structure

New batch starts every month → 6 overlapping batches live at any time. Overlapping returns are handled by averaging monthly returns across active batches (the Jegadeesh–Titman method) → clean monthly series for statistics.

---

## Return calculation

Daily buy-and-hold weights within a period (no rebalancing):

```
rP,t = Σ wi,t · ri,t / Σ wi,t     where  wi,t = wi,t-1 · (1 + ri,t-1)
```

Daily returns compound into monthly returns.

|Measure|Denominator|Meaning|
|---|---|---|
|**Committed capital**|All selected pairs, traded or not|Conservative — a fund must pre-allocate|
|**Employed capital**|Only pairs that opened|Aggressive — pure strategy performance|

Report both.

---

## Results

### Top 20 pairs, 1963–2002

|Metric|No wait|1-day wait|
|---|---|---|
|Monthly excess return (fully invested)|1.44%|0.90%|
|t-statistic|11.56|9.29|
|Monthly committed-capital return|0.81%|0.52%|
|Annualised (approx)|~11%|~7%|

Out-of-sample (1999–2002) Newey–West t = 4.82 — far beyond the 2.0 threshold; the adjustment corrects for autocorrelation and heteroskedasticity.

### Diversification

More pairs → lower SD. From 5 to 20 pairs, negative months fall from 124 to 71 of 474.

### Sector breakdown (top 20, 1-day wait)

|Sector|Monthly excess return|
|---|---|
|Utilities|1.08%|
|Financials|0.78%|
|Industrials|0.61%|
|Transportation|0.58%|

**71% of top-20 pairs are utilities.** Regulated, stable cash flows, interest-rate driven → the whole sector co-moves, producing tight pairs and clean signals. This sector concentration is central to replicating the result.

---

## Transaction costs

Waiting one day after divergence drops returns by 324 bp per 6 months (top 20). With ~2 round-trips per pair per period: 324/2 = 162 bp per round-trip → ~81 bp effective spread. The delay-based measurement backs out implicit transaction costs without quote data.

Profits survive: after the 324 bp cost estimate, net profit is 113–225 bp per 6 months — still significant. The edge decays fast with hesitation; execution speed matters.

---

## Risk analysis

- Excess return ≈ 2× the equity premium at 1/2–1/3 the SD; Sharpe 4–6× the market
- Fama-French + momentum + reversal factors: risk-adjusted alpha remains 54–76 bp/month; market beta ≈ 0 (genuinely neutral); momentum exposure negative, reversal positive — but neither explains the alpha
- **Not mean reversion:** bootstrap test replaces pair stocks with random same-decile stocks → random pairs earn slightly negative returns with higher variance
- **Short leg dominates:** alpha comes mostly from shorting the outperformer; long-leg alpha ≈ 0 → rules out bankruptcy/distress-risk explanations
- **Short-selling robustness:** large-cap-only profits barely change; simulated short recalls cost only 4–13 bp

---

## Sub-period decline

|Period|Monthly return|Risk-adjusted alpha|
|---|---|---|
|1963–1988|1.18%|0.67%|
|1989–2002|0.38%|0.42%|

Raw returns fell (more competition, hedge fund AUM $4B → $137B, cheaper transacting); risk-adjusted alpha fell less. Correlation between top-20 and pairs-101–120 portfolios (0.51 pre-1989 → 0.18 after) points to a **latent common risk factor** that went relatively dormant. The paper's framing: pairs profits are compensation for bearing this unidentified risk while enforcing LOP — what the risk _is_ remains the open question.

---

## Gatev vs Faber

||Faber GTAA|Gatev pairs|
|---|---|---|
|Type|Trend following|Mean reversion|
|Positions|Long or cash|Long + short simultaneously|
|Assets|5 asset classes|Pairs of individual stocks|
|Signal|Price vs 10-month SMA|Spread vs 2 SD|
|Market exposure|Yes, when invested|Neutral|
|Holding period|Monthly|Days to weeks|

Opposite logic; both documented to work. They would perform differently in the same environment.

---

## Key terms

- **CRSP** — Center for Research in Security Prices; survivorship-bias-free US stock database (includes delisted stocks)
- **Committed / employed capital** — denominator includes all reserved pairs vs only opened pairs
- **Bid-ask bounce** — artificial zigzag between bid and ask creating fake divergence
- **Cointegration** — non-stationary series with a stationary, mean-reverting spread
- **Formation / trading period** — 12 months to select pairs / 6 months to trade them
- **Newey–West t-stat** — t-statistic corrected for autocorrelation and heteroskedasticity
- **Market neutral** — offsetting long and short → net market exposure ≈ 0