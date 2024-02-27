import robin_stocks.robinhood as r
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 
from datetime import *
import yfinance as yf
import dateutil.parser
def safe_division(n, d):
    return n / d if d else 0

def get_historicals(ticker, intervalArg, spanArg, boundsArg):
    try:
        history = r.get_stock_historicals(ticker,interval=intervalArg,span=spanArg,bounds=boundsArg)
    except:
        print("Crypto cannot be calculated atm.")
        raise
    #If it's not a stock ticker, try it as a crypto ticker
    if(history is None or None in history):
        #history = r.get_crypto_historicals(ticker,interval=intervalArg,span=spanArg,bounds=boundsArg)
        print("^^Above This is a Crypto Error Disregard^^")

    return history

def get_stockquote(ticker):

    quote = r.get_stock_quote_by_id(ticker)
    #If it's not a stock ticker, try it as a crypto ticker
    if(quote is None or None in quote):
        quote = r.get_crypto_quote_by_id(ticker)
        print("^^Above This is a Crypto Error Disregard^^")
    return quote

def get_watchlist_symbols():
    """
    Returns: the symbol for each stock in your watchlist as a list of strings
    """
    my_list_names = set()
    symbols = set()
    
    watchlistInfo = r.get_all_watchlists()
    for watchlist in watchlistInfo['results']:
        listName = watchlist['display_name']
        my_list_names.add(listName)

    for listName in my_list_names:
        watchlist = r.get_watchlist_by_name(name=listName)
        if(watchlist is None):
            print('')
        else:
            for item in watchlist['results']:
                symbol = item['symbol']
                symbols.add(symbol)

    return symbols

def get_portfolio_symbols():
    """
    Returns: the symbol for each stock in your portfolio as a list of strings
    """
    symbols = []
    holdings_data = r.get_open_stock_positions()
    for item in holdings_data:
        if not item:
            continue
        instrument_data = r.get_instrument_by_url(item.get('instrument'))
        symbol = instrument_data['symbol']
        symbols.append(symbol)
    return symbols

def get_position_creation_date(symbol, holdings_data):
    """Returns the time at which we bought a certain stock in our portfolio

    Args:
        symbol(str): Symbol of the stock that we are trying to figure out when it was bought
        holdings_data(dict): dict returned by r.get_open_stock_positions()

    Returns:
        A string containing the date and time the stock was bought, or "Not found" otherwise
    """
    instrument = r.get_instruments_by_symbols(symbol)
    url = instrument[0].get('url')
    for dict in holdings_data:
        if(dict.get('instrument') == url):
            return dict.get('created_at')
    return "Not found"

def get_modified_holdings():
    """ Retrieves the same dictionary as r.build_holdings, but includes data about
        when the stock was purchased, which is useful for the read_trade_history() method
        in tradingstats.py

    Returns:
        the same dict from r.build_holdings, but with an extra key-value pair for each
        position you have, which is 'bought_at': (the time the stock was purchased)
    """
    holdings = r.build_holdings()
    holdings_data = r.get_open_stock_positions()
    for symbol, dict in holdings.items():
        bought_at = get_position_creation_date(symbol, holdings_data)
        bought_at = str(pd.to_datetime(bought_at))
        holdings[symbol].update({'bought_at': bought_at})
    return holdings

def get_last_crossing(df, days, symbol="", direction=""):
    """Searches for a crossing between two indicators for a given stock

    Args:
        df(pandas.core.frame.DataFrame): Pandas dataframe with columns containing the stock's prices, both indicators, and the dates
        days(int): Specifies the maximum number of days that the cross can occur by
        symbol(str): Symbol of the stock we're querying. Optional, used for printing purposes
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
    """
    prices = df.loc[:,"Price"]
    shortTerm = df.loc[:,"Indicator1"]
    LongTerm = df.loc[:,"Indicator2"]
    dates = df.loc[:,"Dates"]
    lastIndex = prices.size - 1
    index = lastIndex
    found = index
    recentDiff = (shortTerm.at[index] - LongTerm.at[index]) >= 0
    if((direction == "above" and not recentDiff) or (direction == "below" and recentDiff)):
        return 0
    index -= 1
    while(index >= 0 and found == lastIndex and not np.isnan(shortTerm.at[index]) and not np.isnan(LongTerm.at[index]) \
                        and ((pd.Timestamp("now", tz='UTC') - dates.at[index]) <= pd.Timedelta(str(days) + " days"))):
        if(recentDiff):
            if((shortTerm.at[index] - LongTerm.at[index]) < 0):
                found = index
        else:
            if((shortTerm.at[index] - LongTerm.at[index]) > 0):
                found = index
        index -= 1
    if(found != lastIndex):
        if((direction == "above" and recentDiff) or (direction == "below" and not recentDiff)):
            print(symbol + ": Short SMA crossed" + (" ABOVE " if recentDiff else " BELOW ") + "Long SMA at " + str(dates.at[found]) \
                +", which was " + str(pd.Timestamp("now", tz='UTC') - dates.at[found]) + " ago", ", price at cross: " + str(prices.at[found]) \
                + ", current price: " + str(prices.at[lastIndex]))
        return (1 if recentDiff else -1)
    else:
        return 0

