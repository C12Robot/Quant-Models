import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path(__file__).resolve().parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

TICKERS = ["SPY", "EFA", "VNQ", "GSG", "TLT"]
SMA_MONTHS = 10

data = yf.download(TICKERS, period="max", auto_adjust=True)["Close"]
data = data[TICKERS].dropna()  

monthly_price = data.resample("ME").last()
today = pd.Timestamp.today()
if monthly_price.index[-1] > today - pd.offsets.MonthEnd(1):
    monthly_price = monthly_price.iloc[:-1]
sma = monthly_price.rolling(SMA_MONTHS).mean().dropna()
monthly_price = monthly_price.loc[sma.index]
monthly_returns = monthly_price.pct_change().dropna()


# Fix 3: real T-bill rate. ^IRX = 13-week T-bill discount yield in percent (annualised).
irx = yf.download("^IRX", period="max", auto_adjust=True)["Close"]
tbill_monthly = (irx.resample("ME").last() / 100 / 12).squeeze()
tbill_monthly = tbill_monthly.reindex(monthly_returns.index).ffill()

# ---------------- signals & returns ----------------
signal = (monthly_price > sma).astype(int)
signal_shifted = signal.shift(1).dropna()  # trade next month on this month's signal (no lookahead)
returns_aligned = monthly_returns.loc[signal_shifted.index]
tbill_aligned = tbill_monthly.loc[signal_shifted.index]

# long the asset when signal=1, earn T-bill when signal=0
strategy_returns = (
    signal_shifted * returns_aligned
    + (1 - signal_shifted).mul(tbill_aligned, axis=0)
)
strategy = strategy_returns.mean(axis=1)          # equal weight across 5 sleeves
benchmark = monthly_returns.mean(axis=1).loc[strategy.index]  # equal-weight B&H, same sample

strategy_curve = (1 + strategy).cumprod()
benchmark_curve = (1 + benchmark).cumprod()

# ---------------- metrics ----------------
def get_metrics(returns: pd.Series, curve: pd.Series, tbill: pd.Series) -> dict:
    n_months = len(returns)
    cagr = curve.iloc[-1] ** (12 / n_months) - 1          # Fix 1: from the CURVE
    excess = returns - tbill.loc[returns.index]
    sharpe = excess.mean() / excess.std() * np.sqrt(12)
    vol = returns.std() * np.sqrt(12)
    dd = (curve - curve.cummax()) / curve.cummax()
    annual = returns.resample("YE").apply(lambda x: (1 + x).prod() - 1)
    return {
        "CAGR": cagr,
        "Sharpe": sharpe,
        "Volatility": vol,
        "Max Drawdown": dd.min(),
        "Worst Year": annual.min(),
    }

summary = pd.DataFrame(
    {
        "Strategy": get_metrics(strategy, strategy_curve, tbill_monthly),
        "Buy & Hold": get_metrics(benchmark, benchmark_curve, tbill_monthly),
    }
)
print(summary.round(4))
print(f"\nSample: {strategy.index[0].date()} to {strategy.index[-1].date()}"
      f" ({len(strategy)} months)")

# ---------------- exports (Fix 5) ----------------
pd.DataFrame({"strategy": strategy, "buy_hold": benchmark}).to_csv(
    RESULTS_DIR / "monthly_returns.csv"
)
summary.to_csv(RESULTS_DIR / "summary.csv")

fig, ax = plt.subplots(figsize=(10, 6))
strategy_curve.plot(ax=ax, color="red", label="GTAA Strategy")
benchmark_curve.plot(ax=ax, color="orange", label="Equal-Weight Buy & Hold")
ax.axhline(y=1, color="green", linestyle="--", linewidth=0.8)
ax.set_ylabel("Growth of $1")
ax.set_xlabel("")
ax.set_title("Faber GTAA vs Buy & Hold")
ax.legend()
fig.tight_layout()
fig.savefig(RESULTS_DIR / "equity_curves.png", dpi=150)
plt.show()