import csv
#from dotenv import load_dotenv
import json
import os
import pdb
import requests
import datetime

def parse_response(response_text):

    # response_text can be either a raw JSON string or an already-converted dictionary

    if isinstance(response_text, str): # if not yet converted, then:
        response_text = json.loads(response_text) # convert string to dictionary

    results = []
    time_series_daily = response_text["Time Series (Daily)"] #> a nested dictionary
    for trading_date in time_series_daily: # FYI: can loop through a dictionary's top-level keys/attributes
        prices = time_series_daily[trading_date] #> {'1. open': '101.0924', '2. high': '101.9500', '3. low': '100.5400', '4. close': '101.6300', '5. volume': '22165128'}
        result = {
            "date": trading_date,
            "open": prices["1. open"],
            "high": prices["2. high"],
            "low": prices["3. low"],
            "close": prices["4. close"],
            "volume": prices["5. volume"]
        }
        results.append(result)
    return results

def write_prices_to_file(prices=[], filename="db/prices.csv"):
    csv_filepath = os.path.join(os.path.dirname(__file__), "..", filename)
    with open(csv_filepath, "w") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["timestamp", "open", "high", "low", "close", "volume"])
        writer.writeheader()
        for d in prices:
            row = {
                "timestamp": d["date"], # change attribute name to match project requirements
                "open": d["open"],
                "high": d["high"],
                "low": d["low"],
                "close": d["close"],
                "volume": d["volume"]
            }
            writer.writerow(row)


if __name__ == '__main__': # only execute if file invoked from the command-line, not when imported into other files, like tests

    #load_dotenv() # loads environment variables set in a ".env" file, including the value of the ALPHAVANTAGE_API_KEY variable

    api_key = os.environ.get("ALPHAVANTAGE_API_KEY") or "OOPS. Please set an environment variable named 'ALPHAVANTAGE_API_KEY'."
#    print(api_key)

    risk_input = input("Please indicate your risk tolerance level (low, medium, high): ")
    if risk_input == "low":
        risk_level = 1.0
    if risk_input == "medium":
        risk_level = 1.3
    if risk_input == "high":
        risk_level = 1.5
    if risk_input != "low" and risk_input != "medium" and risk_input != "high":
        quit("unrecognized input")
    symbol_list = input("Please input a stock symbol, or a list of stock symbol seperated by comma: ").split(",")

    for symbol in symbol_list:
#            symbol = input("Please input a stock symbol (e.g. 'NFLX') or enter 'quit' to quit the program: ") # input("Please input a stock symbol (e.g. 'NFLX'): ")
        symbol = symbol.strip()
        symbol = symbol.upper()
        if str(symbol) == "QUIT":
            print("You have now quit the program.")
            break
        elif len(symbol) > 8:
            print("check your symbol again, must be less than 8 characters/letters")
            pass
        else:
            try:
                float(symbol)
                quit(f"Symbol {symbol} is numeric. Stock symbols must be non-numeric")
            except Exception as e:
                pass
            # VALIDATE SYMBOL AND PREVENT UNECESSARY REQUESTS

            # ASSEMBLE REQUEST URL
            # ... see: https://www.alphavantage.co/support/#api-key

            request_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        #   request_url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=" + symbol + "&apikey=" + api_key

            # ISSUE "GET" REQUEST

            response = requests.get(request_url)
            if "Error Message" in response.text:
                print("Sorry, one or more of your entered stock symbols cannot be found, please check again")
                quit("Quit program...")
            # VALIDATE RESPONSE AND HANDLE ERRORS
            # ... todo

            # PARSE RESPONSE (AS LONG AS THERE ARE NO ERRORS)

            daily_prices = parse_response(response.text)

            # WRITE TO CSV
            filename_symbol = f"db/prices_{symbol.lower()}.csv"
            write_prices_to_file(prices=daily_prices, filename=filename_symbol)

            last_trading_date_prices = daily_prices[0]
        #   print(last_trading_date_prices)

            last_trading_date = last_trading_date_prices["date"]


            print(f"Stock: {symbol}")
            print(f"Run at {datetime.datetime.now().time()} on {datetime.date.today()}")
            # pdb.set_trace()
            print(f"Last data from {last_trading_date}")

            latest_close = float(daily_prices[0]["close"])
            latest_close_usd = "${0:,.2f}".format(latest_close)
            print(f"Latest close price: {latest_close_usd}")

            high_list = []
            for each_price in daily_prices:
                high_list.append(float(each_price["high"]))
            avg_high = sum(high_list)/len(high_list)
            avg_high_usd = "${0:,.2f}".format(avg_high)
            print(f"Recent Average High: {avg_high_usd}")

            low_list = []
            for each_price in daily_prices:
                low_list.append(float(each_price["low"]))
            avg_low = sum(low_list)/len(low_list)
            avg_low_usd = "${0:,.2f}".format(avg_low)
            print(f"Recent Average Low: {avg_low_usd}")


            if latest_close > (avg_high * (float(risk_level))):
                print("Recommendation: Sell. Because the latest close price exceeds the 'to-sell' threshold.")
            elif latest_close < (avg_low * (2 - float(risk_level))):
                print("Recommendation: Buy. Because the latest close price exceeds the 'to-buy' threshold.")
            else:
                print("Recommendation: Hold. There is no strong evidence to suggest a 'buy' or 'sell'.")
