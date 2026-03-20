def is_near(price, low, high, threshold=0.003):

    if low <= price <= high:
        return True

    if price < low:
        return (low - price) / price < threshold

    if price > high:
        return (price - high) / price < threshold

    return False