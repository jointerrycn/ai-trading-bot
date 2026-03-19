import ccxt
import pandas as pd
import time

from strategy import check_setup
from strategy_short import check_short_setup
from selector import select_best_coins, select_best_hours
from telegram_bot import send_message

exchange = ccxt.binance()

SYMBOLS = ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT"]

def get_data(symbol, timeframe, limit=200):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

    df = pd.DataFrame(ohlcv, columns=['time','open','high','low','close','volume'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    return df

print("🚀 BOT STARTED")

while True:
    try:
        BEST_COINS = select_best_coins()
        BEST_HOURS = select_best_hours()

        for symbol in SYMBOLS:

            if symbol not in BEST_COINS:
                continue

            df_15m = get_data(symbol, "15m")
            df_1h = get_data(symbol, "1h")

            current_time = df_15m["time"].iloc[-1]
            hour = current_time.hour

            if hour not in BEST_HOURS:
                continue

            long_ok, long_data = check_setup(df_1h, df_15m)
            short_ok, short_data = check_short_setup(df_1h, df_15m)

            if long_ok:
                msg = f"""
🟢 LONG {symbol}
Entry: {long_data['entry']:.2f}
SL: {long_data['sl']:.2f}
TP: {long_data['tp']:.2f}
RR: {long_data['rr']:.2f}
"""
                send_message(msg)

            if short_ok:
                msg = f"""
🔴 SHORT {symbol}
Entry: {short_data['entry']:.2f}
SL: {short_data['sl']:.2f}
TP: {short_data['tp']:.2f}
RR: {short_data['rr']:.2f}
"""
                send_message(msg)

        time.sleep(60)

    except Exception as e:
        print("Error:", e)
        time.sleep(10)