def five_year_check(stockTicker):
    """Figure out if a stock has risen or been created within the last five years.

    Args:
        stockTicker(str): Symbol of the stock we're querying

    Returns:
        True if the stock's current price is higher than it was five years ago, or the stock IPO'd within the last five years
        False otherwise
    """
    instrument = r.get_instruments_by_symbols(stockTicker)
    if(instrument is None or len(instrument) == 0):
        return True
    list_date = instrument[0].get("list_date")
    if ((pd.Timestamp("now") - pd.to_datetime(list_date)) < pd.to_timedelta(df['years_variable']*365, unit = 'D')).dt.date:
        return True
    fiveyear =  get_historicals(stockTicker, "day", "5year", "regular")
    if (fiveyear is None or None in fiveyear):
        return True
    closingPrices = []
    for item in fiveyear:
        closingPrices.append(float(item['close_price']))
    recent_price = closingPrices[len(closingPrices) - 1]
    oldest_price = closingPrices[0]
    return (recent_price > oldest_price)

def golden_cross(stockTicker, n1, n2, days, direction=""):
    """Determine if a golden/death cross has occured for a specified stock in the last X trading days

    Args:
        stockTicker(str): Symbol of the stock we're querying
        n1(int): Specifies the short-term indicator as an X-day moving average.
        n2(int): Specifies the long-term indicator as an X-day moving average.
                 (n1 should be smaller than n2 to produce meaningful results, e.g n1=50, n2=200)
        days(int): Specifies the maximum number of days that the cross can occur by
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
        False if direction == "above" and five_year_check(stockTicker) returns False, meaning that we're considering whether to
            buy the stock but it hasn't risen overall in the last five years, suggesting it contains fundamental issues
    """
    if(direction == "above"):
        return False
    
    history = get_historicals(stockTicker, "day", "year", "regular")

    #Couldn't get pricing data
    if(history is None or None in history):
        return False
    
    closingPrices = []
    dates = []
    for item in history:
        closingPrices.append(float(item['close_price']))
        dates.append(item['begins_at'])
    price = pd.Series(closingPrices)
    dates = pd.Series(dates)
    dates = pd.to_datetime(dates)
    sma1 = ta.volatility.bollinger_mavg(price, int(n1), False)
    sma2 = ta.volatility.bollinger_mavg(price, int(n2), False)
    series = [price.rename("Price"), sma1.rename("Indicator1"), sma2.rename("Indicator2"), dates.rename("Dates")]
    df = pd.concat(series, axis=1)
    cross = get_last_crossing(df, days, symbol=stockTicker, direction=direction)
    
    if(cross) and plot:
        show_plot(price, sma1, sma2, dates, symbol=stockTicker, label1=str(n1)+" day SMA", label2=str(n2)+" day SMA")
    return cross


