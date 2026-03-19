import pandas as pd

def ema(df, period):
    return df["close"].ewm(span=period).mean()

# 1. Trend 1H
def trend_ok(df):
    df["ema50"] = ema(df, 50)
    df["ema200"] = ema(df, 200)
    return df["ema50"].iloc[-1] > df["ema200"].iloc[-1]

# 2. Sweep (lookback nhiều nến)
def sweep(df):
    recent_lows = df["low"].iloc[-10:-2]
    current_low = df["low"].iloc[-1]
    close = df["close"].iloc[-1]

    sweep_level = recent_lows.min()

    return current_low < sweep_level and close > sweep_level

# 3. Break (lookback rộng hơn)
def break_structure(df):
    recent_high = df["high"].iloc[-10:-2].max()
    close = df["close"].iloc[-1]

    return close > recent_high

# 4. HL (giữ structure)
def hl_valid(df):
    recent_lows = df["low"].iloc[-5:]
    return recent_lows.iloc[-1] > recent_lows.min()

# 5. Check setup (linh hoạt hơn)
def check_setup(df_1h, df_15m):
    if not trend_ok(df_1h):
        return False

    # 🔥 sweep là bắt buộc
    if not sweep(df_15m):
        return False

    # 👉 còn lại cần ít nhất 1
    conditions = [
        break_structure(df_15m),
        hl_valid(df_15m)
    ]

    return any(conditions)