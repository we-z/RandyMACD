import alpaca_trade_api as tradeapi
import time
import talib

# Replace YOUR_API_KEY and YOUR_SECRET_KEY with your own keys
api = tradeapi.REST(
    key_id='YOUR_API_KEY',
    secret_key='YOUR_SECRET_KEY',
    base_url='https://paper-api.alpaca.markets'
)

# Set the symbol and time frame
symbol = 'SOXL'
timeframe = '5Min'

# Set the MACD parameters
fast_length = 4
slow_length = 5
signal_smooth = 3

while True:
    # Get the current bar data
    bars = api.get_bars(symbol, timeframe, limit=2)
    data = [x.c for x in bars]

    # Calculate the MACD
    macd, macd_signal, macd_hist = talib.MACD(data, fast_length, slow_length, signal_smooth)

    # Get the current price
    price = data[-1]

    # Check if we should buy or sell
    if macd[-1] > macd_signal[-1] and data[-2] < data[-1]:
        # MACD is positive and the price is increasing, so buy
        api.orders.submit(
            symbol=symbol,
            qty=1,
            side='buy',
            type='market',
            time_in_force='gtc',
            stop_loss={
                'stop_price': price * 0.99,
                'limit_price': price * 1.01
            }
        )
    elif macd[-1] < macd_signal[-1] and data[-2] > data[-1]:
        # MACD is negative and the price is decreasing, so sell
        api.orders.submit(
            symbol=symbol,
            qty=1,
            side='sell',
            type='market',
            time_in_force='gtc',
            stop_loss={
                'stop_price': price * 1.01,
                'limit_price': price * 0.99
            }
        )

    # Sleep for one minute
    time.sleep(60)
