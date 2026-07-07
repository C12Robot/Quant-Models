import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt 
import datetime


data = pd.read_csv(r"C:\Users\meena\Documents\testing\Nat_Gas.csv")
data['Dates'] = pd.to_datetime(data['Dates'])
data = data.set_index('Dates')

t = (data.index - data.index[0]).days /30.44
X = np.column_stack([t, np.sin(2*np.pi*t/12), np.cos(2*np.pi*t/12), np.ones(len(t))])
coeffcients, *_ = np.linalg.lstsq(X, data['Prices'].values, rcond=None)

results = []
def estimate_price(date):
    date = pd.to_datetime(date)
    t_new = (date - data.index[0]).days / 30.44
    price = coeffcients[0]*t_new + coeffcients[1]*np.sin(2*np.pi*t_new/12) + coeffcients[2]*np.cos(2*np.pi*t_new/12) + coeffcients[3]
    return price
    
test_dates = ['2021-06-30', '2025-06-30']
results = [estimate_price(d) for d in test_dates]

print(data.loc['2024-01-31'])
print(estimate_price('2024-01-31'))

plt.figure(figsize=(10,5))
plt.plot(data.index, data['Prices'], label='Actual')

future_dates = pd.date_range(data.index[0], data.index[-1] + pd.DateOffset(years=1), freq='D')
fitted = [estimate_price(d) for d in future_dates]
plt.plot(future_dates, fitted, label='Fitted + Extrapolated', linestyle='--')
plt.legend()
plt.show()
