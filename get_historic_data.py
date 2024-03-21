import pandas as pd
import yfinance as yf
import os
from datetime import datetime

# Normalize date format
def normalize_date(date_str):
    if not pd.isnull(date_str) and date_str:
        try:
            return datetime.strptime(date_str.strip(), '%Y-%m-%d').strftime('%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str.strip(), '%m-%d-%Y').strftime('%Y-%m-%d')
            except ValueError:
                print(f"Date format not recognized: {date_str}")
                return None
    return None

# Read the CSV file with the first column as index
df = pd.read_csv('my_tickers.csv', index_col=0)
df['Start Date'] = df['Start Date'].apply(normalize_date)
df['End Date'] = df['End Date'].apply(normalize_date)

# Ensure the stock_data directory exists
os.makedirs('stock_data', exist_ok=True)

# Function to fetch and save stock data along with additional metrics
def fetch_and_save_stock_data(ticker, start_date, end_date):
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    if not stock_data.empty:
        # Fetch additional information
        ticker_info = yf.Ticker(ticker)
        info = ticker_info.info
        additional_data = {
            'dividendYield': info.get('dividendYield'),
            'targetMeanPrice': info.get('targetMeanPrice'),
            'earningsDate': info.get('earningsDate', [None])[0],
            'beta': info.get('beta'),
            'priceToBook': info.get('priceToBook'),
            'priceToSalesTrailing12Months': info.get('priceToSalesTrailing12Months'),
            'forwardPE': info.get('forwardPE')
        }

        for key, value in additional_data.items():
            stock_data[key] = value

        filename = f'stock_data/{ticker}.csv'
        stock_data.to_csv(filename)
        print(f"Data for {ticker} saved to {filename}")
    else:
        print(f"No data found for {ticker}")

# Iterate over each row to fetch and save data
for ticker, row in df.iterrows():
    start_date = row['Start Date']
    end_date = row['End Date']
    fetch_and_save_stock_data(ticker, start_date, end_date)
