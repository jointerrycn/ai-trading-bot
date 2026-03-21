from config import RISK_PER_TRADE

def calculate_position_size(balance, entry, sl):
    risk_amount = balance * RISK_PER_TRADE
    risk_per_unit = abs(entry - sl)

    if risk_per_unit == 0:
        return 0

    return risk_amount / risk_per_unit