def stockhood_main(stockTicker, n1, n2, days, direction=""):
    """Determine if a golden/death cross has occured for a specified stock in the last X trading days

    Args:
        stockTicker(str): Symbol of the stock we're querying
        n1(int): Specifies the short-term indicator as an X-day moving average.
        n2(int): Specifies the long-term indicator as an X-day moving average.
                 (n1 should be smaller than n2 to produce meaningful results, e.g n1=50, n2=200)
        days(int): Specifies the maximum number of days that the cross can occur by
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwaords cross. Optional, used for printing purposes

    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
        False if direction == "above" and five_year_check(stockTicker) returns False, meaning that we're considering whether to
            buy the stock but it hasn't risen overall in the last five years, suggesting it contains fundamental issues
    """
    if(direction == "above"):
        print("Direction Above!")
        return False
    
    history = get_historicals(stockTicker, "day", "year", "regular")

    #Couldn't get pricing data
    if(history is None or None in history):
        print("No History!")
        return False
    print('First')
    closingPrices = []
    dates = []
    print('Second')
    for item in history:
        closingPrices.append(float(item['close_price']))
        dates.append(item['begins_at'])
    price = pd.Series(closingPrices)
    dates = pd.Series(dates)
    dates = pd.to_datetime(dates)
    cross = 0
    print(stockTicker)
    print(price)
    print(dates)
    sma1 = ta.volatility.bollinger_mavg(price, int(n1), False)
    sma2 = ta.volatility.bollinger_mavg(price, int(n2), False)
    series = [price.rename("Price"), sma1.rename("Indicator1"), sma2.rename("Indicator2"), dates.rename("Dates")]
    df = pd.concat(series, axis=1)
    print('\nPercentage Change 253 Days:')
    if closingPrices[0] != 0:
        print((closingPrices[252] - closingPrices[0]) / closingPrices[0] * 100)
        print(closingPrices[252] - closingPrices[0])
        if ((closingPrices[252] - closingPrices[0]) / closingPrices[0] * 100) > 15.00:
            cross = ((closingPrices[252] - closingPrices[0]) / closingPrices[0] * 100)
            print('TAKE ME 253 Day Mover!\n') 
    else:
        print("Starting Close Price was 0.00\n")
    print('\nPercentage Change 30 Days:')
    if closingPrices[0] != 0:
        print((closingPrices[252] - closingPrices[222]) / closingPrices[222] * 100)
        print(closingPrices[252] - closingPrices[222])
        if ((closingPrices[252] - closingPrices[222]) / closingPrices[222] * 100) > 15.00:
            cross = ((closingPrices[252] - closingPrices[222]) / closingPrices[222] * 100)
            print('TAKE ME 30 Day MOVER!\n') 
    else:
        print("Starting Close Price was 0.00\n")   

    print('\nPercentage Change 15 Days:')
    if closingPrices[0] != 0:
        print((closingPrices[252] - closingPrices[237]) / closingPrices[237] * 100)
        print(closingPrices[252] - closingPrices[237])
        if ((closingPrices[252] - closingPrices[237]) / closingPrices[237] * 100) > 15.00:
            cross = ((closingPrices[252] - closingPrices[237]) / closingPrices[237] * 100)
            print('TAKE ME 15 Day MOVER!\n') 
    else:
        print("Starting Close Price was 0.00\n")       

    print('\nPercentage Change 7 Days:')
    if closingPrices[0] != 0:
        print((closingPrices[252] - closingPrices[245]) / closingPrices[245] * 100)
        print(closingPrices[252] - closingPrices[245])
        if ((closingPrices[252] - closingPrices[245]) / closingPrices[245] * 100) > 15.00:
            cross = ((closingPrices[252] - closingPrices[245]) / closingPrices[245] * 100)
            print('TAKE ME 7 Day MOVER!\n') 
    else:
        print("Starting Close Price was 0.00\n")    

    print('\nPercentage Change 3 Days:')
    if closingPrices[0] != 0:
        print((closingPrices[252] - closingPrices[249]) / closingPrices[249] * 100)
        print(closingPrices[252] - closingPrices[249])
        if ((closingPrices[252] - closingPrices[249]) / closingPrices[249] * 100) > 15.00:
            cross = ((closingPrices[252] - closingPrices[249]) / closingPrices[249] * 100)
            print('TAKE ME 3 Day MOVER!\n') 
    else:
        print("Starting Close Price was 0.00\n")            

    print('Third')
    return cross

def stockhood_main2(stockTicker, intervals, upPerc, downPerc):
    """
    This will take into account how far you would like to go in 5 minute intervals starting from the latest 5 minute candle
    """  
    try:
        history = get_historicals(stockTicker, "5minute", "day", "regular")
    except:
        print('This is the Exception')
    #Couldn't get pricing data
    if(history is None or None in history):
        return False
    closingPrices = []
    dates = []
    for item in history:
        closingPrices.append(float(item['close_price']))
        dates.append(item['begins_at'])

    num = len(closingPrices)

    #Positive?
    if closingPrices[0] != 0:
        if ((closingPrices[num - 1] - closingPrices[num - (int(intervals) + 1)]) / closingPrices[num - (int(intervals) + 1)] * 100) > float(upPerc):
            print((closingPrices[num - 1] - closingPrices[num - (int(intervals) + 1)]) / closingPrices[num - (int(intervals) + 1)] * 100)
            print(stockTicker)
            print('+++This Stock is Rising Fast!+++\n') 

    #Negative?
    if closingPrices[0] != 0:
        if (((closingPrices[num - 1] - closingPrices[num - int(intervals)]) / closingPrices[num - int(intervals)] * 100) < (0 - float(downPerc))):
            print((closingPrices[num - 1] - closingPrices[num - int(intervals)]) / closingPrices[num - int(intervals)] * 100)
            print(stockTicker)
            print('---Drop Alert!---\n') 



