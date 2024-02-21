from statsmodels.tsa.arima.model import ARIMA
import pandas as pd

# Load dataset
df = pd.read_csv('stock_prices.csv')
series = df['Close']  # Assuming you're predicting closing prices

# Fit ARIMA model (example: ARIMA(5,1,0))
model = ARIMA(series, order=(5,1,0))
model_fit = model.fit()

# Forecast
forecast = model_fit.forecast(steps=5)
print(forecast)
