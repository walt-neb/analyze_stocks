import pandas as pd
import yfinance as yf
import os
import sys
from datetime import datetime
import warnings
import numpy as np
import yfinance as yf

#get_peg.py


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

    # Get market cap
    market_cap = data.info['marketCap'] if 'marketCap' in data.info else 'N/A'

    # Get price/sales (ttm)
    price_sales = data.info['priceToSalesTrailing12Months'] if 'priceToSalesTrailing12Months' in data.info else 'N/A'

    # Get % held by institutions
    percent_held_by_institutions = data.info['heldPercentInstitutions'] * 100 if 'heldPercentInstitutions' in data.info else 'N/A'

    # Get % held by insiders
    percent_held_by_insiders = data.info['heldPercentInsiders'] * 100 if 'heldPercentInsiders' in data.info else 'N/A'

    # Get short % of shares outstanding
    short_percent_of_shares_outstanding = data.info['shortPercentOfFloat'] * 100 if 'shortPercentOfFloat' in data.info else 'N/A'


    return price, eps, pe_ratio, growth, peg_ratio, price_sales, market_cap, percent_held_by_institutions, percent_held_by_insiders, short_percent_of_shares_outstanding


def create_peg_table(tickers):
    # Create a table to store the data
    table = pd.DataFrame(columns=['Ticker', 'Price', 'EPS', 'P/E', 'Growth', 'PEG'])

    # Fetch data for each ticker
    for ticker in tickers:
        [price, eps, pe_ratio, growth, 
        peg_ratio, price_sales, market_cap,
        percent_held_by_institutions, 
        percent_held_by_insiders, 
        short_percent_of_shares_outstanding]  = fetch_data(ticker)
        
        market_cap = market_cap / 1e6 if market_cap != 'N/A' else 'N/A'
        pe_ratio = np.round(pe_ratio,2) if pe_ratio != 'N/A' else 'N/A'
        peg_ratio = np.round(peg_ratio, 2) if peg_ratio != 'N/A' else 'N/A'
        
        new_row = pd.DataFrame({
            'Ticker': [ticker],
            'Price': [price],
            'EPS': [eps],
            'P/E': [pe_ratio],
            'Growth': [growth],
            'PEG': [peg_ratio],
            'Price/Sales': [price_sales],
            'Market Cap MM': [market_cap],
            '% Inst. Held': [percent_held_by_institutions],
            '% Insid. Held': [percent_held_by_insiders],
            '% Short': [short_percent_of_shares_outstanding]

        })
        
        # Check if new_row is empty or contains all NA values
        if not new_row.empty and not new_row.isna().all().all():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                table = pd.concat([table, new_row], ignore_index=True)

    return table.round(2)  # Round the table to two decimal places


# def load_tickers(file_name):
#     # Read the file line by line and process only relevant lines
#     tickers = []
#     with open(file_name, 'r') as file:
#         for line in file:
#             line = line.strip()
#             if line.startswith("#") or ':' not in line:
#                 continue
#             symbol = line.split(':')[0].strip()
#             tickers.append(symbol)
    
#     return tickers
    

def load_tickers(file_name):
    tickers = []
    with open(file_name, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            ticker = line.split(',')[0].strip()
            tickers.append(ticker)
    return tickers

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <tickerlist_file_name>")
        print(f'where <tickerlist_file_name> is a text file containing a column of stock tickers')
        sys.exit(1)
    else:
        file_name = sys.argv[1]

    if not os.path.exists(file_name):
        print(f"Error: File '{file_name}' not found.")
        sys.exit(1)
    
    tickers = load_tickers(file_name)
    print(f'\n\nReading ticker list from {file_name}')


    if len(tickers[0].split(',')) > 1:
        print("\n")
        print(tickers)
        print(f'Expected 1 column, found {len(tickers[0].split(","))} columns')
        sys.exit(0)

    elif len(tickers[0].split(',')) == 1:
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', 1000)
        table = create_peg_table(tickers)
        numerical_cols = table.select_dtypes(include=['float64', 'float32', 'int64']).columns
        table[numerical_cols] = table[numerical_cols].round(2)
        
        # Print the table with a title
        print("\n")
        print(f'Date: {datetime.now().strftime("%m-%d-%Y %H:%M:%S")}')
        print(f'{"="*40}\n{"=" + "  PEG Ratio Comparison ".center(38, " ") + "="}\n{"="*40}\n')
        print(table)
        print("\n")

        # Convert the table to CSV format and print it
        csv_output = table.to_csv(index=False)
        print("CSV format of the table:\n")
        print(csv_output)