def stockhood_goldencross(stockTicker, n1, n2, days, direction=""):
    """
    Determine if a golden/death cross has occured for a specified stock in the last X trading days
    Args:
        stockTicker(str): Symbol of the stock we're querying
        n1(int): Specifies the short-term indicator as an X-day moving average.
        n2(int): Specifies the long-term indicator as an X-day moving average.
                 (n1 should be smaller than n2 to produce meaningful results, e.g n1=50, n2=200)
        days(int): Specifies the maximum number of days that the cross can occur by
        direction(str): "above" if we are searching for an upwards cross, "below" if we are searching for a downwards cross. Optional, used for printing purposes
    Returns:
        1 if the short-term indicator crosses above the long-term one
        0 if there is no cross between the indicators
        -1 if the short-term indicator crosses below the long-term one
        False if direction == "above" and five_year_check(stockTicker) returns False, meaning that we're considering whether to
        buy the stock but it hasn't risen overall in the last five years, suggesting it contains fundamental issues.
    """
    
    history = get_historicals(stockTicker, "day", "year", "regular")

    #Couldn't get pricing data
    if(history is None or None in history):
        return False
    
    closingPrices = []
    dates = []
    for item in history:
        closingPrices.append(float(item['close_price']))
        dates.append(item['begins_at'])
    price = pd.Series(closingPrices)
    dates = pd.Series(dates)
    dates = pd.to_datetime(dates)
    sma1 = ta.volatility.bollinger_mavg(price, int(n1), False)
    sma2 = ta.volatility.bollinger_mavg(price, int(n2), False)
    series = [price.rename("Price"), sma1.rename("Indicator1"), sma2.rename("Indicator2"), dates.rename("Dates")]
    df = pd.concat(series, axis=1)
    cross = get_last_crossing(df, days, symbol=stockTicker, direction=direction)
    

    show_plot(price, sma1, sma2, dates, symbol=stockTicker, label1=str(n1)+" day SMA", label2=str(n2)+" day SMA")
    return cross

def sell_holdings(symbol, holdings_data):
    """ Place an order to sell all holdings of a stock.

    Args:
        symbol(str): Symbol of the stock we want to sell
        holdings_data(dict): dict obtained from get_modified_holdings() method
    """
    shares_owned = int(float(holdings_data[symbol].get("quantity")))
    if not debug:
        r.order_sell_market(symbol, shares_owned)
    print("####### Selling " + str(shares_owned) + " shares of " + symbol + " #######")

def buy_holdings(potential_buys, profile_data, holdings_data):
    """ Places orders to buy holdings of stocks. This method will try to order
        an appropriate amount of shares such that your holdings of the stock will
        roughly match the average for the rest of your portfoilio. If the share
        price is too high considering the rest of your holdings and the amount of
        buying power in your account, it will not order any shares.

    Args:
        potential_buys(list): List of strings, the strings are the symbols of stocks we want to buy
        symbol(str): Symbol of the stock we want to sell
        holdings_data(dict): dict obtained from r.build_holdings() or get_modified_holdings() method
    """
    cash = float(profile_data.get('cash'))
    portfolio_value = float(profile_data.get('equity')) - cash
    ideal_position_size = (safe_division(portfolio_value, len(holdings_data))+cash/len(potential_buys))/(2 * len(potential_buys))
    prices = r.get_latest_price(potential_buys)
    for i in range(0, len(potential_buys)):
        stock_price = float(prices[i])
        if(ideal_position_size < stock_price < ideal_position_size*1.5):
            num_shares = int(ideal_position_size*1.5/stock_price)
        elif (stock_price < ideal_position_size):
            num_shares = int(ideal_position_size/stock_price)
        else:
            print("####### Tried buying shares of " + potential_buys[i] + ", but not enough buying power to do so#######")
            break
        print("####### Buying " + str(num_shares) + " shares of " + potential_buys[i] + " #######")
        if not debug:
            r.order_buy_market(potential_buys[i], num_shares)

