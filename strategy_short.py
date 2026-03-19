from strategy import ema

def downtrend_ok(df_1h):
    df = df_1h.copy()

    df["ema50"] = ema(df, 50)
    df["ema200"] = ema(df, 200)

    return df["ema50"].iloc[-1] < df["ema200"].iloc[-1]

def check_short_setup(df_1h, df_15m):
    if not downtrend_ok(df_1h):
        return False, {}

    df = df_15m.copy()

    df["ema20"] = ema(df, 20)

    if df["ema20"].iloc[-1] > df["ema20"].iloc[-2]:
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

    if len(highs) < 1 or len(lows) < 2:
        return False, {}

    last_low = lows[-1][1]
    prev_low = lows[-2][1]
    last_high = highs[-1][1]

    if last_low >= prev_low:
        return False, {}

    current_close = df["close"].iloc[-1]
    current_open = df["open"].iloc[-1]

    body = abs(current_close - current_open)
    avg_body = abs(df["close"] - df["open"]).rolling(20).mean().iloc[-1]

    if not (current_close < last_low and body > avg_body * 1.2):
        return False, {}

    move = last_high - last_low

    if move / last_low > 0.02:
        entry = last_high - move * 0.382
        tp_rr = 2.5
    else:
        entry = last_high - move * 0.5
        tp_rr = 1.5

    sl = last_high * 1.001

    risk = sl - entry
    tp = entry - risk * tp_rr

    rr = (entry - tp) / risk if risk != 0 else 0

    return True, {
        "entry": entry,
        "sl": sl,
        "tp": tp,
        "rr": rr
    }