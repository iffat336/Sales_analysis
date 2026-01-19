import pandas as pd
import numpy as np
import sqlite3
import os
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings

# Suppress statsmodels warnings for cleaner logs
warnings.filterwarnings("ignore")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_analysis.db")

def get_sales_data():
    """Fetches daily revenue data from the database."""
    conn = sqlite3.connect(DB_PATH)
    try:
        query = """
            SELECT 
                DATE(i.invoice_date) as date, 
                SUM(ii.quantity * ii.price) as revenue
            FROM invoices i
            JOIN invoice_items ii ON i.invoice_id = ii.invoice_id
            GROUP BY date
            ORDER BY date
        """
        df = pd.read_sql(query, conn)
        df['date'] = pd.to_datetime(df['date'])
        df = df.set_index('date')
        # Resample to Daily frequency to ensure continuous timeline (fill missing days with 0)
        df = df.resample('D').sum().fillna(0)
        return df
    finally:
        conn.close()

def generate_forecast(days=30):
    """
    Generates a revenue forecast for the next 'days' days.
    Returns: DataFrame with columns [Revenue, Forecast]
    """
    df = get_sales_data()
    
    # Validation: Need enough data points
    if len(df) < 14:
        raise ValueError("Not enough data to forecast. Need at least 14 days of history.")

    # 1. Train Model (Holt-Winters Exponential Smoothing)
    # 'additive' trend/seasonal usually works best for general sales unless they grow exponentially
    # We use a 7-day seasonality since retail is weekly.
    try:
        model = ExponentialSmoothing(
            df['revenue'],
            trend='add',
            seasonal='add',
            seasonal_periods=7
        ).fit()
    except:
        # Fallback for simpler data
        model = ExponentialSmoothing(df['revenue'], trend='add').fit()

    # 2. Predict
    forecast = model.forecast(days)
    
    # 3. Create Result DataFrame
    # Extend the index for future dates
    last_date = df.index[-1]
    future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
    
    forecast_df = pd.DataFrame(index=future_dates, data={'Forecast': forecast.values})
    
    # Combine (for plotting)
    # We return the original data joined with forecast
    # The original data will have NaN in 'Forecast', the new data will have Values
    combined_df = df.copy()
    combined_df['Forecast'] = np.nan
    
    # Append forecast
    forecast_df['revenue'] = np.nan # Historic revenue is unknown for future
    
    result = pd.concat([combined_df, forecast_df])
    
    return result

if __name__ == "__main__":
    print("Testing Forecasting Engine...")
    try:
        forecast_data = generate_forecast(30)
        print(f"Success! Generated forecast. Total records: {len(forecast_data)}")
        print(forecast_data.tail())
    except Exception as e:
        print(f"Error: {e}")
