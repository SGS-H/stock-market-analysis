#BEFORE RUNNING - Update file paths and download necessary libraries. Make sure correct file paths are written into the app as well. Directories are not automatically created but files are

#alphaVantage access key ################
#LIMITED TO 5 API requests per minute and 500 requests per day
#example API URL:   https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=IBM&outputsize=compact&apikey=################



import json
import requests
import time
import os



#fn to assign a default value if variable is null
def isNull(test, default):
    if test is None:
        test = default
    elif test is not None:
        test = test
    return(test)
    


#fn to get percent change between starting and ending value    
def percentChange(start, end):
    change = float(((isNull(end,0) - isNull(start,0)) / isNull(start,0)) * 100)
    return(change) #returns percent return as a float... doesn't include percent sign
    
    
    
#fn to save a dictionary to json file
def saveResults(dictionaryName = {}):
    json.dump(dictionaryName, open("C:/Users/Username/Documents/stock-market-analysis/data/results.json", "w+"))
    


#fn to retrieve data from the API
def retrieveTickerData(tickerIndexPos):
    #get data and assign keys for loops
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + tickers[tickerIndexPos] + "&outputsize=compact&apikey=################"
    request = requests.get(url)
    dt_request = json.loads(request.text)
    
    
    #open the file in write/create mode
    csvFile = open("C:/Users/Username/Documents/stock-market-analysis/data/" + tickers[tickerIndexPos] + ".csv", "w+")
    lines = csvFile.readlines()
    
    #if there are no lines then create the file and append data to it
    if not lines:
        csvFile.write("date,price\n")
        csvLines = []
        for key2 in dt_request[key1]:
            csvLines.append(key2 + "," + dt_request[key1][key2][key3] + "\n")
        csvLines = csvLines[::-1]
        csvFile.writelines(csvLines)
        csvFile.mode = 'r'
        
    else:
        #get latest date
        latestDate = lines[-1].split(",")[tickerIndexPos]
    
        #append new lines to list
        newLines = []
        for key2 in dt_request[key1]: 
            if key2 == latestDate:
                break
            newLines.append(key2 + "," + dt_request[key1][key2][key3] + "\n")
    
        #correctly order list, then append data to csv file
        newLines = newLines[::-1]
        csvFile.mode = "a"
        csvFile.writelines(newLines)
    
    csvFile.close() #close csv file
    print("retrieved " + str(tickers[tickerIndexPos]) + "...")
    return





def movingAverage(tickerIndexPos, deviance = 0, methodName = "Moving Average"):
    #tickerIndexPos will select data for the specific ticker
    #deviance defines the amount of deviance to be used.

    #as per instructions: 0 = simpleMovingAverage, 2 = meanReversion, 5 = bollingerBands
    tickerIndex = 0 #track position
    isBought = 0 #track if stock is currently held
    moneyOwed = 0.00 #how much money is owed to someone else (because of short selling)
    initialPurchase = None #first time purchse price
    currentHoldingValue = None #value of the stock currently owned
    netChange = None #net change between single purchase and sale
    totalNetChange = None #net total change between all purchases and sales
    recommendedAction = None #action to take for today
    
    
    #load data from csv into a list
    file = open("C:/Users/Username/Documents/stock-market-analysis/data/" + tickers[tickerIndexPos] + ".csv") #open file by ticker name
    lines = file.readlines()[1:] #read each line in the file
    prices = [] #create list to store the lines as a float
    for line in lines:
        prices.append(float(line.split(",", 1)[1])) #convert to float
        
        
    #return total-$-change
    avg5DayPrice = ((prices[0] + prices[1] + prices[2] + prices[3] + prices[4]) / 5) #initial 5-day average for first 5 days of data tracking
    
    
    #begin buy if and sell if
    pricesCount = len(prices)
    for price in prices:
        if tickerIndex <= 4: #skip first 5 iterations since data is already stored in avg5DayPrice
            tickerIndex += 1
            continue
    
        else:
            currentPrice = price #get current price
            avg5DayPrice = ((prices[i - 5] + prices[i - 4] + prices[i - 3] + prices[i - 2] + prices[i - 1]) / 5) #get moving 5-day average for previous 5 days
        
        
            #purchase code
            if currentPrice < (avg5DayPrice * (1 - (deviance / 10))): #if currentPrice is less than 100% - deviance
                if isBought == 0: #need to not own the stock to buy into it
                    if initialPurchase is None:
                        initialPurchaes = currentPrice #if initialPurchase is null, assign it to current price (captures first purchase value)
                    currentHoldingValue = currentPrice #captures the current holding value
                    
                    if pricesCount == (tickerIndex - 2): #last iteration
                        recommendedAction = "Recommended Action:\tBuy Today:"
                    #print("Bought:\t$"+ str(round(currentHoldingValue,2))) #print the purchase price
                    isBought = 1 #set isBought = 1 (true) after a purchase is made
                
            
            #sell code
            elif currentPrice > (avg5DayPrice * (1 + (deviance / 10))): #if currentPrice is greater than 100% + deviance
                netChange = currentPrice - isNull(currentHoldingValue, 0) #get the net change for this sale
                totalNetChange = isNull(totalNetChange, 0.00) #set totalNetChange to 0.00 if it doesn't have a value yet
                totalNetChange += netChange #add sale value to totalNetChange
                
                if isBought == 1:
                    moneyOwed = moneyOwed
                    if pricesCount == (tickerIndex - 2): #last iteration
                        recommendedAction = "Recommended Action:\tSell Today:"
                    #print("Sell:\t$" + str(round(currentPrice,2)), "\nNet Change: $" + str(round(netChange,2)), "\n")
                if isBought == 0:
                    moneyOwed += netChange
                    if pricesCount == (tickerIndex - 2): #last iteration
                        recommendedAction = "Recommended Action:\tShort Sell Today"
                    #print("Shrt:\t$" + str(round(currentPrice,2)), "\nNet Change: $" + str(round(netChange,2)), "\n")
                isBought = 0 #set isBought = 0 (false) after a sale is made
                
            tickerIndex += 1
    
    if recommendedAction is None:
        recommendedAction = "Recommended Action:\tHold Stocks"
    print(methodName + " " + recommendedAction)    
    
    totalNetChange = isNull(totalNetChange, 0) - isNull(moneyOwed, 0) #total value of stocks minus how much money is owed due to borrowing to short sell
    return totalNetChange



