import robin_stocks.robinhood as r
import pandas as pd
import numpy as np
import ta as ta
import time
import datetime
import pandas_datareader.data as web
import sys
import matplotlib.pyplot as plt
import matplotlib
from pandas.plotting import register_matplotlib_converters
from ta import *
from misc import *
from tradingstats import *
from config import *
from menu import *
from algos import *
from methods import *
from pandas import Series, DataFrame
from tkinter import *
import os
import time
import threading
import mplfinance as mpf
import requests

from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource
print(matplotlib.__version__)
ans=True

def show_hotstocks():                                                                                                                    
    register_matplotlib_converters()
    watchlist_symbols = get_watchlist_symbols()

    ans=input("""
This will calculate rising or falling stocks based on 5 minute intervals.
IE: 1 = 10 minutes | 2 = 15 minutes | 3 = 20 minutes | 4 = 25 minutes | etc...
How many 5 minute intervals?: """) 
    ans2=input("""
Please enter the percentage up you are looking for.
IE: 3 - Stock went up 3'%' over indicated 5 minute interval | 5 - Stock went up 5'%' over indicated 5 minute interval | etc..
What Percentage Up?: """)
    ans3=input("""
Please enter the percentage down you are looking for.
IE: 3 - Stock went down 3'%' over indicated 5 Minute Interval | 5 - Stock went down 5'%' over indicated 5 Minute Interval | etc..
What Percentage Down?: """) 
    for symbol in watchlist_symbols:
        stockhood_main2(symbol, ans, ans2, ans3)
        #potential_buys.append(symbol)
    if(len(potential_buys) > 0):
        if startbuying:
            print('okBUY')
        buy_holdings(potential_buys, profile_data, holdings_data)
        if(len(sells) > 0):
            update_trade_history(sells, holdings_data, "tradehistory.txt")
            print("----- Scan Complete -----\n")
    if debug:
        print("----- DEBUG MODE ON -----\n")

        
def show_watchlist():
    """
    If you sell a stock, this updates tradehistory.txt with information about the position,
    how much you've earned/lost, etc.
    """
                                                                                                                                                                             
    #register_matplotlib_converters()
    watchlist_symbols = get_watchlist_symbols()
    print("\n"
    "\n"

    " ▄████▄   █    ██  ██▀███   ██▀███  ▓█████  ███▄    █ ▄▄▄█████▓    █     █░ ▄▄▄     ▄▄▄█████▓ ▄████▄   ██░ ██  ██▓     ██▓  ██████ ▄▄▄█████▓\n"
    "▒██▀ ▀█   ██  ▓██▒▓██ ▒ ██▒▓██ ▒ ██▒▓█   ▀  ██ ▀█   █ ▓  ██▒ ▓▒   ▓█░ █ ░█░▒████▄   ▓  ██▒ ▓▒▒██▀ ▀█  ▓██░ ██▒▓██▒    ▓██▒▒██    ▒ ▓  ██▒ ▓▒\n"
    "▒▓█    ▄ ▓██  ▒██░▓██ ░▄█ ▒▓██ ░▄█ ▒▒███   ▓██  ▀█ ██▒▒ ▓██░ ▒░   ▒█░ █ ░█ ▒██  ▀█▄ ▒ ▓██░ ▒░▒▓█    ▄ ▒██▀▀██░▒██░    ▒██▒░ ▓██▄   ▒ ▓██░ ▒░\n"
    "▒▓▓▄ ▄██▒▓▓█  ░██░▒██▀▀█▄  ▒██▀▀█▄  ▒▓█  ▄ ▓██▒  ▐▌██▒░ ▓██▓ ░    ░█░ █ ░█ ░██▄▄▄▄██░ ▓██▓ ░ ▒▓▓▄ ▄██▒░▓█ ░██ ▒██░    ░██░  ▒   ██▒░ ▓██▓ ░ \n"
    "▒ ▓███▀ ░▒▒█████▓ ░██▓ ▒██▒░██▓ ▒██▒░▒████▒▒██░   ▓██░  ▒██▒ ░    ░░██▒██▓  ▓█   ▓██▒ ▒██▒ ░ ▒ ▓███▀ ░░▓█▒░██▓░██████▒░██░▒██████▒▒  ▒██▒ ░ \n"
    "░ ░▒ ▒  ░░▒▓▒ ▒ ▒ ░ ▒▓ ░▒▓░░ ▒▓ ░▒▓░░░ ▒░ ░░ ▒░   ▒ ▒   ▒ ░░      ░ ▓░▒ ▒   ▒▒   ▓▒█░ ▒ ░░   ░ ░▒ ▒  ░ ▒ ░░▒░▒░ ▒░▓  ░░▓  ▒ ▒▓▒ ▒ ░  ▒ ░░   \n"
    "  ░  ▒   ░░▒░ ░ ░   ░▒ ░ ▒░  ░▒ ░ ▒░ ░ ░  ░░ ░░   ░ ▒░    ░         ▒ ░ ░    ▒   ▒▒ ░   ░      ░  ▒    ▒ ░▒░ ░░ ░ ▒  ░ ▒ ░░ ░▒  ░ ░    ░    \n"
    "░         ░░░ ░ ░   ░░   ░   ░░   ░    ░      ░   ░ ░   ░           ░   ░    ░   ▒    ░      ░         ░  ░░ ░  ░ ░    ▒ ░░  ░  ░    ░      \n"
    "░ ░         ░        ░        ░        ░  ░         ░                 ░          ░  ░        ░ ░       ░  ░  ░    ░  ░ ░        ░           \n"
    "░                                                                                            ░                                              \n"
    "\n"
    "\n"     + str(watchlist_symbols) + "\n" + "\n" + "\n")
