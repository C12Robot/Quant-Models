import pandas as pd 
import yfinance as yf
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np 
import datetime
from dotenv import load_dotenv
import os 
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

load_dotenv()
client = StockHistoricalDataClient(
    api_key=os.getenv("ALPACA_KEY"),
    secret_key=os.getenv("ALPACA_SECRET_KEY")
)

request = StockBarsRequest(
    symbol_or_symbols="SPY",
    timeframe=TimeFrame(5, TimeFrameUnit.Minute),
    start="2018-01-01",
    end="2026-01-01"
)

data = client.get_stock_bars(request).df
data = data.reset_index(level='symbol', drop=True)
data.index = data.index.tz_convert("America/New_York")
data.columns = [col.capitalize() for col in data.columns]


orb_candles = (data.index.time >= datetime.time(9,30)) & (data.index.time < datetime.time(9,45))
orb_data = data[orb_candles]
orb_High = orb_data.groupby(orb_data.index.date)['High'].max()
orb_Low = orb_data.groupby(orb_data.index.date)['Low'].min()
orb_Zone = pd.DataFrame({'High' : orb_High, 'Low' : orb_Low})

orb_trade_candles = (data.index.time >= datetime.time(9,45))
orb_trade_data = data[orb_trade_candles]


trade_data = data[orb_trade_candles].copy()
trade_data['date'] = trade_data.index.date
trade_data = pd.merge(trade_data, orb_Zone, left_on='date', right_index=True)
trade_data = trade_data.rename(columns={'High_y':'orb_high', 'Low_y':'orb_low'})

trade_data['long_signal'] = (trade_data['Close'] > trade_data['orb_high']) & (trade_data['Close'].shift(1) <= trade_data['orb_high'])
trade_data['short_signal'] = (trade_data['Close'] < trade_data['orb_low']) & (trade_data['Close'].shift(1) >= trade_data['orb_low'])

def ORB_backtest(day_data, trades_per_day):
    results = []
    signals = day_data[(day_data['long_signal']) | (day_data['short_signal'])]

    for idx, row in signals.iterrows():
        date = idx.date()
        if trades_per_day.get(date, 0) >= 3:
            continue

        is_long = row['long_signal']
        entry_price = row['Close']
        tp = entry_price + 2 if is_long else entry_price - 2
        sl = entry_price - 1 if is_long else entry_price + 1

        future = day_data[day_data.index > idx]
        if future.empty:
            continue

        tp_hit = future['High_x'] >= tp if is_long else future['Low_x'] <= tp
        sl_hit = future['Low_x'] <= sl if is_long else future['High_x'] >= sl

        hit = tp_hit | sl_hit
        if not hit.any():
            last_price = future['Close'].iloc[-1]
            pnl = (last_price - entry_price) if is_long else (entry_price - last_price)
            results.append({'entry_time': idx, 'entry_price': entry_price, 'exit_price': last_price, 'result': 'expired', 'pnl': pnl})
            trades_per_day[date] = trades_per_day.get(date, 0) + 1
            continue

        first_hit_idx = hit.idxmax()

        if tp_hit.loc[first_hit_idx]:
            exit_price = tp
            result = 'win'
            pnl = 5
        else:
            exit_price = sl
            result = 'loss'
            pnl = -2

        results.append({'entry_time': idx, 'entry_price': entry_price, 'exit_price': exit_price, 'result': result, 'pnl': pnl})
        trades_per_day[date] = trades_per_day.get(date, 0) + 1

    return results

trades_per_day ={}
all_results = []

for date, day_data in trade_data.groupby('date'):
    day_results = ORB_backtest(day_data, trades_per_day)
    all_results.extend(day_results)

trades_df = pd.DataFrame(all_results)

vix = yf.download("^VIX", start="2018-01-01", end="2026-01-01", interval="1d")
vix.columns = vix.columns.droplevel(1)
vix.index = vix.index.tz_localize("America/New_York")
vix.index = vix.index.date

trades_df['date'] = pd.to_datetime(trades_df['entry_time']).dt.date
all_trade_vix = pd.merge(trades_df, vix[['Close']], left_on='date', right_index=True)
all_trade_vix = all_trade_vix.rename(columns={'Close' : 'vix'})
print(f"all trades vix: {len(all_trade_vix)}")
high_vix = all_trade_vix[all_trade_vix['vix'] >= 20]
low_vix = all_trade_vix[all_trade_vix['vix'] < 20]

