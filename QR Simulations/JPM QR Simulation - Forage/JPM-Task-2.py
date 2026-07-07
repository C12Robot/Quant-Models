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

def price_contract(injection_dates, withdrawl_dates, prices, amount, max_volume, monthly_storage_fees, injection_withdrawl_fee):
    volume_in_storage = 0
    total_value = 0
    events = [(d, 'inject') for d in injection_dates] + [(d, 'withdraw') for d in withdrawl_dates]
    events.sort(key=lambda x: x[0])

    for date, service in events:
        if service == 'inject':
            injected_amount = amount[date]
            if volume_in_storage + injected_amount > max_volume:
                print(f"Injection failed on {date}: exceeds {max_volume}")
                return None
            else:
                volume_in_storage += injected_amount
                total_value -= prices[date] * injected_amount
                total_value -= injection_withdrawl_fee * (injected_amount / 1000000)
                
        
        if service == 'withdraw':
            withdraw_amount = amount[date]
            if withdraw_amount > volume_in_storage:
                print(f"Withdraw failed on {date}: insufficient volume in storage")
                return None
            else:
                volume_in_storage -= withdraw_amount
                total_value += prices[date] * withdraw_amount
                total_value -= injection_withdrawl_fee * (withdraw_amount / 1000000)
        
    duration_months = (events[-1][0] - events[0][0]).days / 30.44
    total_value -= monthly_storage_fees * duration_months
    return total_value

inj_dates = [pd.Timestamp('2024-06-01'), pd.Timestamp('2024-07-01'), pd.Timestamp('2024-08-01')]
wd_dates  = [pd.Timestamp('2025-01-01'), pd.Timestamp('2025-02-01'), pd.Timestamp('2025-03-01')]
test_dates_all = inj_dates + wd_dates
test_prices = {d: estimate_price(d) for d in test_dates_all}
test_amounts = {pd.Timestamp('2024-06-01'): 2_000_000, pd.Timestamp('2024-07-01'): 1_000_000, pd.Timestamp('2024-08-01'): 1_500_000, pd.Timestamp('2025-01-01'): 2_000_000, pd.Timestamp('2025-02-01'): 1_000_000, pd.Timestamp('2025-03-01'): 1_500_000,
}


result = price_contract(
    injection_dates=inj_dates,
    withdrawl_dates=wd_dates,
    prices=test_prices,
    amount=test_amounts,
    max_volume=5_000_000,
    monthly_storage_fees=100_000,
    injection_withdrawl_fee=10_000,
)
print(result)