def SMAMeanReversion():
    ticker = "AMC"
    sma = 50
    threshold = 0.1
    shorts=True

    history = get_historicals(ticker, "day", "5year", "regular")

    #Couldn't get pricing data
    if(history is None or None in history):
        return False

    data = pd.DataFrame.from_dict(history)
    print(data)
    data['SMA'] = data['close_price'].rolling(sma).mean()
    data['extension'] = (data['close_price'].astype(float) - data['SMA'].astype(float)) / data['SMA'].astype(float)
    print(data)
    data['position'] = np.nan
    data['position'] = np.where(data['extension']<-threshold,1, data['position'])
    if shorts:
        data['position'] = np.where(data['extension']>threshold, -1, data['position'])
    print("1111")
    print(" ")
    print(data)
    data['position'] = np.where(np.abs(data['extension'].astype(float))<0.01,0, data['position'].astype(float))
    data['position'] = data['position'].ffill().fillna(0)
    
    # Calculate returns and statistics
    data['returns'] = data['close_price'].astype(float) / data['close_price'].shift(1).astype(float)
    data['log_returns'] = np.log(data['returns'])
    data['strat_returns'] = data['position'].shift(1).astype(float) * data['returns'].astype(float)
    data['strat_log_returns'] = data['position'].shift(1).astype(float) * data['log_returns'].astype(float)
    data['cum_returns'] = np.exp(data['log_returns'].cumsum())
    data['strat_cum_returns'] = np.exp(data['strat_log_returns'].cumsum())
    data['peak'] = data['cum_returns'].cummax()
    data['strat_peak'] = data['strat_cum_returns'].cummax()
    colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
    fig, ax = plt.subplots(3, figsize=(10, 8), sharex=True)

    ax[1].plot(data['extension']*100, label='Extension', color=colors[0])
    ax[1].axhline(threshold*100, linestyle='--', color=colors[1])
    ax[1].axhline(-threshold*100, label='Threshold', linestyle='--', color=colors[1])
    ax[1].axhline(0, label='Neutral', linestyle=':', color='k')
    ax[1].set_title('Price Extension and Buy/Sell Thresholds')
    ax[1].set_ylabel(f'Extension (%)')
    ax[1].legend(bbox_to_anchor=[1, 0.75])
    ax[2].plot(data['position'])
    ax[2].set_xlabel('Date')
    ax[2].set_title('Position')
    ax[2].set_yticks([-1, 0, 1])
    ax[2].set_yticklabels(['Short', 'Neutral', 'Long'])
    plt.tight_layout()
    plt.show()


    print(data.dropna().tail(30))
    print(data['returns'])
    print(data['extension'].tail(30))
    return data.dropna()

def signal():
    ticker = "AMC"
    sma = 50
    threshold = 0.1
    shorts=True

    history = get_historicals(ticker, "day", "5year", "regular")

    #Couldn't get pricing data
    if(history is None or None in history):
        return False

    data = pd.DataFrame.from_dict(history)
    width = 0.0003 # 3 pips Gap example for Hourly OHLC data

    print(data)        
    return data

#CHATGPT
            
def crosssectionalmomentumandmeanreversionstrategies():

    # Define a list of stocks including AMC and other assets
    stock_symbols = ['AMC', 'AAPL', 'MSFT', 'GOOGL', 'TSLA']  # Add more stocks as needed

    # Download historical price data for the specified stocks
    data = yf.download(stock_symbols, start='2022-01-01', end='2023-01-01')

    # Calculate daily returns for each stock
    returns = data['Adj Close'].pct_change()

    # Define parameters for the strategies
    lookback_period = 20  # Adjust this as needed
    momentum_threshold = 0.02  # Adjust this as needed
    mean_reversion_threshold = -0.01  # Adjust this as needed

    # Cross-Sectional Momentum Strategy
    momentum_rank = returns.rolling(lookback_period).mean().rank(axis=1, ascending=False)
    momentum_signal = np.where(momentum_rank <= len(stock_symbols) * momentum_threshold, 1, 0)

    # Cross-Sectional Mean Reversion Strategy
    mean_reversion_rank = returns.rolling(lookback_period).mean().rank(axis=1, ascending=True)
    mean_reversion_signal = np.where(mean_reversion_rank <= len(stock_symbols) * mean_reversion_threshold, 1, 0)

    # Backtest the strategies
    momentum_returns = momentum_signal * returns.values
    mean_reversion_returns = mean_reversion_signal * returns.values

    # Calculate the cumulative returns for the portfolio
    portfolio_momentum_returns = momentum_returns.sum(axis=1)
    portfolio_mean_reversion_returns = mean_reversion_returns.sum(axis=1)

    portfolio_momentum_cumulative_returns = (1 + portfolio_momentum_returns).cumprod().tolist()
    portfolio_mean_reversion_cumulative_returns = (1 + portfolio_mean_reversion_returns).cumprod().tolist()

    # Convert the index and data to lists
    data_index = data.index.tolist()

    # Plot the cumulative returns
    plt.figure(figsize=(12, 6))

    # Plot Cross-Sectional Momentum
    plt.subplot(2, 1, 1)
    plt.plot(data_index, portfolio_momentum_cumulative_returns, label='Cross-Sectional Momentum')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()

    # Plot Cross-Sectional Mean Reversion
    plt.subplot(2, 1, 2)
    plt.plot(data_index, portfolio_mean_reversion_cumulative_returns, label='Cross-Sectional Mean Reversion')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()

    # Add labels for stock symbols
    for symbol in stock_symbols:
        plt.text(data_index[-1], 1, symbol)

    plt.tight_layout()
    plt.show()

