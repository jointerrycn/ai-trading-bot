import pandas as pd

def ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()

def trend_ok(df_1h, swing_length=2):
    df = df_1h.copy()

    df["ema50"] = ema(df, 50)
    df["ema200"] = ema(df, 200)

    if not (df["ema50"].iloc[-1] > df["ema200"].iloc[-1]):
        return False

    highs, lows = [], []

    for i in range(swing_length, len(df) - swing_length):
        if df["high"].iloc[i] == df["high"].iloc[i-swing_length:i+swing_length+1].max():
            highs.append(df["high"].iloc[i])
        if df["low"].iloc[i] == df["low"].iloc[i-swing_length:i+swing_length+1].min():
            lows.append(df["low"].iloc[i])

    if len(highs) < 2 or len(lows) < 2:
        return False

    return highs[-1] > highs[-2] and lows[-1] > lows[-2]

def check_setup(df_1h, df_15m):
    if not trend_ok(df_1h):
        return False, {}

    df = df_15m.copy()

    df["ema20"] = ema(df, 20)

    if df["ema20"].iloc[-1] < df["ema20"].iloc[-2]:
        return False, {}

    range_ = df["high"].iloc[-20:].max() - df["low"].iloc[-20:].min()
    if range_ < df["close"].iloc[-1] * 0.01:
        return False, {}

    swing = 2
    highs, lows = [], []

    for i in range(swing, len(df) - swing):
        if df["high"].iloc[i] == df["high"].iloc[i-swing:i+swing+1].max():
            highs.append((i, df["high"].iloc[i]))
        if df["low"].iloc[i] == df["low"].iloc[i-swing:i+swing+1].min():
            lows.append((i, df["low"].iloc[i]))

    if len(highs) < 2 or len(lows) < 1:
        return False, {}

    last_high = highs[-1][1]
    prev_high = highs[-2][1]
    last_low = lows[-1][1]

    if last_high <= prev_high:
        return False, {}

    current_close = df["close"].iloc[-1]
    current_open = df["open"].iloc[-1]

    body = abs(current_close - current_open)
    avg_body = abs(df["close"] - df["open"]).rolling(20).mean().iloc[-1]

    if not (current_close > last_high and body > avg_body * 1.2):
        return False, {}

    move = last_high - last_low

    # 🔥 adaptive entry
    if move / last_low > 0.02:
        entry = last_low + move * 0.382
        tp_rr = 2.5
    else:
        entry = last_low + move * 0.5
        tp_rr = 1.5

    sl = last_low * 0.999

    risk = entry - sl
    tp = entry + risk * tp_rr

    rr = (tp - entry) / risk if risk != 0 else 0

    return True, {
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "rr": rr
    }