import pandas as pd
import numpy as np
import random

# =========================
# 1. TÌM SWING HIGHS / LOWS (CẤU TRÚC THỊ TRƯỜNG)
# =========================
def get_swings(df, window=5):
    """Tìm các đỉnh/đáy xoay chiều (Swing High/Low)"""
    df_copy = df.copy()
    df_copy['is_high'] = df_copy['high'] == df_copy['high'].rolling(window, center=True).max()
    df_copy['is_low'] = df_copy['low'] == df_copy['low'].rolling(window, center=True).min()
    
    highs = df_copy[df_copy['is_high']]
    lows = df_copy[df_copy['is_low']]
    return highs, lows

# =========================
# 2. XÁC ĐỊNH XU HƯỚNG 1H
# =========================
def get_trend(df):
    """Xác định xu hướng dựa trên 2 đỉnh và 2 đáy gần nhất"""
    highs, lows = get_swings(df)
    
    if len(highs) < 2 or len(lows) < 2:
        return "sideway"
        
    # Lấy 2 đỉnh cuối và 2 đáy cuối
    last_highs = df.loc[highs.index[-2:]]['high'].values
    last_lows = df.loc[lows.index[-2:]]['low'].values
    
    # Uptrend: Đỉnh sau cao hơn đỉnh trước VÀ Đáy sau cao hơn đáy trước (HH, HL)
    if last_highs[1] > last_highs[0] and last_lows[1] > last_lows[0]:
        return "up"
        
    # Downtrend: Đỉnh sau thấp hơn đỉnh trước VÀ Đáy sau thấp hơn đáy trước (LH, LL)
    elif last_highs[1] < last_highs[0] and last_lows[1] < last_lows[0]:
        return "down"
        
    return "sideway"

# =========================
# 3. RANGE FILTER BẰNG ATR
# =========================
def calculate_atr(df, period=14):
    """Tính toán chỉ báo ATR để đo lường biến động giá"""
    df_copy = df.copy()
    
    # Tính toán các thành phần của True Range
    high_low = df_copy['high'] - df_copy['low']
    high_close = (df_copy['high'] - df_copy['close'].shift(1)).abs()
    low_close = (df_copy['low'] - df_copy['close'].shift(1)).abs()
    
    # Gộp lại và tìm Max trên mỗi hàng
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Trung bình động của TR (ATR)
    return tr.rolling(window=period).mean()

def is_ranging_atr(df_15m, window=20, atr_multiplier=1):
    """
    Kiểm tra xem thị trường có đang đi ngang không.
    Nếu biên độ của 'window' nến gần nhất nhỏ hơn 'atr_multiplier * ATR', 
    thì coi là thị trường đang bị nén/choppy.
    """
    # Tính ATR và gán vào dataframe tạm
    df_temp = df_15m.copy()
    df_temp['atr'] = calculate_atr(df_temp, period=14)
    
    # Bỏ qua các hàng NaN do rolling gây ra
    if df_temp['atr'].isna().iloc[-1]:
        return True 
        
    recent_df = df_temp.iloc[-window:]
    max_high = recent_df['high'].max()
    min_low = recent_df['low'].min()
    
    # Biên độ hộp hiện tại
    current_range_width = max_high - min_low
    # Giá trị ATR của nến đóng cửa gần nhất
    current_atr = df_temp['atr'].iloc[-1]
    
    # Kiểm tra điều kiện nén giá
    if current_range_width < (current_atr * atr_multiplier):
        return True
        
    return False

