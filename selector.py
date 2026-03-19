import json
import os

# =========================
# LOAD DATA (SAFE)
# =========================
data_cache = None

def load_data():
    global data_cache

    if data_cache is not None:
        return data_cache

    if not os.path.exists("performance.json"):
        data_cache = {"coin_stats": {}, "hour_stats": {}}
        return data_cache

    with open("performance.json", "r") as f:
        data_cache = json.load(f)

    return data_cache


# =========================
# SELECT COINS
# =========================
def select_best_coins():
    data = load_data()

    if not data["coin_stats"]:
        #return ["BTC/USDT", "ETH/USDT"]  # fallback
        return ["BTC/USDT","ETH/USDT","SOL/USDT","BNB/USDT","XRP/USDT","TAO/USDT"]

    result = []

    for coin, s in data["coin_stats"].items():
        total = s["win"] + s["loss"]
        if total == 0:
            continue

        winrate = s["win"] / total * 100

        if winrate >= 50 and s["r"] > 0:
            result.append(coin)

    # 🔥 fallback nếu lọc hết
    if not result:
        print("⚠️ Không có coin nào đạt điều kiện → dùng fallback")
        return ["BTC/USDT", "ETH/USDT"]

    return result


# =========================
# SELECT HOURS
# =========================
def select_best_hours():
    data = load_data()

    if not data["hour_stats"]:
        return list(range(24))  # fallback trade all giờ

    result = []

    for h, s in data["hour_stats"].items():
        total = s["win"] + s["loss"]

        if total < 5:
            continue

        winrate = s["win"] / total * 100

        if winrate >= 50:
            result.append(int(h))

    # 🔥 fallback nếu không có giờ nào
    if not result:
        print("⚠️ Không có giờ tốt → trade full session")
        return list(range(24))

    return result