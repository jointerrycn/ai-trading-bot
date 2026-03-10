import time

from data import fetch_ohlcv
from indicators import add_indicators
from strategy import check_signal
from telegram_bot import send_alert

symbol = "BTC/USDT"

while True:

    df = fetch_ohlcv(symbol)

    df = add_indicators(df)

    signal = check_signal(df)

    if signal:
        send_alert(f"{symbol} BUY SIGNAL")

    time.sleep(60)