# =========================
# 4. HÀM CHECK SMC CHÍNH (TIME-SERIES LOGIC)
# =========================
def check_smc(df_1h, df_15m):
    # 🔴 Bỏ cây nến cuối cùng (iloc[:-1]) vì nó chưa đóng cửa
    df_1h_closed = df_1h.iloc[:-1].reset_index(drop=True)
    df_15m_closed = df_15m.iloc[:-1].reset_index(drop=True)
    
    if len(df_15m_closed) < 50 or len(df_1h_closed) < 20:
        return None, None

    # ===== KIỂM TRA TREND 1H =====
    trend_1h = get_trend(df_1h_closed)
    
    if trend_1h not in ["up", "down"]:
        return None, None 

    # ===== KIỂM TRA CHOPPY / RANGE 15M =====
    if is_ranging_atr(df_15m_closed, window=20, atr_multiplier=1.8):
        return None, None 

    # ===== PHÂN TÍCH SMC 15M =====
    highs, lows = get_swings(df_15m_closed)
    
    if len(highs) < 2 or len(lows) < 2:
        return None, None

    recent_df = df_15m_closed.iloc[-40:]
    
    # =========================
    # KIỂM TRA SETUP LONG (CHỈ KHI 1H UPTREND)
    # =========================
    if trend_1h == "up":
        last_low_idx = lows.index[-1]
        prev_low_idx = lows.index[-2]
        
        # 1. LIQUIDITY SWEEP
        is_sweep_low = df_15m_closed.loc[last_low_idx, 'low'] < df_15m_closed.loc[prev_low_idx, 'low']
        
        # 2. BOS BULLISH
        last_high_idx = highs.index[-1]
        bos_bullish_found = False
        bos_idx = None
        
        for idx in recent_df.index:
            if idx > last_low_idx and df_15m_closed.loc[idx, 'close'] > df_15m_closed.loc[last_high_idx, 'high']:
                bos_bullish_found = True
                bos_idx = idx
                break

        if is_sweep_low and bos_bullish_found:
            fvg = None
            ob = None
            
            # 3. Tìm FVG tăng
            for i in range(last_low_idx + 2, bos_idx + 1):
                if df_15m_closed.loc[i, 'low'] > df_15m_closed.loc[i-2, 'high']:
                    fvg = (df_15m_closed.loc[i-2, 'high'], df_15m_closed.loc[i, 'low'])
                    break
            
            # 4. Tìm Order Block
            for i in range(last_low_idx, bos_idx):
                if df_15m_closed.loc[i, 'close'] < df_15m_closed.loc[i, 'open']: 
                    ob = (df_15m_closed.loc[i, 'low'], df_15m_closed.loc[i, 'high'])
            
            # 5. Gộp vùng Entry
            if fvg and ob:
                overlap_low = max(fvg[0], ob[0])
                overlap_high = min(fvg[1], ob[1])
                if overlap_low < overlap_high:
                    return "LONG", (overlap_low, overlap_high)
            
            if fvg:
                return "LONG", fvg

    # =========================
    # KIỂM TRA SETUP SHORT (CHỈ KHI 1H DOWNTREND)
    # =========================
    if trend_1h == "down":
        last_high_idx = highs.index[-1]
        prev_high_idx = highs.index[-2]
        
        # 1. LIQUIDITY SWEEP
        is_sweep_high = df_15m_closed.loc[last_high_idx, 'high'] > df_15m_closed.loc[prev_high_idx, 'high']
        
        # 2. BOS BEARISH
        last_low_idx_for_short = lows.index[-1]
        bos_bearish_found = False
        bos_idx = None
        
        for idx in recent_df.index:
            if idx > last_high_idx and df_15m_closed.loc[idx, 'close'] < df_15m_closed.loc[last_low_idx_for_short, 'low']:
                bos_bearish_found = True
                bos_idx = idx
                break

        if is_sweep_high and bos_bearish_found:
            fvg = None
            ob = None
            
            # 3. Tìm FVG giảm
            for i in range(last_high_idx + 2, bos_idx + 1):
                if df_15m_closed.loc[i, 'high'] < df_15m_closed.loc[i-2, 'low']: 
                    fvg = (df_15m_closed.loc[i, 'high'], df_15m_closed.loc[i-2, 'low'])
                    break
                    
            # 4. Tìm Order Block
            for i in range(last_high_idx, bos_idx):
                if df_15m_closed.loc[i, 'close'] > df_15m_closed.loc[i, 'open']: 
                    ob = (df_15m_closed.loc[i, 'low'], df_15m_closed.loc[i, 'high'])
                    
            # 5. Gộp vùng Entry
            if fvg and ob:
                overlap_low = max(fvg[0], ob[0])
                overlap_high = min(fvg[1], ob[1])
                if overlap_low < overlap_high:
                    return "SHORT", (overlap_low, overlap_high)
            
            if fvg:
                return "SHORT", fvg

    return None, None

# =========================
# 5. HÀM MÔ PHỎNG (ĐỂ TEST)
# =========================
def check_smctest(df_1h, df_15m):

    # fake signal random
    signals = ["LONG", "SHORT", None]
    signal = random.choice(signals)

    if not signal:
        return None, None

    price = df_15m["close"].iloc[-1]

    # fake entry gần giá
    low = price * random.uniform(0.995, 0.999)
    high = price * random.uniform(1.001, 1.005)

    return signal, (low, high)