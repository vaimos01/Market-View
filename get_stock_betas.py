import yfinance as yf
import pandas as pd
import time
import pickle
import datetime

def get_stocks_data(ticker_list,time_period): 
    
    '''Download the historical price data for each stock using yfinance'''
    #stocks = yf.download(ticker, period="1y", interval="1d", group_by="ticker") #1mo, 1y, max
    
    # Create an empty DataFrame to store the 'Adj Close' prices for each stock
    adj_close = pd.DataFrame()
    returnz = []
    # Extract the 'Adj Close' prices for each stock and store them in the DataFrame
    for symbol in ticker_list:
        adj_close[symbol] = yf.download(symbol, period=time_period, interval="1d", group_by="ticker")["Adj Close"]
        try:         
            # Calculate the daily returns for stocks
            returns = adj_close[symbol].pct_change()
            returns = returns.tz_localize(None)

            returnz.append(returns)

        except Exception as e:
            print(e)
    
    data = pd.concat(returnz, axis=1)

    return data,adj_close

def calculate_beta(symbol,data):
    
    '''Function to calculate the beta value for each stock'''
    
    cov = data[symbol].cov(data["^BSESN"])
    var = data["^BSESN"].var()
    beta = cov / var
    return beta

def calc_bench(returns,ticker_list):
    
    '''Calculate the benchmark returns'''
    
    benchmark = yf.download("^BSESN", period="1y", interval="1d")["Adj Close"].pct_change()
    benchmark = benchmark.tz_localize(None)
    
    # Combine the returns data for the stocks and the benchmark into a single DataFrame
    data = pd.concat([returns, benchmark], axis=1)
    data.columns = ticker_list + ["^BSESN"]

    # Drop any rows with missing data
    data.dropna(how='all',inplace=True)
    #return data
    return data

def beta_fetch(ticker_lis,time_period):
    
    '''Generate beta list for all the tickers'''
    
    output = pd.DataFrame()
    j = 3
    i = 0
    final_lis = [ticker+'.NS' for ticker in ticker_lis]

    while i in range(len(final_lis)):
        print(i)

        if i+j<len(final_lis):
            try:
                stock_returns,stock_prices = get_stocks_data(final_lis[i:i+j],time_period)
                stock_returns = calc_bench(stock_returns,final_lis[i:i+j])
                stock_returns.dropna(axis=1,how='all',inplace=True)
                betas = {symbol: calculate_beta(symbol,stock_returns) for symbol in stock_returns.columns}
                df_dictionary = pd.DataFrame([betas])
                output = pd.concat([output, df_dictionary], ignore_index=True)
                print('done')
                
            except Exception as e:   
                print(e)


        else:
            try:
                stock_returns,stock_prices = get_stocks_data(final_lis[i:len(final_lis)],time_period)
                stock_returns = calc_bench(stock_returns,final_lis[i:len(final_lis)])
                stock_returns.dropna(axis=1,how='all',inplace=True)
                betas = {symbol: calculate_beta(symbol,stock_returns) for symbol in stock_returns.columns}
                df_dictionary = pd.DataFrame([betas])
                output = pd.concat([output, df_dictionary], ignore_index=True)
                print('done')
                
            except Exception as e:
                print(e)

#        time.sleep(10)
        i=i+j
    output = output.stack().droplevel(0).reset_index().rename(columns={'index':'stock',0:'beta'}).drop_duplicates()
    return output
  
