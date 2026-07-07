import pandas as pd
import numpy as np 
import datetime
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

loans = pd.read_csv(r"C:\Users\meena\Documents\testing\Loan_Data.csv")

X = loans[['credit_lines_outstanding','loan_amt_outstanding', 'total_debt_outstanding', 'income', 'years_employed', 'fico_score']]
Y = loans['default']
X_train, X_test, Y_train, Y_test = train_test_split(X,Y, test_size = 0.2, random_state = 42)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression()
model.fit(X_train_scaled, Y_train)

y_predict = model.predict(X_test_scaled)
y_probability = model.predict_proba(X_test_scaled)[:,1]

print(f"Accuracy of Model:", accuracy_score(Y_test, y_predict))
print(f"AUC:", roc_auc_score(Y_test, y_probability))

def credit_risk(credit_lines_outstanding, loan_amt_outstanding, total_debt_outstanding, income, years_employed, fico_score):
    input_data = [[credit_lines_outstanding, loan_amt_outstanding, total_debt_outstanding, income, years_employed, fico_score]]
    input_scaled = scaler.transform(input_data)
    pd_estimate = float(model.predict_proba(input_scaled)[:,1][0])
    expected_loss = float(pd_estimate* (1-0.1) * loan_amt_outstanding)
    return pd_estimate, expected_loss

Probability, expected_loss = credit_risk(credit_lines_outstanding=5, loan_amt_outstanding=1958.92873, total_debt_outstanding=8228.753, income=26648.44, years_employed=2, fico_score=572)
print(f"Probability of Default: {Probability*100}%")
print(f"Expected Loss: ${expected_loss:,.2f}")


