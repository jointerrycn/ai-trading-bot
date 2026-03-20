import pandas as pd

# =========================
# 1. TREND (FAST - VECTORIZED)
# =========================
def smc_trend_fast(df):

    highs = df[df['high'] == df['high'].rolling(5, center=True).max()]
    lows = df[df['low'] == df['low'].rolling(5, center=True).min()]

    peaks = highs[['high']].assign(type='H').rename(columns={'high': 'val'})
    troughs = lows[['low']].assign(type='L').rename(columns={'low': 'val'})

    structure = pd.concat([peaks, troughs]).sort_index()

    if len(structure) < 4:
        return None

    last = structure.iloc[-4:]
    types = last['type'].tolist()
    vals = last['val'].tolist()

    # UP trend
    if types == ['L', 'H', 'L', 'H']:
        if vals[2] > vals[0] and vals[3] > vals[1]:
            return "up"

    # DOWN trend
    if types == ['H', 'L', 'H', 'L']:
        if vals[2] < vals[0] and vals[3] < vals[1]:
            return "down"

    return None


# =========================
# 2. LIQUIDITY SWEEP
# =========================
def liquidity_sweep_low(df):
    recent_low = df["low"].iloc[-21:-1].min()
    current_low = df["low"].iloc[-1]
    return current_low < recent_low


def liquidity_sweep_high(df):
    recent_high = df["high"].iloc[-21:-1].max()
    current_high = df["high"].iloc[-1]
    return current_high > recent_high


# =========================
# 3. BOS (BREAK STRUCTURE)
# =========================
def bos_bullish(df):
    prev_high = df["high"].iloc[-10:-2].max()
    return df["close"].iloc[-1] > prev_high


def bos_bearish(df):
    prev_low = df["low"].iloc[-10:-2].min()
    return df["close"].iloc[-1] < prev_low


# =========================
# 4. FVG (FIX TIMING)
# =========================
def find_fvg(df):
    for i in range(len(df)-1, 1, -1):  # FIX
        if df["low"].iloc[i] > df["high"].iloc[i-2]:
            return (df["high"].iloc[i-2], df["low"].iloc[i])
    return None


def find_fvg_bearish(df):
    for i in range(len(df)-1, 1, -1):  # FIX
        if df["high"].iloc[i] < df["low"].iloc[i-2]:
            return (df["high"].iloc[i], df["low"].iloc[i-2])
    return None


# =========================
# 5. ORDER BLOCK (ICT BASIC)
# =========================
def find_bullish_ob(df):
    for i in range(len(df)-5, 1, -1):
        if df["close"].iloc[i] < df["open"].iloc[i]:
            return (df["low"].iloc[i], df["high"].iloc[i])
    return None


def find_bearish_ob(df):
    for i in range(len(df)-5, 1, -1):
        if df["close"].iloc[i] > df["open"].iloc[i]:
            return (df["low"].iloc[i], df["high"].iloc[i])
    return None


# =========================
# 6. CONFLUENCE (FVG ∩ OB)
# =========================
def get_overlap(zone1, zone2):
    low = max(zone1[0], zone2[0])
    high = min(zone1[1], zone2[1])

    if low < high:
        return (low, high)

    return None


# =========================
# 7. MAIN SMC CHECK
# =========================
def check_smc2(df_1h, df_15m):

    trend = smc_trend_fast(df_1h)

    # =========================
    # LONG
    # =========================
    if trend == "up":

        if liquidity_sweep_low(df_15m) and bos_bullish(df_15m):

            fvg = find_fvg(df_15m)
            ob = find_bullish_ob(df_15m)

            # ❌ Không có FVG → bỏ luôn
            if not fvg:
                return None, None

            # ✅ Có OB → check overlap
            if ob:
                overlap = get_overlap(fvg, ob)

                if overlap:
                    return "LONG", overlap  # BEST CASE

            # ⚡ fallback → dùng FVG
            return "LONG", fvg

    # =========================
    # SHORT
    # =========================
    if trend == "down":

        if liquidity_sweep_high(df_15m) and bos_bearish(df_15m):

            fvg = find_fvg_bearish(df_15m)
            ob = find_bearish_ob(df_15m)

            if not fvg:
                return None, None

            if ob:
                overlap = get_overlap(fvg, ob)

                if overlap:
                    return "SHORT", overlap

            return "SHORT", fvg

    return None, None

import random

def check_smc(df_1h, df_15m):

    # fake signal random
    signals = ["LONG", "SHORT", None]
    signal = random.choice(signals)

    if not signal:
        return None, None

    price = df_15m["close"].iloc[-1]

    # fake entry gần giá
    low = price * random.uniform(0.995, 0.999)
    high = price * random.uniform(1.001, 1.005)

    return signal, (low, high)