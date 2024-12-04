import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

from yahoo_fin import stock_info

price = stock_info.get_live_price("AAPL")
print(price)

