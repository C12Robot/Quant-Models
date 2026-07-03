
import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from itertools import combinations
from dateutil.relativedelta import relativedelta
from datetime import date
from pathlib import Path

# ---------------- config ----------------
USE_VIX_FILTER = False      # False = base variant, True = skip windows with VIX < 20
VIX_THRESHOLD = 20
TOP_N_PAIRS = 20
MIN_OVERLAP_DAYS = 100
START = date(2000, 1, 1)
END = date(2026, 7, 1)

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

TICKERS = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B',
    'JPM', 'JNJ', 'V', 'PG', 'UNH', 'HD', 'MA', 'DIS', 'BAC', 'XOM',
    'PFE', 'KO', 'PEP', 'ABBV', 'AVGO', 'COST', 'TMO', 'MRK', 'ACN',
    'WMT', 'CVX', 'ABT', 'MCD', 'NEE', 'LIN', 'DHR', 'TXN', 'PM',
    'CRM', 'QCOM', 'AMD', 'HON', 'LOW', 'UPS', 'CAT', 'GS', 'MS',
    'BLK', 'SPGI', 'AXP', 'RTX', 'DE'
]

# ---------------- data ----------------
data = yf.download(TICKERS, start=str(START), end=str(END), auto_adjust=True)
prices = data["Close"][TICKERS]          # select by name, never positionally

vix = yf.download("^VIX", start=str(START), end=str(END), auto_adjust=True)["Close"]
vix = vix.squeeze()

LAST_DATE = prices.index[-1].date()

# ---------------- one window ----------------
def run_window(formation_start: date) -> float | None:
    """Form pairs on 12m, trade 6m. Returns average pair return, or None if skipped."""
    formation_end = formation_start + relativedelta(months=12)
    trading_start = formation_end
    trading_end = formation_end + relativedelta(months=6)

    # Fix 1: normalize within the window. One base — the formation window's first
    # row — shared by formation and trading prices, so the formation-period SD and
    # the trading-period spread live on the same scale. Tickers not yet trading at
    # the base date become NaN and drop out via the overlap check.
    window_prices = prices.loc[str(formation_start):str(trading_end)]
    if window_prices.empty:
        return None
    base = window_prices.iloc[0]
    normalized = window_prices / base

    formation_data = normalized.loc[str(formation_start):str(formation_end)]
    trading_data = normalized.loc[str(trading_start):str(trading_end)]

    if USE_VIX_FILTER:
        try:
            vix_at_start = vix.loc[str(trading_start):].iloc[0]
        except IndexError:
            return None
        if vix_at_start < VIX_THRESHOLD:
            return None

    # ---- formation: rank pairs by SSD ----
    pairs = []
    for a, b in combinations(TICKERS, 2):
        pair_data = formation_data[[a, b]].dropna()
        if len(pair_data) < MIN_OVERLAP_DAYS:
            continue
        spread = pair_data[a] - pair_data[b]
        pairs.append((a, b, (spread ** 2).sum(), spread.std()))

    if not pairs:
        return None
    pairs_df = (
        pd.DataFrame(pairs, columns=["a", "b", "distance", "std"])
        .sort_values("distance")
        .head(TOP_N_PAIRS)
    )

    # ---- trading ----
    pair_returns_list = []
    for _, row in pairs_df.iterrows():
        a, b, std = row["a"], row["b"], row["std"]
        spread = trading_data[a] - trading_data[b]

        positions = []
        position = 0
        for value in spread:
            if position == 0:
                if value > 2 * std:
                    position = -1        # short a, long b
                elif value < -2 * std:
                    position = 1         # long a, short b
            elif position == 1 and value >= 0:
                position = 0
            elif position == -1 and value <= 0:
                position = 0
            positions.append(position)

        positions = pd.Series(positions, index=spread.index)
        # Fix 2: signal on day t trades from day t+1 — no same-day lookahead.
        positions = positions.shift(1).fillna(0)

        daily_ret = trading_data[[a, b]].pct_change()
        pair_ret = positions * (daily_ret[a] - daily_ret[b])
        pair_returns_list.append((1 + pair_ret.fillna(0)).prod() - 1)

    return float(np.mean(pair_returns_list))

# ---------------- rolling loop ----------------
windows = []
current = START
while current + relativedelta(months=18) <= LAST_DATE:   # full 12m+6m must fit
    avg = run_window(current)
    if avg is not None:
        windows.append((str(current + relativedelta(months=12)), avg))
    current += relativedelta(months=1)

results = pd.DataFrame(windows, columns=["trading_start", "avg_return"])
results.set_index("trading_start", inplace=True)

# ---------------- stats ----------------
mean_6m = results["avg_return"].mean()
annualised = (1 + mean_6m) ** 2 - 1
sharpe = mean_6m / results["avg_return"].std() * np.sqrt(2)   # see caveat in docstring
cumulative = (1 + results["avg_return"]).cumprod()

variant = "vix_filtered" if USE_VIX_FILTER else "base"
print(f"Variant: {variant} | windows run: {len(results)}")
print(f"Annualised Return: {annualised:.4%}")
print(f"Sharpe (overlapping-window, inflated): {sharpe:.4f}")
print(f"Final Cumulative: {cumulative.iloc[-1]:.4f}")

# ---------------- exports ----------------
results.to_csv(RESULTS_DIR / f"window_returns_{variant}.csv")
pd.DataFrame(
    {"annualised_return": [annualised], "sharpe": [sharpe],
     "windows": [len(results)], "variant": [variant]}
).to_csv(RESULTS_DIR / f"summary_{variant}.csv", index=False)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8))
results["avg_return"].plot(ax=ax1)
ax1.axhline(0, color="red", linestyle="--")
ax1.set_title(f"Rolling 6-Month Window Returns ({variant})")
cumulative.plot(ax=ax2, color="green")
ax2.axhline(1, color="red", linestyle="--")
ax2.set_title("Cumulative Return")
fig.tight_layout()
fig.savefig(RESULTS_DIR / f"pairs_{variant}.png", dpi=150)
plt.show()