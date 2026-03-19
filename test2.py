from data import get_ohlc

df = get_ohlc("BTC/USDT", "1h")
print(df.tail())