def timeseriesmomentummeanreversion(stockTicker, startDate, endDate):
    '''
    Time Series Momentum and Mean Reversion are two different trading strategies used in financial markets to take advantage of price movements. Here's a brief definition of each:

    Time Series Momentum:

    Time Series Momentum, often referred to as trend-following or momentum trading, is a strategy based on the belief that assets that have shown recent price strength or weakness will 
    continue to perform in the same direction for a certain period. Traders following this strategy typically buy or hold assets that have exhibited positive price momentum (upward trends) 
    and sell or avoid assets with negative momentum (downtrends). It's grounded in the notion that "the trend is your friend." Time Series Momentum traders often use technical indicators 
    and moving averages to identify trends and make trading decisions.

    Mean Reversion:

    Mean Reversion is a strategy based on the idea that asset prices tend to revert to their historical average or mean over time. In mean reversion trading, when an asset's price 
    deviates significantly from its historical mean (either positively or negatively), traders anticipate that the price will move back towards the mean. This strategy involves buying 
    assets that are undervalued or have seen recent price declines and selling assets that are overvalued or have experienced significant price gains. Mean reversion strategies often use 
    statistical tools to identify deviations from the mean and determine entry and exit points.
    '''
    #history = get_historicals(stockTicker, "day", "5year", "regular")
    
       # Download historical AMC price data from Yahoo Finance
    amc = yf.download(stockTicker, start=startDate, end=endDate)

    # Calculate daily returns
    amc['Returns'] = amc['Adj Close'].pct_change()

    # Define parameters for the strategies
    lookback_period = 20  # Adjust this as needed
    momentum_threshold = 0.02  # Adjust this as needed
    mean_reversion_threshold = 0.01  # Adjust this as needed

    # Time Series Momentum Strategy
    amc['Momentum_Signal'] = np.where(amc['Returns'].rolling(lookback_period).sum() > momentum_threshold, 1, 0)

    # Mean Reversion Strategy
    amc['Mean_Reversion_Signal'] = np.where(amc['Returns'].rolling(lookback_period).mean() > mean_reversion_threshold, 1, 0)

    # Backtest the strategies
    amc['Momentum_Returns'] = amc['Returns'] * amc['Momentum_Signal'].shift(1).values
    amc['Mean_Reversion_Returns'] = amc['Returns'] * amc['Mean_Reversion_Signal'].shift(1).values

    # Calculate cumulative returns
    amc['Momentum_Cumulative_Returns'] = (1 + amc['Momentum_Returns']).cumprod()
    amc['Mean_Reversion_Cumulative_Returns'] = (1 + amc['Mean_Reversion_Returns']).cumprod()

    # Convert the index and data to lists before plotting
    index_list = amc.index.tolist()
    momentum_cumulative_returns_list = amc['Momentum_Cumulative_Returns'].tolist()
    mean_reversion_cumulative_returns_list = amc['Mean_Reversion_Cumulative_Returns'].tolist()


    plt.figure(figsize=(12, 6))
    plt.plot(index_list, momentum_cumulative_returns_list, label='Momentum')
    plt.plot(index_list, mean_reversion_cumulative_returns_list, label='Mean Reversion')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.title(stockTicker + ' Time Series Momentum vs. Mean Reversion Strategy')
    plt.show()


