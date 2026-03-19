import ccxt
import pandas as pd
import time

from strategy import check_setup
from strategy_short import check_short_setup
from selector import select_best_coins, select_best_hours
from telegram_bot import send_message

exchange = ccxt.binance()

SYMBOLS = ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT","TAO/USDT"]

VERBOSE = True

def log(msg):
    if VERBOSE:
        print(msg)

def get_data(symbol, timeframe, limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

print("🚀 BOT STARTED")

while True:
    try:
        log("\n========================")
        log("🔄 NEW LOOP START")
        log("========================")

        BEST_COINS = select_best_coins()
        BEST_HOURS = select_best_hours()

        log(f"📊 Best Coins: {BEST_COINS}")
        log(f"⏰ Best Hours: {BEST_HOURS}")

        for symbol in SYMBOLS:

            log(f"\n🔍 Checking {symbol}")

            # ❌ Skip coin
            if symbol not in BEST_COINS:
                log("⛔ Skip coin (không nằm trong best coins)")
                continue

            df_15m = get_data(symbol, "15m")
            df_1h = get_data(symbol, "1h")

            current_time = df_15m["time"].iloc[-1]
            hour = current_time.hour

            log(f"🕒 Time: {current_time} (Hour: {hour})")

            # ❌ Skip hour
            if hour not in BEST_HOURS:
                log("⛔ Skip giờ (không nằm trong best hours)")
                continue

            log("✅ Passed filter coin + session")

            # =========================
            # CHECK SETUP
            # =========================
            long_ok, long_data = check_setup(df_1h, df_15m)
            short_ok, short_data = check_short_setup(df_1h, df_15m)

            if not (long_ok or short_ok):
                log("❌ Không có setup")
                continue

            log("⚡ SETUP FOUND")

            # =========================
            # LONG
            # =========================
            if long_ok:
                log(f"🟢 LONG SIGNAL {symbol}")
                log(f"Entry: {long_data['entry']:.2f}")
                log(f"SL: {long_data['sl']:.2f}")
                log(f"TP: {long_data['tp']:.2f}")
                log(f"RR: {long_data['rr']:.2f}")

                msg = f"""
🟢 LONG {symbol}
Entry: {long_data['entry']:.2f}
SL: {long_data['sl']:.2f}
TP: {long_data['tp']:.2f}
RR: {long_data['rr']:.2f}
"""
                send_message(msg)

            # =========================
            # SHORT
            # =========================
            if short_ok:
                log(f"🔴 SHORT SIGNAL {symbol}")
                log(f"Entry: {short_data['entry']:.2f}")
                log(f"SL: {short_data['sl']:.2f}")
                log(f"TP: {short_data['tp']:.2f}")
                log(f"RR: {short_data['rr']:.2f}")

                msg = f"""
🔴 SHORT {symbol}
Entry: {short_data['entry']:.2f}
SL: {short_data['sl']:.2f}
TP: {short_data['tp']:.2f}
RR: {short_data['rr']:.2f}
"""
                send_message(msg)

        log("\n⏳ Sleep 60s...\n")
        time.sleep(60)

    except Exception as e:
        print("❌ ERROR:", e)
        time.sleep(10)