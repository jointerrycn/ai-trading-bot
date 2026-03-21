import pandas as pd
import time
import ccxt
import json
from collections import defaultdict

from strategy import check_setup
from strategy_short import check_short_setup

# =========================
# CONFIG
# =========================
SYMBOLS = ["BTC/USDT","ETH/USDT","SOL/USDT"]
TEST_DAYS = 90
VERBOSE = True

exchange = ccxt.binance()

def log(msg):
    if VERBOSE:
        print(msg)

def get_data(symbol, timeframe, days):
    now = exchange.milliseconds()
    since = now - days * 24 * 60 * 60 * 1000

    data = []
    while since < now:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since=since, limit=1000)
        if not ohlcv:
            break
        data += ohlcv
        since = ohlcv[-1][0] + 1
        time.sleep(0.2)

    df = pd.DataFrame(data, columns=['time','open','high','low','close','volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms') + pd.Timedelta(hours=7)
    df.set_index('time', inplace=True)
    return df

trades = []
in_trade = False

for symbol in SYMBOLS:
    print(f"\n🚀 TESTING {symbol}")

    df_15m = get_data(symbol, "15m", TEST_DAYS)
    df_1h = get_data(symbol, "1h", TEST_DAYS + 15)

    for i in range(200, len(df_15m)):
        current_time = df_15m.index[i]
        candle = df_15m.iloc[i]

        # 🔍 SCAN LOG
        if i % 100 == 0:
            log(f"\n🔍 Scan: {current_time}")

        # ================= EXIT =================
        if in_trade:
            t = trades[-1]

            if t["direction"] == "LONG":
                if candle["low"] <= t["sl"]:
                    log(f"❌ SL HIT {symbol} at {current_time}")
                    t["status"] = "SL"
                    in_trade = False

                elif candle["high"] >= t["tp"]:
                    log(f"✅ TP HIT {symbol} at {current_time}")
                    t["status"] = "TP"
                    in_trade = False

            else:
                if candle["high"] >= t["sl"]:
                    log(f"❌ SL HIT {symbol} at {current_time}")
                    t["status"] = "SL"
                    in_trade = False

                elif candle["low"] <= t["tp"]:
                    log(f"✅ TP HIT {symbol} at {current_time}")
                    t["status"] = "TP"
                    in_trade = False

        # ================= ENTRY =================
        if not in_trade:
            sub_15m = df_15m.iloc[:i+1]
            sub_1h = df_1h[df_1h.index <= current_time]

            if len(sub_1h) < 200:
                continue

            long_ok, long_data = check_setup(sub_1h, sub_15m)
            short_ok, short_data = check_short_setup(sub_1h, sub_15m)

            if not (long_ok or short_ok):
                continue

            log(f"\n⚡ SETUP FOUND {symbol} at {current_time}")

            if long_ok:
                log(f"→ LONG | Entry {long_data['entry']:.2f} SL {long_data['sl']:.2f} TP {long_data['tp']:.2f}")

            if short_ok:
                log(f"→ SHORT | Entry {short_data['entry']:.2f} SL {short_data['sl']:.2f} TP {short_data['tp']:.2f}")

            if long_ok:
                direction = "LONG"
                data = long_data
            else:
                direction = "SHORT"
                data = short_data

            entry = data["entry"]
            sl = data["sl"]
            tp = data["tp"]

            # ⏳ ENTRY CHECK
            if direction == "LONG" and candle["low"] > entry:
                log("⏳ LONG chưa chạm entry")
                continue

            if direction == "SHORT" and candle["high"] < entry:
                log("⏳ SHORT chưa chạm entry")
                continue

            # RR FILTER
            risk = abs(entry - sl)
            rr = abs(tp - entry) / risk if risk != 0 else 0

            if rr < 1.3:
                log(f"⛔ Skip RR thấp: {rr:.2f}")
                continue

            log(f"\n💰 ENTER {direction} {symbol}")
            log(f"Entry {entry:.2f} | SL {sl:.2f} | TP {tp:.2f} | RR {rr:.2f}")

            trades.append({
                "symbol": symbol,
                "time": current_time,
                "direction": direction,
                "entry": entry,
                "sl": sl,
                "tp": tp,
                "status": "RUN"
            })

            in_trade = True

# ================= RESULT =================
win = loss = 0

for t in trades:
    if t["status"] == "TP":
        win += 1
    elif t["status"] == "SL":
        loss += 1

print("\n===== RESULT =====")
print("Trades:", len(trades))
print("Win:", win)
print("Loss:", loss)

if win + loss > 0:
    print("Winrate:", round(win/(win+loss)*100,2), "%")