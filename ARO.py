from statsmodels.tsa.ar_model import AutoReg
import pandas as pd

# Load dataset
df = pd.read_csv('stock_prices.csv')
series = df['Close']

# Fit AR model
model = AutoReg(series, lags=5)
model_fit = model.fit()

# Forecast
forecast = model_fit.predict(start=len(series), end=len(series)+4)
print(forecast)
