import ccxt
import pandas as pd

exchange = ccxt.binance({
    'options': {
        'defaultType': 'future'
    }
})

def get_ohlc(symbol, timeframe, limit=200):
    ohlc = exchange.fetch_ohlcv(
        symbol,
        timeframe,
        limit=limit,
        params={"price": "mark"}  # 🔥 thêm dòng này
    )
    df = pd.DataFrame(ohlc, columns=["time","open","high","low","close","volume"])
    return df