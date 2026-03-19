import json

def load_data():
    with open("performance.json", "r") as f:
        return json.load(f)

def select_best_coins():
    data = load_data()
    result = []

    for coin, s in data["coin_stats"].items():
        total = s["win"] + s["loss"]
        if total == 0:
            continue

        winrate = s["win"] / total * 100

        if winrate >= 50 and s["r"] > 0:
            result.append(coin)

    return result

def select_best_hours():
    data = load_data()
    result = []

    for h, s in data["hour_stats"].items():
        total = s["win"] + s["loss"]
        if total < 5:
            continue

        winrate = s["win"] / total * 100

        if winrate >= 50:
            result.append(int(h))

    return result