def gapupmomentum():   
    '''
    Gap-Up Momentum, in the context of trading and finance, refers to a trading strategy that takes advantage of a significant price gap (or "gap-up") in a financial instrument's price at the market open. This strategy is based on the idea that a large upward price gap often indicates strong bullish sentiment and can lead to further price momentum in the same direction. Here are the key components of Gap-Up Momentum:

    Price Gap: A price gap occurs when there is a noticeable difference between a financial instrument's closing price from the previous day and its opening price on the current day. In the case of Gap-Up Momentum, the opening price is significantly higher than the previous day's closing price.

    Bullish Sentiment: Gap-Up Momentum traders believe that the gap-up is a sign of strong bullish sentiment. This sentiment may be driven by positive news, earnings reports, or other market events that occurred after the previous day's close.

    Entry and Exit: Traders employing Gap-Up Momentum strategies typically aim to enter positions shortly after the market open when the gap-up occurs. They anticipate that the price will continue to move in the same direction as the gap. They often set specific entry and exit criteria to manage the trade.

    Volatility: Gap-Up Momentum can be associated with increased volatility, as the market reacts to the new information or events driving the price gap. Traders should be prepared for price swings and adjust their risk management strategies accordingly.

    Risk Management: Effective risk management is crucial in Gap-Up Momentum trading. Traders often use stop-loss orders to limit potential losses if the trade moves against them. They may also set profit targets to lock in gains.

    Backtesting: Traders may use historical data to backtest Gap-Up Momentum strategies, allowing them to assess the historical performance of such strategies in different market conditions.

    Monitoring: Gap-Up Momentum traders continuously monitor their positions and the market to make timely decisions. They may exit positions if the momentum starts to wane or if new information changes the sentiment.
    '''
    # Define the stock symbol (e.g., AMC) and the date range
    stock_symbol = "AMC"
    start_date = "2022-01-01"
    end_date = "2023-01-01"

    # Download historical price data for AMC
    amc = yf.download(stock_symbol, start=start_date, end=end_date)

    # Calculate the price gap at the open
    amc['Price_Gap'] = amc['Open'] / amc['Close'].shift(1) - 1

    # Define a threshold for gap-up, e.g., 1% gap-up
    gap_up_threshold = 0.01

    # Create a signal for gap-up based on the threshold
    amc['Gap_Up_Signal'] = (amc['Price_Gap'] > gap_up_threshold).astype(int)

    # Backtest the Gap-Up Momentum strategy
    amc['Returns'] = amc['Adj Close'].pct_change()
    amc['Strategy_Returns'] = amc['Gap_Up_Signal'].shift(1).values * amc['Returns']

    # Calculate cumulative returns
    amc['Cumulative_Returns'] = (1 + amc['Strategy_Returns']).cumprod()

    data_index = amc.index.tolist()
    cumulative_returns = amc['Cumulative_Returns'].tolist()

    # Plot the cumulative returns
    plt.figure(figsize=(12, 6))
    plt.plot(data_index, cumulative_returns, label='Gap-Up Momentum')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.title('AMC Gap-Up Momentum Strategy')
    plt.show()


def statisticalarbitrage():    
    '''
    Select a Correlated Asset: Choose a stock that is correlated with AMC. For example, let's use GME (GameStop) as the correlated asset, given their historical connection.

    Download Historical Price Data: Use the Yahoo Finance API (yfinance) to download historical price data for both AMC and GME.

    Calculate the Spread: Calculate the spread between the two assets. The spread can be calculated as the difference in their prices or as a z-score.

    Define Entry and Exit Conditions: Define conditions for entering and exiting the trade based on the spread. For example, you can enter when the spread deviates by a certain threshold from its mean and exit when it reverts to the mean.

    Backtest the Strategy: Apply the entry and exit conditions to the historical data to backtest the strategy.
    '''
    # Define the stock symbols (AMC and GME) and the date range
    amc_symbol = "AMC"
    gme_symbol = "GME"
    start_date = "2022-01-01"
    end_date = "2023-01-01"

    # Download historical price data for AMC and GME
    amc_data = yf.download(amc_symbol, start=start_date, end=end_date)
    gme_data = yf.download(gme_symbol, start=start_date, end=end_date)

    # Calculate the spread (difference in prices)
    spread = amc_data['Adj Close'] - gme_data['Adj Close']

    # Calculate z-score for the spread
    spread_mean = spread.rolling(20).mean()
    spread_std = spread.rolling(20).std()
    z_score = (spread - spread_mean) / spread_std

    # Define entry and exit thresholds (you can adjust these)
    entry_threshold = 1.0  # Example entry threshold
    exit_threshold = 0.0   # Example exit threshold

    # Create signals for entry and exit
    entry_signal = np.where(z_score > entry_threshold, 1, 0)
    exit_signal = np.where(z_score < exit_threshold, 1, 0)

    # Calculate daily returns for each asset
    amc_returns = amc_data['Adj Close'].pct_change()
    gme_returns = gme_data['Adj Close'].pct_change()

    # Calculate strategy returns
    strategy_returns = (entry_signal - exit_signal) * (amc_returns - gme_returns)

    # Calculate cumulative returns
    cumulative_returns = (1 + strategy_returns).cumprod().tolist()

    # Convert the index to a list
    data_index = amc_data.index.tolist()

    # Plot the cumulative returns
    plt.figure(figsize=(12, 6))
    plt.plot(data_index, cumulative_returns, label='Pairs Trading Strategy')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Returns')
    plt.legend()
    plt.title('AMC vs. GME Pairs Trading Strategy')
    plt.show()

