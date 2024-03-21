import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import numpy as np
import os
import datetime
import sys

# Constants for configuration
CONFIG_FILE = 'analysis_settings.txt'
DATA_DIR = 'stock_data'
DEFAULT_TICKER = 'AAPL'


# Read settings from analysis_settings.txt
def read_settings():
    print("reading config file for settings...")
    settings = {'tickers': [], 'analyses': [], 'start_date': None, 'end_date': None}
    with open(CONFIG_FILE, 'r') as file:
        for line in file:
            if 'tickers:' in line:
                settings['tickers'] = line.split(':')[1].strip().split(',')
            elif 'start_date:' in line:
                settings['start_date'] = line.split(':')[1].strip()
            elif 'end_date:' in line:
                settings['end_date'] = line.split(':')[1].strip()
            elif 'analysis:' in line:
                parts = line.split(':')[1].strip().split(',')
                settings['analyses'].append({'type': parts[0], 'params': list(map(int, parts[1:]))})
    return settings


# Fetch and save stock data
def fetch_and_save_stock_data(ticker, start_date, end_date):
    filename = f'{DATA_DIR}/{ticker}.csv'
    #todo fix this so it downloads any missing data within the date range passed in
    #currently this function just check to see if a ticker exists, but doesn't make
    #sure the data in the storage file covers the given date range
    if not os.path.exists(filename):
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        if not stock_data.empty:
            stock_data.to_csv(filename)
            print(f"Data for {ticker} saved to {filename}")
        else:
            print(f"No data found for {ticker}")


# Calculate indicators
def calculate_indicators(data, analysis_type, params):
    if analysis_type == 'SMA':
        short_window, long_window = params
        data['Short_Moving_Avg'] = data['Close'].rolling(window=short_window).mean()
        data['Long_Moving_Avg'] = data['Close'].rolling(window=long_window).mean()
    elif analysis_type == 'Bollinger':
        window, num_of_std = params
        rolling_mean = data['Close'].rolling(window=window).mean()
        rolling_std = data['Close'].rolling(window=window).std()
        data['Bollinger_High'] = rolling_mean + (rolling_std * num_of_std)
        data['Bollinger_Low'] = rolling_mean - (rolling_std * num_of_std)
    return data



def calculate_buy_sell_signals(data, analysis_type, analysis_params):
    if analysis_type == 'SMA':
        short_window = analysis_params[0]
        long_window = analysis_params[1]
        # A simple strategy: buy when short SMA crosses above long SMA, sell when it crosses below
        data['Signal'] = 0.0  # Default no signal
        mask = (data['Short_Moving_Avg'] > data['Long_Moving_Avg']).values
        data.loc[mask, 'Signal'] = 1.0
        data['Position'] = data['Signal'].diff()
    elif analysis_type == 'Bollinger':
        # Placeholder for Bollinger-based strategy
        # data['Signal'] = ...
        # data['Position'] = ...
        pass
    return data

# Plot stock data with indicators
def plot_stock_data(ticker, data, analysis_type, analysis_params):
    plt.figure(figsize=(14, 7))
    plt.plot(data['Close'], label='Close Price', color='blue', alpha=0.35)

    # Assume only one analysis is active
    data = calculate_buy_sell_signals(data, analysis_type, analysis_params)

    if analysis_type == 'SMA':
        plt.plot(data['Short_Moving_Avg'], label='Short Moving Average', color='green', alpha=0.7)
        plt.plot(data['Long_Moving_Avg'], label='Long Moving Average', color='red', alpha=0.7)
    elif analysis_type == 'Bollinger':
        plt.plot(data['Bollinger_High'], label='Bollinger High', color='orange', alpha=0.7)
        plt.plot(data['Bollinger_Low'], label='Bollinger Low', color='purple', alpha=0.7)

    # Plot buy signals
    buy_signals = data[data['Position'] == 1]
    plt.scatter(buy_signals.index, buy_signals['Close'], label='Buy Signal', marker='^', color='green', alpha=1)

    # Plot sell signals
    sell_signals = data[data['Position'] == -1]
    plt.scatter(sell_signals.index, sell_signals['Close'], label='Sell Signal', marker='v', color='red', alpha=1)

    plt.title(f'Stock Price and Indicators for {ticker}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid(True)
    plt.show()

#Main execution
def run_analysis():
    print("Starting Stock Analyzer.")
    settings = read_settings()
    print(settings)
    os.makedirs(DATA_DIR, exist_ok=True)
    for ticker in settings['tickers']:
        fetch_and_save_stock_data(ticker, settings['start_date'], settings['end_date'])
        file_path = f'{DATA_DIR}/{ticker}.csv'
        if os.path.exists(file_path):
            data = pd.read_csv(file_path, index_col='Date', parse_dates=True)
            for analysis in settings['analyses']:
                data = calculate_indicators(data, analysis['type'], analysis['params'])
            # Calculate the buy/sell signals
            #for analysis in settings['analyses']:
            #    data = calculate_signals(data)

            plot_stock_data(ticker, data, analysis['type'], analysis['params'])

if __name__ == "__main__":
    run_analysis()
