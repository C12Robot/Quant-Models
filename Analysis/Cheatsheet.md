# Python & Pandas Cheatsheet

**Last updated: May 2026**

---

## Setup

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from mlxtend.preprocessing import minmax_scaling
import yfinance as yf
import sqlite3
import calendar
```

---

## 1. Creating Data

```python
# DataFrame — a table
pd.DataFrame({'Yes': [50, 21], 'No': [56, 45]})

# DataFrame with custom index
pd.DataFrame({
    'Aryan': ['Smart', 'Builder'],
    'FRIDAY': ['AI', 'Assistant']
}, index=['Row 1', 'Row 2'])

# Series — a single column / list
pd.Series([1, 2, 3, 4, 5])
```

---

## 2. Reading & Saving Data

```python
# CSV
df = pd.read_csv('file.csv')
df = pd.read_csv('file.csv', low_memory=False)   # for mixed type columns
df = pd.read_csv('file.csv', index_col=0)         # use first column as index
df = pd.read_csv('file.csv', skiprows=3)          # skip N header rows (e.g. CBOE CSV)
print(df.to_string())                              # print entire file

# Save to CSV
df.to_csv('filename.csv', index=False)

# SQLite database
conn = sqlite3.connect('file.sqlite')
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", conn)
df = pd.read_sql("SELECT * FROM table_name", conn)
conn.close()

# Market data
nifty = yf.download("^NSEI", period="1y")
data = yf.download(['^NSEI', '^GSPC', 'GC=F'], period="2y")['Close']
data.columns = ['Nifty', 'SP500', 'Gold']         # rename after MultiIndex download
data.droplevel(1, axis=1)                          # alternative: drop MultiIndex level
```

---

## 3. Exploring Data

```python
df.head()            # first 5 rows
df.shape             # (rows, columns) — no brackets, it's a property
df.columns           # column names
df.dtypes            # data types per column
df.describe()        # basic stats for numeric columns
df.isnull().sum()    # count nulls per column
np.prod(df.shape)    # total cells (rows × columns)
```

---

## 4. Selecting Data

```python
df['column']                      # single column
df[['col1', 'col2']]              # multiple columns — double brackets

# loc — label based (inclusive on both ends)
df.loc[0, 'column']
df.loc[0]
df.loc[:, 'column']
df.loc[0:10]

# iloc — position based (excludes last)
df.iloc[0, 0]
df.iloc[:, 0]
df.iloc[0:10]

df.set_index('title')             # set index
df.ffill()                        # forward fill missing values (use before iloc[-1])
df.iloc[-1]                       # last row
df.iloc[0]                        # first row
```

> **loc vs iloc:** loc is label-based and inclusive. iloc is position-based and excludes the last element.

> **ffill():** Always use before `.iloc[-1]` or `.iloc[0]` when data has NaN gaps (e.g. BTC on trading days).

---

## 5. Filtering Data

```python
df.loc[df['country'] == 'Italy']
df.loc[(df['country'] == 'Italy') & (df['points'] >= 90)]
df.loc[(df['country'] == 'Italy') | (df['points'] >= 90)]
df.loc[df['country'].isin(['Italy', 'France'])]
df.loc[df['price'].isnull()]
df.loc[df['price'].notnull()]
df[df['Signal'].diff() == 1]      # filter rows where value changed to 1 (crossover)
```

---

## 6. Aggregation

```python
df['column'].count()
df['column'].sum()
df['column'].mean()
df['column'].median()
df['column'].max()
df['column'].min()
df['column'].idxmax()             # index of max value — returns date/label, not value
df['column'].idxmin()             # index of min value
df['column'].value_counts()
df.mean(numeric_only=True)
df.sum(numeric_only=True)
```

> **max() vs idxmax():** max() returns the value. idxmax() returns when/where it happened.

> **count() vs value_counts():** count() = non-null rows. value_counts() = frequency of each unique value.

---

## 7. Groupby

```python
df.groupby('X')['Y'].max()
df.groupby('X')['Y'].mean()
df.groupby('X')['Y'].agg([min, max])
df.groupby(['X1', 'X2']).size()
df.groupby('winery').apply(lambda df: df.title.iloc[0])

# group by calendar month
df.groupby(df.index.month)['Return'].mean()    # index.month extracts month number (1-12)
df.groupby(df.index.year)['Return'].mean()     # group by year
df.groupby(df.index.dayofweek)['Return'].mean()# group by day of week
```

---

## 8. Sorting

```python
df.sort_index()
df.sort_index(ascending=False)
df.sort_values('column')
df.sort_values(by=['col1', 'col2'], ascending=[False, False])
series.sort_values(ascending=False).head(5)    # top 5 values — sort THEN head
series.sort_values().head(5)                   # bottom 5 values
```

> **head() alone doesn't sort** — always sort first, then slice with head/tail.

---

## 9. Mapping & Applying Functions

```python
reviews.points.map(lambda p: p - reviews.points.mean())
df['description'].map(lambda x: "word" in str(x)).sum()

def stars(row):
    if row.country == 'Canada': return 3
    elif row.points >= 95: return 3
    elif row.points >= 85: return 2
    else: return 1

star_ratings = reviews.apply(stars, axis='columns')
reviews.country + " - " + reviews.region_1
```

> **map() vs apply():** map() = element by element on a Series. apply() = row or column of a DataFrame.

---

## 10. Cleaning Data

```python
df.fillna('Unknown')
df.fillna({'col1': 'None', 'col2': 0})
df.dropna()
df.dropna(subset=['Name'])
df['Type'].replace({'Grass': 'GRASS'})
df['Name'] = df['Name'].str.lower()
df['column'] = df['column'].astype(float)
df = df.drop(columns=['column_name'])
df = df.drop_duplicates()
df.rename(columns={'old': 'new'})
pd.to_numeric(df['column'], errors='coerce')   # convert to float, bad values → NaN
```

---

## 11. Finance-Specific Operations

```python
# returns
returns = data.pct_change().dropna()