#print(f"Total Trades high vix: {len(high_vix)}")
#print(f"Total pnl: {high_vix['pnl'].sum()}")
#print(f"Win Rate : {(high_vix['result'] == 'win').sum() / len(high_vix) * 100:.2f}%")
#print(high_vix['result'].value_counts())

#print(f"Total Trades low vix: {len(low_vix)}")
#print(f"Total pnl: {low_vix['pnl'].sum()}")
#print(f"Win Rate : {(low_vix['result'] == 'win').sum() / len(low_vix) * 100:.2f}%")
#print(low_vix['result'].value_counts())

all_trade_vix = all_trade_vix.sort_values('entry_time')
all_trade_vix['cumulative_pnl'] = all_trade_vix['pnl'].cumsum()

daily_pnl = all_trade_vix.groupby('date')['pnl'].sum()
sharpe = (daily_pnl.mean() / daily_pnl.std()) * np.sqrt(252)

rolling_max = all_trade_vix['cumulative_pnl'].cummax()
drawdown = all_trade_vix['cumulative_pnl'] - rolling_max
max_drawdown = drawdown.min()

#print(f"Total Trades: {len(all_trade_vix)}")
#print(f"Win Rate: {(all_trade_vix['result'] == 'win').sum() / len(all_trade_vix) * 100:.1f}%")
#print(f"Total PnL: ${all_trade_vix['pnl'].sum():.2f}")
#print(f"Sharpe Ratio: {sharpe:.2f}")
#print(f"Max Drawdown: ${max_drawdown:.2f}")
#print(f"Avg Win: ${all_trade_vix[all_trade_vix['result'] == 'win']['pnl'].mean():.2f}")
#print(f"Avg Loss: ${all_trade_vix[all_trade_vix['result'] == 'loss']['pnl'].mean():.2f}")

pnl_values = np.array(all_trade_vix['pnl'])
scenarios = []
for i in range(1000):
    original = pnl_values.copy()
    np.random.shuffle(original)
    cumulative = np.cumsum(original)
    max_dd = (cumulative - np.maximum.accumulate(cumulative)).min()
    scenarios.append(max_dd)

print(f"Median drawdown: ${np.median(scenarios):.2f}")
print(f"Worst 5% drawdown: ${np.percentile(scenarios, 5):.2f}")
print(f"Best 5% drawdown: ${np.percentile(scenarios, 95):.2f}")

cutoff = pd.Timestamp('2024-06-01', tz='America/New_York')
in_sample = all_trade_vix[all_trade_vix['entry_time'] <= cutoff]
out_sample = all_trade_vix[all_trade_vix['entry_time'] > cutoff]

for name, df in [('In-Sample', in_sample), ('Out-Sample', out_sample)]:
    daily = df.groupby('date')['pnl'].sum()
    sharpe_forward = (daily.mean() / daily.std()) * np.sqrt(252)
    print(f"\n{name}")
    print(f"Trades: {len(df)}")
    print(f"Win Rate: {(df['result'] == 'win').sum() / len(df) * 100:.1f}%")
    print(f"Total PnL: ${df['pnl'].sum():.2f}")
    print(f"Sharpe: {sharpe_forward:.2f}")

plt.figure(figsize=(10, 5))
plt.hist(scenarios, bins=50, color='red', alpha=0.7)
plt.axvline(max_drawdown, color='black', linestyle='--', label=f'Actual: ${max_drawdown:.2f}')
plt.axvline(np.percentile(scenarios, 5), color='orange', linestyle='--', label=f'Worst 5%: ${np.percentile(scenarios, 5):.2f}')
plt.title('Monte Carlo Max Drawdown Distribution (1000 scenarios)')
plt.xlabel('Max Drawdown ($)')
plt.ylabel('Frequency')
plt.legend()
#plt.show()


plt.figure(figsize=(12,5))
plt.plot(all_trade_vix['entry_time'], all_trade_vix['cumulative_pnl'])
plt.title('ORB Strategy Equity Curve')
plt.xlabel('Date')
plt.ylabel('Cumulative PNL')
plt.grid(True)
plt.show()

