import ccxt
import pandas as pd
import time
import datetime
import re

from smc import check_smc
from entry import is_near
from session import is_killzone
from telegram_bot import send_photo_and_message

from chart.chart import save_chart
from ai.ai_llm import analyze_with_ai

# =========================
# CONFIG
# =========================
SYMBOLS = ["BTC/USDT", "ETH/USDT"]
TIMEFRAME_1H = "1h"
TIMEFRAME_15M = "15m"

VERBOSE = True

# lưu setup đã gửi
last_setup = {}

# =========================
# LOGGER
# =========================
def log(msg):
    if VERBOSE:
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] {msg}")

# =========================
# EXCHANGE
# =========================
exchange = ccxt.binance()

def get_data(symbol, timeframe):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=200)
    df = pd.DataFrame(
        ohlcv, columns=["time", "open", "high", "low", "close", "volume"]
    )
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    return df

# =========================
# AI HELPERS
# =========================
def extract_score(text):
    match = re.search(r"Score:\s*(\d+(\.\d+)?)", text)
    return float(match.group(1)) if match else 0


def extract_decision(text):
    if "TRADE" in text.upper():
        return "TRADE"
    elif "SKIP" in text.upper():
        return "SKIP"
    return "UNKNOWN"


def build_prompt(symbol, signal, entry, price, df_15m):
    body = abs(df_15m["close"].iloc[-1] - df_15m["open"].iloc[-1])

    return f"""
Bạn là trader SMC chuyên nghiệp.

Symbol: {symbol}
Signal: {signal}

Entry: {entry[0]:.2f} - {entry[1]:.2f}
Price: {price:.2f}

Momentum: {body:.2f}

Hãy trả lời CHÍNH XÁC theo format:

Score: <number từ 1-10>
Decision: TRADE hoặc SKIP
Reason: <1 câu ngắn>

KHÔNG giải thích dài.
"""

# =========================
# CHECK SETUP MỚI
# =========================
def is_new_setup(symbol, signal, low, high, threshold=0.003):
    if symbol not in last_setup:
        return True

    old_signal, old_low, old_high = last_setup[symbol]

    # đổi LONG/SHORT → setup mới
    if signal != old_signal:
        return True

    # entry lệch đủ lớn → setup mới
    if abs(low - old_low) / low > threshold:
        return True

    if abs(high - old_high) / high > threshold:
        return True

    return False

# =========================
# MAIN LOOP
# =========================
log("🚀 BOT STARTED (NEW SETUP FILTER)")

while True:
    try:
        log("\n======================")
        log("🔄 NEW LOOP")
        log("======================")

        for symbol in SYMBOLS:
            log(f"\n🔍 Checking {symbol}")

            # ===== DATA =====
            df_1h = get_data(symbol, TIMEFRAME_1H)
            df_15m = get_data(symbol, TIMEFRAME_15M)

            current_time = df_15m["time"].iloc[-1]
            hour = current_time.hour

            log(f"🕒 Time: {current_time} (Hour: {hour})")

            # ===== SESSION =====
            #if not is_killzone(hour):
            #    log("⛔ Không phải killzone → skip")
            #    continue

            #log("✅ Đúng killzone")

            # ===== SMC =====
            signal, data = check_smc(df_1h, df_15m)

            if not signal:
                log("❌ Không có setup SMC")
                continue

            entry = data["entry"] if isinstance(data, dict) else data
            low, high = entry

            log(f"⚡ Setup: {signal}")
            log(f"📦 Entry: {low:.2f} - {high:.2f}")

            # ===== CHECK NEW SETUP =====
            if not is_new_setup(symbol, signal, low, high):
                log("⚠️ Setup trùng → skip")
                continue

            # ===== PRICE =====
            price = df_15m["close"].iloc[-1]
            log(f"💰 Price: {price:.2f}")

            # ===== NEAR ENTRY =====
            if not is_near(price, low, high):
                log("⛔ Giá chưa gần entry → skip")
                continue

            if abs(price - low) / price > 0.003:
                log("⛔ Chưa đủ gần → skip AI")
                continue

            log("🔥 Giá gần entry → AI check")

            # ===== SAVE CHART =====
            chart_path = save_chart(
                df_15m, f"{symbol.replace('/', '_')}.png"
            )

            # ===== BUILD PROMPT =====
            prompt = build_prompt(symbol, signal, (low, high), price, df_15m)

            # ===== CALL AI =====
            ai_result = analyze_with_ai(prompt, chart_path)

            log(f"🤖 AI:\n{ai_result}")

            # ===== PARSE AI =====
            score = extract_score(ai_result)
            decision = extract_decision(ai_result)

            log(f"🎯 Score: {score}")
            log(f"🧠 Decision: {decision}")

            # ===== TAG =====
            if score >= 8:
                tag = "🔥 HIGH QUALITY"
            elif score >= 6:
                tag = "👍 OK"
            else:
                tag = "⚠️ WEAK"

            # ===== SAVE SETUP =====
            last_setup[symbol] = (signal, low, high)

            # ===== TELEGRAM =====
            message = f"""{tag} {symbol}

📊 Signal: {signal}
💰 Price: {price:.2f}

🎯 Entry:
{low:.2f} - {high:.2f}

🤖 AI Analysis:
{ai_result}

🎯 Score: {score}
🧠 AI Suggest: {decision}

👉 Bạn tự quyết định
""".strip()

            send_photo_and_message(chart_path, message)

        log("\n⏳ Sleep 60s...\n")
        time.sleep(60)

    except Exception as e:
        log(f"❌ ERROR: {e}")
        time.sleep(10)