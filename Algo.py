import alpaca_trade_api as tradeapi
import time
import pytz

# Insert your Alpaca API keys here
API_KEY = "YOUR_API_KEY"
SECRET_KEY = "YOUR_SECRET_KEY"

# Connect to Alpaca's API
api = tradeapi.REST(API_KEY, SECRET_KEY, api_version='v2')

# Set the time frame for the analysis
timeframe = "1D"

# Set the list of ticker symbols to analyze
ticker_list = ["SPY", "SQQQ", "TQQQ"]

# Loop through the ticker symbols
for ticker in ticker_list:
    # Get the historical data for the ticker
    barset = api.get_barset(ticker, timeframe, limit=1000).df

    # Calculate the MACD indicator
    fast_period = 12
    slow_period = 26
    signal_period = 9

    barset['fast_ema'] = barset[ticker].ewm(span=fast_period, adjust=False).mean()
    barset['slow_ema'] = barset[ticker].ewm(span=slow_period, adjust=False).mean()
    barset['macd'] = barset['fast_ema'] - barset['slow_ema']
    barset['signal'] = barset['macd'].ewm(span=signal_period, adjust=False).mean()

    # Get the current time in the Pacific time zone
    pacific_time = pytz.timezone('US/Pacific')
    current_time = pd.datetime.now(pacific_time)

    # Check if the MACD indicator is above the signal line
    if barset['macd'][-1] > barset['signal'][-1]:
        # MACD is above the signal line, so place a buy order
        try:
            api.submit_order(
                symbol=ticker,
                qty=1,
                side='buy',
                type='market',
                time_in_force='gtc',
                order_class='bracket',
                take_profit=dict(
                    limit_price=barset[ticker][-1]*1.03
                ),
                stop_loss=dict(
                    stop_price=barset[ticker][-1]*0.97,
                    limit_price=barset[ticker][-1]*0.97
                )
            )
        except Exception as e:
            print("Error placing buy order:", e)
    else:
        # MACD is below the signal line, so place a sell order
        try:
            api.submit_order(
                symbol=ticker,
                qty=1,
                side='sell',
                type='market',
                time_in_force='gtc',
                order_class='bracket',
                take_profit=dict(
                    limit_price=barset[ticker][-1]*0.97
                ),
                stop_loss=dict(
                    stop_price=barset[ticker][-1]*1.03,
                    limit_price=barset[ticker][-1]*1.03
                )
         except Exception as e:
             print("Error placing sell order:", e)