def weightedaverageprice():   

#To determine the weighted average price of a stock like AMC (AMC Entertainment Holdings, Inc.), you need to have information about the quantity 
#(number of shares) and the price of each transaction. The weighted average price is calculated by multiplying the quantity by the price for each transaction,
#summing these products, and then dividing by the total quantity. Here's a Python code example to calculate the weighted average price of AMC stock using sample transaction data:

    # Sample transaction data (date, quantity, price)
    transactions = [
        ('2023-10-01', 100, 50.25),  # Date, Quantity, Price
        ('2023-10-02', 150, 51.20),
        ('2023-10-03', 75, 49.80),
        ('2023-10-04', 200, 48.90),
    ]

    # Initialize variables to calculate the weighted average
    total_quantity = 0
    weighted_price_sum = 0

    # Calculate the weighted average price
    for date, quantity, price in transactions:
        total_quantity += quantity
        weighted_price_sum += quantity * price

    # Check if there are any transactions
    if total_quantity > 0:
        weighted_average_price = weighted_price_sum / total_quantity
        print(f'Weighted Average Price of AMC stock: ${weighted_average_price:.2f}')
    else:
        print('No transactions found.')

    # Output:
    # Weighted Average Price of AMC stock: $50.78


def goldencrossup():
    # Define the stock symbol (AMC) and the date range
    stock_symbol = "AMC"
    start_date = "2022-01-01"
    end_date = "2023-01-01"

    # Download historical price data for AMC
    amc_data = yf.download(stock_symbol, start=start_date, end=end_date)

    # Calculate the 50-day and 200-day simple moving averages
    amc_data['50_SMA'] = amc_data['Adj Close'].rolling(window=50).mean()
    amc_data['200_SMA'] = amc_data['Adj Close'].rolling(window=200).mean()

    # Create a signal for the Golden Cross
    amc_data['Golden_Cross_Signal'] = 0
    amc_data.loc[amc_data['50_SMA'] > amc_data['200_SMA'], 'Golden_Cross_Signal'] = 1

    # Plot the AMC stock price and moving averages
    plt.figure(figsize=(12, 6))
    plt.plot(amc_data.index, amc_data['Adj Close'], label='AMC Stock Price')
    plt.plot(amc_data.index, amc_data['50_SMA'], label='50-Day SMA', linestyle='--')
    plt.plot(amc_data.index, amc_data['200_SMA'], label='200-Day SMA', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Plot the Golden Cross points
    cross_points = amc_data[amc_data['Golden_Cross_Signal'] == 1]
    plt.scatter(cross_points.index, cross_points['50_SMA'], marker='^', color='green', label='Golden Cross (50 > 200)')
    plt.title('AMC Golden Cross Analysis')
    plt.show()

def goldencrossdown():
    # Define the stock symbol (AMC) and the date range
    stock_symbol = "AMC"
    start_date = "2022-01-01"
    end_date = "2023-01-01"

    # Download historical price data for AMC
    amc_data = yf.download(stock_symbol, start=start_date, end=end_date)

    # Calculate the 50-day and 200-day simple moving averages
    amc_data['50_SMA'] = amc_data['Adj Close'].rolling(window=50).mean()
    amc_data['200_SMA'] = amc_data['Adj Close'].rolling(window=200).mean()

    # Create a signal for the Golden Cross Down
    amc_data['Golden_Cross_Signal'] = 0
    amc_data.loc[amc_data['50_SMA'] < amc_data['200_SMA'], 'Golden_Cross_Signal'] = -1

    # Plot the AMC stock price and moving averages
    plt.figure(figsize=(12, 6))
    plt.plot(amc_data.index, amc_data['Adj Close'], label='AMC Stock Price')
    plt.plot(amc_data.index, amc_data['50_SMA'], label='50-Day SMA', linestyle='--')
    plt.plot(amc_data.index, amc_data['200_SMA'], label='200-Day SMA', linestyle='--')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()

    # Plot the Golden Cross Down points
    cross_points = amc_data[amc_data['Golden_Cross_Signal'] == -1]
    plt.scatter(cross_points.index, cross_points['50_SMA'], marker='v', color='red', label='Golden Cross Down (50 < 200)')
    plt.title('AMC Golden Cross Down Analysis')
    plt.show()