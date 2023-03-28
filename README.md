# stock-market-analysis
Stocks in "tickers" list are analyzed using several different stock analysis methods (name and deviation defined by the client). Recommends actions based on each analysis method, describes the best performing stock / method combination, and saves the results to results.json.


Getting Started:

1 Update file paths. The directories must exist and be accurate for app to run. Files do not need to exist and are created automatically if they don't.

2 alphavantage's stock market API is used (TIME_SERIES_DAILY_ADJUSTED). Developer needs to obtain an API key to use the app.

3 Free tier has limited requests. 500 per day and 5 requests per minute. The time.sleep() expression is used to prevent too many requests made per minute.
