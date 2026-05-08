import pandas as pd 
import numpy as np 
import yfinance as yf 
import matplotlib.pyplot as plt 
import seaborn as sns
import calendar

ticker = ["^NSEI", "GC=F", "BTC-USD"]
Data_1 = yf.download(ticker, period="2y")['Close']
Data_1.columns = ['Nifty', 'Gold', 'Bitcoin'] 
Data_1 = Data_1.ffill()
returns = Data_1.pct_change().dropna()

Data_weekly = returns.resample('W').last()
for col in Data_weekly.columns:
    print(f"{col} Best week: {Data_weekly[col].idxmax().strftime('%B %Y')} -> {(Data_weekly[col].max()*100):.2f}%")
    print(f"{col} Worst week: {Data_weekly[col].idxmin().strftime('%B %Y')} -> {(Data_weekly[col].min()*100):.2f}%")

#part 2 

risk_free_return = 0.065/252
excess_return = returns - risk_free_return
sharpe_ratio = excess_return.rolling(20).mean() / excess_return.rolling(20).std() * np.sqrt(252)
for col in returns.columns:
    print(f"{col} Sharpe Ratio: {sharpe_ratio[col].mean():.2f}")

returns_rolling = returns['Nifty'].rolling(30).corr(returns['Gold'])
plt.plot(returns_rolling)
plt.title('30-Day Rolling Correlation: Nifty vs Gold')
plt.axhline(y=0, color='red', linestyle='--')
plt.ylabel('Correlation')
plt.show()

sharpe_ratio.plot(figsize=(12,5), title='20-day rolling sharpe ratio')
plt.axhline(y=0, color='red', linestyle='--')
plt.ylabel('Sharpe Ratio')
#plt.show()

damn = (1 + returns).cumprod()
drawdown = (damn - damn.cummax()) / damn.cummax()
max_drawdown = drawdown.min()
for col in drawdown.columns:
    print(f"{col} Max Drawdown: {drawdown[col].idxmin().strftime('%B %Y')} -> {(max_drawdown[col])*100:.2f}%")

drawdown.plot(figsize=(12,5), title='Drawdown Curve')
plt.axhline(y=0, color='red', linestyle='--')
plt.ylabel('Drawdown')
#plt.show()

Avg_Return = returns.groupby(returns.index.month).mean()
month_names = [calendar.month_abbr[m] for m in Avg_Return.index]

Avg_Return.index = month_names
Avg_Return.plot(kind='bar', figsize=(12,5))
plt.tight_layout()
#plt.show()

Total_Return = (Data_1.ffill().iloc[-1]/Data_1.ffill().iloc[0])-1
Annualised_vol = returns.std()* np.sqrt(252)
trading_days = len(returns)
A_return = Total_Return * (252/trading_days)
Sharpe_New = (A_return - 0.065) / Annualised_vol

Final = pd.DataFrame({'Total Return':Total_Return, 'Annualised Volume':Annualised_vol, 'Sharpe Ratio':Sharpe_New, 'Max Drawdown': max_drawdown})
print(Final.head())
