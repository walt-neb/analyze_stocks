import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import sys
import warnings
import pandas as pd
import yfinance as yf
import warnings


def read_csv_file(file_name):
    df = pd.read_csv(file_name, comment='#', header=None)
    df.columns = ['Ticker', 'Shares']
    #df = df[df['Ticker'].str.contains(',')]
    return df

def fetch_data(ticker):
    data = yf.download(ticker, period='1d')
    return data.iloc[-1]

def calculate_value(df):
    ticker_prices = {}
    for ticker in df['Ticker']:
        if ticker.upper() == 'CASH':
            ticker_prices[ticker] = 1
        else:
            if ticker not in ticker_prices:
                price = fetch_data(ticker)[0]  # Get the first element of the tuple (Close price)
                ticker_prices[ticker] = price
    
    df['Last Price'] = df['Ticker'].map(ticker_prices)
    df['Value'] = df['Shares'] * df['Last Price']
    return df

# def create_pie_chart(df):
#     plt.figure(figsize=(10, 10))
#     # plt.pie(df['Value'], labels=df['Ticker'], autopct=lambda pct: f"{pct:.1f}% (${int(pct/100*df['Value'].sum()):,})")
#     # plt.title(f"Portfolio Allocation - {pd.Timestamp.today().strftime('%Y-%m-%d')} (Total: ${df['Value'].sum():,})")
#     plt.pie(df['Value'], labels=df['Ticker'], autopct='%1.1f%%')
#     plt.title(f"Portfolio Allocation - {pd.Timestamp.today().strftime('%Y-%m-%d')}")
#     plt.savefig(sys.argv[1] + '.jpg')
#     plt.show()

def create_pie_chart(df):
    plt.figure(figsize=(10, 10))
    labels = [f"{ticker}, {pct:.1f}%" for ticker, pct in zip(df['Ticker'], df['Value'] / df['Value'].sum() * 100)]
    plt.pie(df['Value'], labels=labels, labeldistance=1.08, counterclock=False)
    plt.title(f"Portfolio Allocation - {pd.Timestamp.today().strftime('%Y-%m-%d')}")
    plt.savefig(sys.argv[1] + '.png')
    plt.show()
    

def parse_input_data(df):
    ticker_shares = {}
    for index, row in df.iterrows():
        ticker = row['Ticker']
        shares = row['Shares']
        if ticker not in ticker_shares:
            ticker_shares[ticker] = 0
        ticker_shares[ticker] += shares
    
    unique_tickers = pd.DataFrame({'Ticker': list(ticker_shares.keys()), 'Shares': list(ticker_shares.values())})
    return unique_tickers


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
        
        # Check if new_row is empty or contains all NA values
        if not new_row.empty and not new_row.isna().all().all():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                table = pd.concat([table, new_row], ignore_index=True)

    # Round the float columns to 2 decimal places
    float_columns = ['Price', 'EPS', 'P/E', 'Growth', 'PEG']
    table[float_columns] = table[float_columns].round(2)

    return table


# def run_allocations(file_name):
#     # Main part of the program
#     df = read_csv_file(file_name)
#     summed_shares = parse_input_data(df)
    
#     print('\n')
#     print(summed_shares)
#     df = calculate_value(summed_shares)
#     df = df.sort_values('Value', ascending=False)
    
#     print('\n')
#     print('Portfolio Allocation on ' + pd.Timestamp.today().strftime('%Y-%m-%d'))
#     print(df.round(2))

    
#     peg_table = create_peg_table(summed_shares['Ticker'])
#     print('\n')


#     print(peg_table)
#     create_pie_chart(df)
#     peg_table.to_excel(file_name + '.xlsx', index=False)

def run_allocations(file_name):
    # Main part of the program
    df = read_csv_file(file_name)
    summed_shares = parse_input_data(df)
    
    print('\n')
    print('Holdings input from ' + file_name)
    print(summed_shares)
    df = calculate_value(summed_shares)
    df = df.sort_values('Value', ascending=False)
    
    print('\n')
    print('Portfolio Holdings as of ' + pd.Timestamp.today().strftime('%Y-%m-%d'))
    print(df.round(2))

    
    peg_table = create_peg_table(summed_shares['Ticker'])
    print('\n')

    combined_table = pd.merge(df, peg_table, on='Ticker')
    combined_table = combined_table.drop('Price', axis=1)
    combined_table['% Pie'] = combined_table['Value'] / combined_table['Value'].sum() * 100
    combined_table['% Pie'] = combined_table['% Pie'].round(2)
    combined_table['P/E'] = combined_table['P/E'].round(2)
    combined_table['Growth'] = combined_table['Growth'].round(2)
    combined_table['Last Price'] = combined_table['Last Price'].map('${:,.2f}'.format)
    combined_table['Value'] = combined_table['Value'].map('${:,.0f}'.format)

    # Convert PEG and P/E columns values to float before formatting decimal places
    combined_table.loc[combined_table['PEG'] != 'N/A', 'PEG'] = combined_table.loc[combined_table['PEG'] != 'N/A', 'PEG'].astype(float)
    combined_table.loc[combined_table['PEG'] != 'N/A', 'PEG'] = combined_table.loc[combined_table['PEG'] != 'N/A', 'PEG'].map('{:,.2f}'.format)
    combined_table.loc[combined_table['P/E'] != 'N/A', 'P/E'] = combined_table.loc[combined_table['PEG'] != 'N/A', 'P/E'].astype(float)
    combined_table.loc[combined_table['P/E'] != 'N/A', 'P/E'] = combined_table.loc[combined_table['PEG'] != 'N/A', 'P/E'].map('{:,.2f}'.format)
    
    combined_table = combined_table[['Ticker', 'Shares', 'Last Price', 'Value', '% Pie', 'EPS', 'P/E', 'Growth', 'PEG']]

    print('Walt\'s Portfolio Summary as of: ' + pd.Timestamp.today().strftime('%Y-%m-%d'))
    print(combined_table)
    create_pie_chart(df)
    combined_table.to_excel(file_name + '.xlsx', index=False)



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <tickerlist_file_name>")
        print(f'where <tickerlist_file_name> is a text file containing a column of stock tickers')
        sys.exit(1)
    else:
        file_name = sys.argv[1]

    run_allocations(file_name)