def meanReversion(tickerIndexPos):
    netChange = movingAverage(tickerIndexPos, 2, "Mean Reversion")
    return netChange
 
  
    
def bollingerBands(tickerIndexPos):
    netChange = movingAverage(tickerIndexPos, 5, "Bollinger Bands")
    return netChange



def dollarCostAverage(tickerIndexPos):
    stocksOwned = 0 #number of stocks owned
    totalSpent = None #how much money has been spent on purchasing stocks
    latestPrice = 0.00
    
    file = open("C:/Users/Username/Documents/stock-market-analysis/data/" + tickers[tickerIndexPos] + ".csv") #open file by ticker name
    lines = file.readlines()[1:] #read each line in the file
    prices = [] #create list to store the lines as a float
    for line in lines:
        prices.append(float(line.split(",", 1)[1])) #convert to float
        
    for price in prices:
        stocksOwned += 1 #every day stock is purchased
        
        #how much has been spent on stocks
        totalSpent = isNull(totalSpent, 0.00)
        totalSpent += price
        
        latestPrice = price #get latest price
    
    return float(((stocksOwned * latestPrice) - totalSpent)) #returns the total value of stocks less the amount used to purchase them as a float
    


#tickers to analyze, and keys for the loop
#each of these ticker symbols can be replaced by any different, valid ticker on the stock market. Any number of tickers (1 or more) can be in the tickers list
tickers = ['BIPI', 'BMAQW', 'FRD', 'GLBLW', 'KKR', 'MSFT', 'NLY', 'PACX', 'SSNC', 'TSLA']
key1 = "Time Series (Daily)"
'''key2 "dates"'''
key3 = "4. close"
i = 0 #index position

bestNetChangeValue = 0 #track best net change for ticker/method combo
bestNetChangeMethod = ""
bestNetChangeTicker = ""

#create results dictionary
results = {"results": {}}

#create a placholder key for each ticker
for ticker in tickers:
    results["results"][ticker] = {}
    
    

#remove all csv and results data on previous analysis
'''
dir = "C:/Users/Username/Documents/stock-market-analysis/data"
for file in os.listdir(dir):
    os.remove(os.path.join(dir, file))
'''



#loop through eac ticker to retrieve data and analyze
for ticker in tickers:
    #get data then run analysis on it
    retrieveTickerData(i)
    maNetChange = movingAverage(i)
    mrNetChange = meanReversion(i)
    bbNetChange = bollingerBands(i)
    daNetChange = dollarCostAverage(i)
    
    
    #is moving average with this ticker the best performing ticker/method?
    if maNetChange > bestNetChangeValue:
        bestNetChangeValue = maNetChange
        bestNetChangeTicker = ticker
        bestNetChangeMethod = "Moving Average"
        
    #is mean reversion with this ticker the best performing ticker/method?
    if mrNetChange > bestNetChangeValue:
        bestNetChangeValue = mrNetChange
        bestNetChangeTicker = ticker
        bestNetChangeMethod = "Mean Reversion"
        
    #is bollinger bands with this ticker the best performing ticker/method?
    if bbNetChange > bestNetChangeValue:
        bestNetChangeValue = bbNetChange
        bestNetChangeTicker = ticker
        bestNetChangeMethod = "Bollinger Bands"
        
    #is dollar cost with this ticker the best performing ticker/method?
    if daNetChange > bestNetChangeValue:
        bestNetChangeValue = daNetChange
        bestNetChangeTicker = ticker
        bestNetChangeMethod = "Dollar Cost Averaging"
    
    
    #store results of each method/ticker combination into results dictionary
    results["results"][ticker] = {"Moving_Average": round(maNetChange, 2), "Mean_Reversion": round(mrNetChange, 2), "Bollinger_Bands": round(bbNetChange, 2), "Dollar_Cost_Average": round(daNetChange, 2)}
    
    i += 1
    time.sleep(.5)
    
    if i < len(tickers):
        print("retrieving next data set. please wait...\n")
        time.sleep(11.5) #sleep for 12 seconds to ensure enough time between requests
    if i >= len(tickers):
        print("retrieved final data set!\n")



#add best results method to results dict
results["results"]["bestPerformer"] = {"Method": bestNetChangeMethod, "Ticker": bestNetChangeTicker, "Value": round(bestNetChangeValue, 2)}

#save results to results.json file
saveResults(results)

#print best perfomer results to console
print(bestNetChangeMethod + " on " + bestNetChangeTicker + " is performing the best with a current holding value of $" + str(round(bestNetChangeValue, 2)))