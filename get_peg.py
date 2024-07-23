#get_peg.py


import pandas as pd
import yfinance as yf
import os
import sys
from datetime import datetime


import yfinance as yf

def fetch_data(ticker):
    # Fetch historical market data
    data = yf.Ticker(ticker)

    # Get earnings per share
    eps = data.info['trailingEps'] if 'trailingEps' in data.info else 'N/A'

    # Get stock price
    price = data.info['previousClose'] if 'previousClose' in data.info else 'N/A'

    # Get the estimated earnings growth (5-year)
    growth = data.info['earningsGrowth'] if 'earningsGrowth' in data.info else 'N/A'

    # Calculate P/E ratio if possible
    pe_ratio = price / eps if eps != 'N/A' and price != 'N/A' else 'N/A'

    # Calculate PEG ratio if possible
    peg_ratio = pe_ratio / growth if pe_ratio != 'N/A' and growth != 'N/A' else 'N/A'

    return price, eps, pe_ratio, growth, peg_ratio


def create_peg_table(tickers):
    # Create a table to store the data
    table = pd.DataFrame(columns=['Ticker', 'Price', 'EPS', 'P/E', 'Growth', 'PEG'])

    # Fetch data for each ticker
    for ticker in tickers:
        price, eps, pe_ratio, growth, peg_ratio = fetch_data(ticker)
        new_row = pd.DataFrame({
            'Ticker': [ticker],
            'Price': [price],
            'EPS': [eps],
            'P/E': [pe_ratio],
            'Growth': [growth],
            'PEG': [peg_ratio]
        })
        table = pd.concat([table, new_row], ignore_index=True)

    return table

if __name__ == '__main__':
    print("\n\n")
    print(f'{"="*40}\n{"=" + " Fool Advisor PEG Ratio Comparison ".center(38, " ") + "="}\n{"="*40}\n')
    # Read the ticker data from fool_advisor.csv and make a list of tickers
    ticker_list = pd.read_csv('fool_advisor.csv')
    fool = ticker_list.iloc[:,0].values.tolist()
    fool.sort()
    print(fool)
    print("\n")
    fool_table = create_peg_table(fool)
    print(fool_table)
    print("\n\n")

    print(f'{"="*40}\n{"=" + " MAG7 PEG Ratio Comparison ".center(38, " ") + "="}\n{"="*40}\n')
    mag7 = ['AAPL', 'MSFT', 'TSLA', 'GOOGL', 'AMZN', 'META', 'NVDA' ]
    mag7_table = create_peg_table(mag7)

    print(mag7_table)
    print("\n\n")
    
    print(f'\n{"="*40}\n{"=" + " HOLDINGS PEG Ratio Comparison ".center(38, " ") + "="}\n{"="*40}\n')
    holdings = ['AAPL', 'AMZN', 'GBTC', 'MARA', 'META', 'MSFT', 'RIVN', 'TSLA' ]
    holdings_table = create_peg_table(holdings)
    print(holdings_table)
    print("\n\n")