# cumulative returns
cumulative = (1 + returns).cumprod()

# drawdown
drawdown = (cumulative - cumulative.cummax()) / cumulative.cummax()
max_drawdown = drawdown.min()                   # most negative value per column

# rolling stats
rolling_vol = returns.rolling(30).std() * np.sqrt(252)   # annualised
rolling_mean = returns.rolling(20).mean()

# resample to lower frequency
monthly = data.resample('ME').last()            # month end last price
monthly['Return'] = monthly['Close'].pct_change()

# crossover signal
data['Signal'] = 0
data.loc[MA20 > MA50, 'Signal'] = 1
crossovers = data[data['Signal'].diff() == 1]  # dates where signal flipped to 1

# correlation matrix
returns.corr()                                  # pass to sns.heatmap()
```

---

## 12. Time Series Utilities

```python
# shift — compare today vs yesterday
df['Prev'] = df['Signal'].shift(1)             # moves values down 1 row

# datetime formatting
date.strftime('%B %Y')                          # → 'April 2026'
date.strftime('%b')                             # → 'Apr'
date.strftime('%Y-%m-%d')                       # → '2026-04-30'

# extract date parts
df.index.month                                  # month number (1-12)
df.index.year
df.index.dayofweek                              # 0=Monday, 6=Sunday

# parse dates
df['date'] = pd.to_datetime(df['Date'], format='%m/%d/%Y')
df['date'] = pd.to_datetime(df['Date'], infer_datetime_format=True)  # slower
df['date'].dt.day
df['date'].dt.month
df['date'].dt.year
```

---

## 13. Calendar Module

```python
import calendar

calendar.month_name[4]    # → 'April'  (full name, index 1-12)
calendar.month_abbr[4]    # → 'Apr'    (short name)

# loop with month names
for month, val in series.items():
    print(f"{calendar.month_name[month]}: {val:.2%}")

# list comprehension for bar chart x-axis
month_names = [calendar.month_abbr[m] for m in series.index]
plt.bar(month_names, series.values)
```

---

## 14. Plotting

```python
# line plot
plt.plot(df.index, df['Close'], label='Price')
ax.plot(df.index, MA20, color='red', label='MA20')  # always pass .index explicitly

# scatter — use for crossover dots, events
plt.scatter(x, y, color='green', marker='^', zorder=5)
# zorder controls drawing order — higher = on top of other elements

# bar chart
plt.bar(x, y)                   # matplotlib — simple
sns.barplot(x=x, y=y)           # seaborn — adds CI bars

# histogram
sns.histplot(data, ax=ax[0], kde=True)   # use histplot for subplots, not displot
plt.hist(values, bins=50, alpha=0.7)    # matplotlib histogram

# heatmap
sns.heatmap(returns.corr(), annot=True, cmap='coolwarm')

# subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig, ax = plt.subplots(1, 2, figsize=(15, 3))

# display options
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
plt.tight_layout()
plt.show()
```

> **plt.plot() vs df.plot():** `df.plot()` uses index automatically. `plt.plot()` and `ax.plot()` — always pass `.index` as x explicitly.

> **displot vs histplot:** displot ignores `ax=` and creates its own figure. histplot respects `ax=`. Always use histplot for subplots.

> **zorder:** Higher = drawn on top. Default lines are zorder 1-2. Use zorder=5 on scatter to appear above lines.

---

## 15. Numpy

```python
np.random.seed(0)
np.random.normal(loc=mean, scale=std, size=1000)    # Monte Carlo simulations
np.random.exponential(size=1000)
np.prod(df.shape)
np.sqrt(252)                                         # annualisation factor
np.percentile(values, 5)                             # 5th percentile — Value at Risk
```

---

## 16. Scaling & Transformations

```python
scaled = minmax_scaling(data, columns=[0])
normalized = stats.boxcox(original_data)
```

---

## 17. Format Specifiers

```python
f"{value:.2f}"    # 2 decimal places → 0.07
f"{value:.2%}"    # percentage, 2 decimal places → 7.46% (multiplies by 100 automatically)
f"{value:.0f}"    # integer, no decimals
```

---

## 18. Common Mistakes

|Mistake|Fix|
|---|---|
|`df.shape()`|`df.shape` — no brackets|
|`np.product()`|`np.prod()` — deprecated|
|`sns.displot(ax=ax[0])`|`sns.histplot(ax=ax[0])` — displot ignores ax=|
|`df.groupby('X', 'Y')`|`df.groupby(['X', 'Y'])` — needs a list|
|`df.to_csv('file.csv')`|`df.to_csv('file.csv', index=False)`|
|`sort_values([size])`|`sort_values(ascending=False)`|
|`agg['min','max']`|`agg([min, max])`|
|`idk(idk['col'] == val)`|`idk[idk['col'] == val]` — filter uses `[]` not `()`|
|`data['ES'].std()`|`returns['ES'].std()` — always std of returns, not prices|
|`mean()` inside loop|aggregate stats always go **outside** the loop|
|`for x in x`|variable name collision — use `for scenario in scenarios`|
|`head()` without sorting|`sort_values().head(5)` — sort first|
|`252/252` for ann. return|`252/trading_days` — use actual number of trading days|