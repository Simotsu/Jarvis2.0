from algos import *

#filler delete later
def show_algo1():
    print('algo1')

#Algo Menu Options Detailed:
def basicalgomenu_option1():
      ans4=input("Please enter the stock ticker: ")
      ans5=input("Please enter the start date in '2023-01-01' format: ")
      ans6=input("Please enter the end date in '2023-01-01' format: ")
      timeseriesmomentummeanreversion(ans4, ans5, ans6)

#Time-Series Questions
def show_showtimeseriesmomentummeanreversionquestions():
    print("\n Time-Series Momentum/Mean Reversion Selected")
    ans4=input("Please enter the stock ticker: ")
    ans5=input("Please enter the start date in '2023-01-01' format: ")
    ans6=input("Please enter the end date in '2023-01-01' format: ")
#Basic Algorithms Menu
def show_basicalgorithmmenu():
    print("Basic Algorithm Menu:")
    for key, value in basicalgomenu_options.items():
        print(f"{key}: {value[0]}")
    choice = input("What would you like to do? ")
    
    try:
        choice = int(choice)
        if choice in basicalgomenu_options:
            function = basicalgomenu_options[choice][1]
            if function is not None:
                function()  # Call the selected function
        else:
            print("Invalid choice. Please select a valid option.")
    except ValueError:
        print("Invalid input. Please enter a number.")

basicalgomenu_options = {
    1: ("Time-Series Momentum/Mean Reversion", basicalgomenu_option1),
    2: ("Cross-Sectional Momentum/Mean Reversion", show_algo1),
    3: ("Gap-up Momentum", show_algo1),
    4: ("Statistical Arbitrage", show_algo1),
    5: ("Weighted Average Price", show_algo1),
    6: ("Golden Cross Up", show_algo1),
    7: ("Golden Cross Down", show_algo1),
    8: ("Go Back", show_algo1)
}


#Main Algorithm Menu
def show_algorithmmenu():
    print("Main Algorithm Menu:")
    for key, value in algomenu_options.items():
        print(f"{key}: {value[0]}")
    choice = input("What would you like to do? ")
    
    try:
        choice = int(choice)
        if choice in algomenu_options:
            function = algomenu_options[choice][1]
            if function is not None:
                function()  # Call the selected function
        else:
            print("Invalid choice. Please select a valid option.")
    except ValueError:
        print("Invalid input. Please enter a number.")

algomenu_options = {
    1: ("Basic Algorithms", show_basicalgorithmmenu),
    2: ("Quantitative Algorithms", show_algo1),
    3: ("Percentage Algorithms(WiP)", show_basicalgorithmmenu),
    4: ("Visualize Stock", show_algo1),
    5: ("Volume Algorithms(WiP)", show_algo1),
    6: ("Social Algorithms(WiP)", show_algo1),
    7: ("Go Back", show_algo1)
}
