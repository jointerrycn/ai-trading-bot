from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

def add_indicators(df):

    df["rsi"] = RSIIndicator(df["close"], 14).rsi()

    df["ema50"] = EMAIndicator(df["close"], 50).ema_indicator()

    df["ema200"] = EMAIndicator(df["close"], 200).ema_indicator()

    return df