import ccxt
import pandas as pd

exchange = ccxt.binance()

def fetch_ohlcv(symbol="BTC/USDT", timeframe="15m", limit=200):

    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(
        ohlcv,
        columns=["timestamp","open","high","low","close","volume"]
    )

    return df