import time
from config import SYMBOLS, TIMEFRAME_1H, TIMEFRAME_15M
from data import get_ohlc
from strategy import check_setup, trend_ok, sweep, break_structure, hl_valid
from telegram_bot import send_message


def run():
    for symbol in SYMBOLS:
        try:
            print(f"\n🔍 Checking {symbol}...")

            # lấy data
            df_1h = get_ohlc(symbol, TIMEFRAME_1H)
            df_15m = get_ohlc(symbol, TIMEFRAME_15M)

            # debug từng bước
            trend = trend_ok(df_1h)
            sw = sweep(df_15m)
            br = break_structure(df_15m)
            hl = hl_valid(df_15m)

            print(f"Trend: {trend}")
            print(f"Sweep: {sw}")
            print(f"Break: {br}")
            print(f"HL: {hl}")

            # check setup
            if check_setup(df_1h, df_15m):
                msg = f"🔥 SETUP: {symbol} (LONG)"
                send_message(msg)
                print(msg)

        except Exception as e:
            print(f"❌ Error {symbol}: {e}")


# loop chạy liên tục
while True:
    print("\n===== NEW SCAN =====")
    run()
    time.sleep(300)  # 5 phút