#execute the scan
#maybe get an input from user?
#scan_stocks()
#Log in to Robinhood

#try:
   #login = r.login(rh_username,rh_password)
#except:
#    print("Could not Log In!")
#Put your username and password in a config.py file in the same directory (see sample file)
'''
print("""
                                                                            
                                                                                                       
              JJJJJJJJJJJ                                                           iiii                   
              J:::::::::J                                                          i::::i                  
              J:::::::::J                                                           iiii                   
              JJ:::::::JJ                                                                                  
                J:::::J  aaaaaaaaaaaaa  rrrrr   rrrrrrrrrvvvvvvv           vvvvvvviiiiiii     ssssssssss   
                J:::::J  a::::::::::::a r::::rrr:::::::::rv:::::v         v:::::v i:::::i   ss::::::::::s  
                J:::::J  aaaaaaaaa:::::ar:::::::::::::::::rv:::::v       v:::::v   i::::i ss:::::::::::::s 
                J:::::j           a::::arr::::::rrrrr::::::rv:::::v     v:::::v    i::::i s::::::ssss:::::s
                J:::::J    aaaaaaa:::::a r:::::r     r:::::r v:::::v   v:::::v     i::::i  s:::::s  ssssss 
    JJJJJJJ     J:::::J  aa::::::::::::a r:::::r     rrrrrrr  v:::::v v:::::v      i::::i    s::::::s      
    J:::::J     J:::::J a::::aaaa::::::a r:::::r               v:::::v:::::v       i::::i       s::::::s   
    J::::::J   J::::::Ja::::a    a:::::a r:::::r                v:::::::::v        i::::i ssssss   s:::::s 
    J:::::::JJJ:::::::Ja::::a    a:::::a r:::::r                 v:::::::v        i::::::is:::::ssss::::::s
     JJ:::::::::::::JJ a:::::aaaa::::::a r:::::r                  v:::::v         i::::::is::::::::::::::s 
       JJ:::::::::JJ    a::::::::::aa:::ar:::::r                   v:::v          i::::::i s:::::::::::ss  
         JJJJJJJJJ       aaaaaaaaaa  aaaarrrrrrr                    vvv           iiiiiiii  sssssssssss    


     Coded By: Simotsu@gmail.com
    """)
while ans:
    print ("""

    Main Menu:
    1: My Stocks
    2: My Watchlist
    3: Stock Algorithms
    4: Visualize Stock
    5: Initialize Bot
    6: Backtesting 
    7: Stock Lookup
    8: Earnings Reports
    9: Quit
    10: Test
    11: Stock Scanner
    """)
    ans=input("What would you like to do? ") 
    #Portfoilio Selected
    if ans=="1": 
        try:
            show_portfolio()
        except:
            print("Could not show Portfolio!")
    #Watchlist Selected
    elif ans=="2":
        try:
            show_watchlist()
        except:
            print("Could not show Watchlist!")
        

    #Stock Scanner Selected
    elif ans=="3":
    #This is sloppy need to put this somewhere else, maybe methods..
        print ("""
    Stock Algorithms Selected:
    Please Choose From The Following:
        A: Basic Algorithms
        B: Quantitative Algorithms
        C: Percentage Algorithms(WiP)
        D: Volume Algorithms(WiP)
        E: Social Algorithms(WiP)
        F: Go Back
        """)
        ans2=input("How would you like to scan? ") 
        if ans2=="A": 
            print("\n Algorithm Selected") 
            print ("""
            Please Choose From The Following:
                A: Time-Series Momentum/Mean Reversion
                B: Cross-Sectional Momentum/Mean Reversion
                C: Gap-up Momentum
                D: Statistical Arbitrage
                E: Weighted Average Price
                F: Golden Cross Up
                G: Golden Cross Down
                H: Go Back
            """)
            ans3=input("Which Algoritmic Pattern Would You Like To Implement? ") 
            if ans3=="A": 
                print("\n Time-Series Momentum/Mean Reversion Selected")
                ans4=input("Please enter the stock ticker: ")
                ans5=input("Please enter the start date in '2023-01-01' format: ")
                ans6=input("Please enter the end date in '2023-01-01' format: ")
                
                timeseriesmomentummeanreversion(ans4, ans5, ans6)
            if ans3=="B": 
                #print("\n Time-Series Momentum/Mean Reversion Selected in Depth") 
                #ans4=input("Please enter the stock ticker: ") 
                #ans5=input("Please enter SMA day count(20,30,50): ")
                #ans6=input("Please enter a time period(month, year, 5year): ")                 
                #ans7=input("Please enter the threshold(0.1, 0.12, 0.14): ") 
                #ans8=input("Please enter true or false for Short Positons: ") 
                #SMAMeanReversion()
                crosssectionalmomentumandmeanreversionstrategies()

            if ans3=="C": 
                gapupmomentum()
                print("\n Gap-up Momentum Selected")
            if ans3=="D": 
                statisticalarbitrage()
                print("\n Statistical Arbitrage Selected")
            if ans3=="E": 
                weightedaverageprice()
                print("\n Weighted Average Price Selected")
            if ans3=="F": 
                goldencrossup()
                print("\n Golden Cross Up Selected")
            if ans3=="G": 
                goldencrossdown()
                print("\n Golden Cross Down Selected")
#Quantitative
        if ans2=="B": 
            print("\n Quantitative Selected")
            print ("""
            Please Choose From The Following:
                A: Bi-Directional Encoder Representations from Transformers (BERT)
                B: Long Short Term Memory (LSTM)
                C: Gated Recurrent Units (GRU)
                D: Auto Regressive Integrated Moving Average (ARIMA)
                E: GAN
                F: Go Back
            """)
            ans3=input("Which Quantitative Strategy Would You Like To Implement? ") 
            if ans3=="A": 
                print("\n Bi-Directional Encoder Representations from Transformers (BERT) Selected")
            if ans3=="B": 
                print("\n Long Short Term Memory (LSTM) Selected") 
            if ans3=="C": 
                print("\n Gated Recurrent Units (GRU) Selected")
            if ans3=="D": 
                print("\n Auto Regressive Integrated Moving Average (ARIMA) Selected")
            if ans3=="E": 
                print("\n GAN Selected")
#Percentage
        if ans2=="C": 
            print("\n Percentage Selected")
            show_hotstocks()
            ans3=input("Which Quantitative Strategy Would You Like To Implement? ") 
            if ans3=="A": 
                print("\n Bi-Directional Encoder Representations from Transformers (BERT) Selected")
            if ans3=="B": 
                print("\n Long Short Term Memory (LSTM) Selected") 
            if ans3=="C": 
                print("\n Gated Recurrent Units (GRU) Selected")
            if ans3=="D": 
                print("\n Auto Regressive Integrated Moving Average (ARIMA) Selected")
            if ans3=="E": 
                print("\n GAN Selected")
#Volume
        if ans2=="D": 
            print("\n Volume Selected") 
            print ("""
            Please Choose From The Following:
                A: Volume 1
                B: Go Back
            """)
            ans3=input("Which Volume Search Would You Like To Implement? ") 
            if ans3=="A": 
                print("\n Volume 1 Selected")
            if ans3=="B": 
                print("\n Selected") 
            if ans3=="C": 
                print("\n Selected")
            if ans3=="D": 
                print("\n Selected")
            if ans3=="E": 
                print("\n Selected")
#Social
        if ans2=="E": 
            print("\n Social Selected")
            print ("""
            Please Choose From The Following:
                A: Twitter
                B: WSB
                C: Reddit
                D: Go Back
            """)
            ans3=input("Which Social Media Platform Search Would You Like To Implement? ") 
            if ans3=="A": 
                print("\n Twitter Selected")
            if ans3=="B": 
                print("\n Wall Street Bets Selected") 
            if ans3=="C": 
                print("\n Reddit Selected")
                show_redditsocial()
    #Visualize Stock Selected
    elif ans=="4":
    #Sloppy Needs to be put somewhere else. Just want method calls after.
        print ("""
    Visualize Stock Selected:
    Please Choose From The Following:
        A: Line Chart
        B: Candlestick Chart
        C: Bokeh's Chart
        D: Go Back
        """)
        ans3=input("Which option would you like to use: ") 
        if ans3=="A": 
            
            # Define the stock symbol (AMC) and the date range
            stock_symbol = "AMC"
            start_date = "2022-01-01"
            end_date = "2023-01-01"

            # Download historical price data for AMC
            amc = yf.download(stock_symbol, start=start_date, end=end_date)

            # Create a line chart
            plt.figure(figsize=(12, 6))
            plt.plot(amc.index, amc['Adj Close'], label='AMC Stock Price', color='blue')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.title(f'{stock_symbol} Stock Price Chart')
            plt.grid()
            plt.legend()

            # Show the chart
            plt.show()
            print("\n Line Chart")
        if ans3=="B": 
            stock_symbol = "AMC"
            start_date = "2022-01-01"
            end_date = "2023-01-01"
            # Download historical price data for AMC
            amc = yf.download(stock_symbol, start=start_date, end=end_date)

            # Create a candlestick chart
            mpf.plot(amc, type='candle', style='charles', title=f'{stock_symbol} Candlestick Chart', ylabel='Price')

            # Show the chart
            mpf.show()
            print("\n Candlestick Chart") 
        if ans3=="C": 
            # Define the stock symbol (AMC) and the date range
            stock_symbol = "AMC"
            start_date = "2022-01-01"
            end_date = "2023-01-01"

            # Download historical price data for AMC
            amc = yf.download(stock_symbol, start=start_date, end=end_date)

            # Create a Bokeh candlestick chart
            source = ColumnDataSource(data=dict(
                date=amc.index,
                open=amc['Open'],
                close=amc['Close'],
                high=amc['High'],
                low=amc['Low']
            ))

            p = figure(x_axis_type="datetime", title=f"{stock_symbol} Candlestick Chart", width=1000, height=400)
            p.segment(x0='date', x1='date', y0='low', y1='high', line_color="black", source=source)
            p.vbar(x='date', width=0.5, top='open', bottom='close', fill_color="green", line_color="black", source=source)

            # Customize the chart as needed (e.g., axes labels, grid, etc.)
            p.xaxis.axis_label = 'Date'
            p.yaxis.axis_label = 'Price'
            p.grid.grid_line_alpha = 0.3

            # Save the chart as an HTML file and display it
            output_file(f"{stock_symbol}_candlestick_chart.html")
            show(p)
            print("\n Bokeh's Chart")
                
    #Init Bot Selected
    elif ans =="5":
        print ("""
    Initialize Bot Selected:
    Please Choose From The Following:
        A: Blah
        B: Bleh
        C: Blep
        D: Blop
        E: Blup
        F: Go Back
        """)
        ans3=input("Which option would you like to use: ") 

        # Download historical data for a stock
        stock_symbol = 'F'
        stock_data = yf.download(stock_symbol, start='2022-01-01', end='2023-11-06')

        # Calculate moving averages
        stock_data['50_MA'] = stock_data['Close'].rolling(window=50).mean()
        stock_data['200_MA'] = stock_data['Close'].rolling(window=200).mean()

        # Implement the Golden Cross strategy
        stock_data['Signal'] = 0
        stock_data.loc[stock_data['50_MA'] > stock_data['200_MA'], 'Signal'] = 1

        # Buy and sell signals
        buy_signals = stock_data[stock_data['Signal'] == 1]
        sell_signals = stock_data[stock_data['Signal'] == 0]

        print(buy_signals)
        print(sell_signals)
    #Backtesting Selected
    elif ans =="6":
        print("\n Back Testing")
        #Learn how to implement backtesting stuffs
    #Stock Search
    elif ans =="7":
        try:
            show_stocksearch()
        except: 
            print("Error during Stock Search")
    #Earnings
    elif ans =="8":
        try:
            signal()
        except: 
            print("Error During Earnings Lookup")
    #Quit Selected
    elif ans =="9":
        print("\n Quit Selected")
        raise SystemExit
    #Test Selected
    elif ans =="10":
        print("\n Help/FAQS")
        print ("""


Help and Frequently Asked Questions:
    
    
  █████▒▄▄▄        █████    ██████ 
▓██   ▒▒████▄    ▒██▓  ██▒▒██    ▒ 
▒████ ░▒██  ▀█▄  ▒██▒  ██░░ ▓██▄   
░▓█▒  ░░██▄▄▄▄██ ░██  █▀ ░  ▒   ██▒
░▒█░    ▓█   ▓██▒░▒███▒█▄ ▒██████▒▒
 ▒ ░    ▒▒   ▓▒█░░░ ▒▒░ ▒ ▒ ▒▓▒ ▒ ░
 ░       ▒   ▒▒ ░ ░ ▒░  ░ ░ ░▒  ░ ░
 ░ ░     ░   ▒      ░   ░ ░  ░  ░  
             ░  ░    ░          ░  
                                   
1) When did you start trading?
    A) I started Trading February 2021.
2) Why did you start trading?
    b) I heard about the GME / AMC madness happening.
3) Insert More. :)
        """)
    #Quit if wrong input
    elif ans =="11":
        print("\n Stock Scanner")
        print ("""
        DA STOCK SCAN BITCH
        """)
        # Download a list of stock symbols or use your own
        stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

        # Define criteria for screening
        min_price = 100  # Minimum stock price
        min_volume = 1000000  # Minimum daily trading volume

        # Create a stock scanner
        for symbol in stock_symbols:
            stock_data = yf.Ticker(symbol)
            history = stock_data.history(period="1d")

            if history['Close'].iloc[0] > min_price and history['Volume'].iloc[0] > min_volume:
                print(f"{symbol} meets the criteria.")
    elif ans=="12":

        # Define a list of stock symbols to scan
        stock_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']

        # Define your screening criteria
        min_price = 100  # Minimum stock price
        min_volume = 1000000  # Minimum daily trading volume
        min_50sma_price_ratio = 1.05  # Minimum 50-day SMA to stock price ratio
        min_200sma_price_ratio = 1.02  # Minimum 200-day SMA to stock price ratio
        min_sales_growth = 5  # Minimum annual sales growth (%)
        min_earnings_growth = 5  # Minimum annual earnings growth (%)
        min_dividend_yield = 2  # Minimum dividend yield (%)

        # Function to get sector data using an API (e.g., Alpha Vantage)
        def get_sector(symbol):
            url = f"https://www.alphavantage.co/query?function=SECTOR&symbol={symbol}&apikey=N0T1A3DIQKU0QFVS"
            response = requests.get(url)
            data = response.json()
            if 'Meta Data' in data and 'Sector' in data['Meta Data']:
                return data['Meta Data']['Sector']
            else:
                return "Sector Not Found"

        # Create a function to perform the screening
        def stock_screening(symbol):
            # Download stock data
            stock_data = yf.Ticker(symbol)
    
            # Get historical data for the last 200 trading days
            history = stock_data.history(period="200d")

            # Check if the stock meets the criteria
            if (
                history['Close'].iloc[-1] > min_price and
                history['Volume'].iloc[-1] > min_volume and
                history['Close'].iloc[-1] > min_50sma_price_ratio * history['Close'].rolling(window=50).mean().iloc[-1] and
                history['Close'].iloc[-1] > min_200sma_price_ratio * history['Close'].rolling(window=200).mean().iloc[-1]

            ):
                # Retrieve additional data (Sales Growth, Earnings Growth, Dividend Yield, and Sector)
                sales_growth = 10  # Example: Replace with actual sales growth data
                earnings_growth = 8  # Example: Replace with actual earnings growth data
                dividend_yield = 2.5  # Example: Replace with actual dividend yield data
                sector = get_sector(symbol)

                # Check additional criteria
                if (
                    sales_growth > min_sales_growth and
                    earnings_growth > min_earnings_growth and
                    dividend_yield > min_dividend_yield and
                    sector == "Technology"  # Replace with your desired sector
                ):
                    return True

            return False

        # Perform the screening
        for symbol in stock_symbols:
            if stock_screening(symbol):
                print(f"{symbol} meets the criteria.")
    #Quit if wrong input
    elif ans !="":
        print("\n Wrong Input")   
    '''        
def show_menu():
    print("Main Menu:")
    for key, value in menu_options.items():
        print(f"{key}: {value[0]}")

menu_options = {
    1: ("My Stocks", show_portfolio),
    2: ("My Watchlist", show_watchlist),
    3: ("Stock Algorithms", show_algorithmmenu),
    4: ("Visualize Stock", show_portfolio),
    5: ("Initialize Bot", show_portfolio),
    6: ("Backtesting", show_portfolio),
    7: ("Stock Lookup", show_portfolio),
    8: ("Earnings Reports", show_portfolio),
    9: ("Quit", None),  # You can set the function to None to exit the menu
    10: ("Test", show_portfolio),
    11: ("Stock Scanner", show_portfolio)
}

while True:
    show_menu()
    choice = input("What would you like to do? ")
    
    try:
        choice = int(choice)
        if choice in menu_options:
            function = menu_options[choice][1]
            if function is not None:
                function()  # Call the selected function
            elif choice == 9:
                print("Goodbye!")
                break
        else:
            print("Invalid choice. Please select a valid option.")
    except ValueError:
        print("Invalid input. Please enter a number.")

