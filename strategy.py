import pandas as pd

def ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()

# 1. Trend 1H (Chuẩn)
import pandas as pd
import numpy as np

def ema(df, period):
    return df["close"].ewm(span=period, adjust=False).mean()

# ==========================================
# 🟢 BỘ LỌC TREND 1H (DOW THEORY + EMA)
# ==========================================
def trend_ok(df_1h, swing_length=2):
    """
    Xác định xu hướng Tăng An Toàn:
    1. Dow Theory: Đỉnh sau cao hơn (HH), Đáy sau cao hơn (HL)
    2. EMA: EMA50 > EMA200 và Giá nằm trên EMA50
    swing_length: Số nến 2 bên để xác định 1 đỉnh/đáy (mặc định 2 nến trái, 2 nến phải)
    """
    df = df_1h.copy()
    
    # -----------------------------------
    # ĐIỀU KIỆN 1: ĐỘNG LƯỢNG EMA
    # -----------------------------------
    df["ema50"] = ema(df, 50)
    df["ema200"] = ema(df, 200)
    
    current_close = df["close"].iloc[-1]
    ema50 = df["ema50"].iloc[-1]
    ema200 = df["ema200"].iloc[-1]
    
    if not (ema50 > ema200 and current_close > ema50):
        return False # Tạch điều kiện EMA -> Bỏ qua luôn cho nhẹ máy
        
    # -----------------------------------
    # ĐIỀU KIỆN 2: LÝ THUYẾT DOW (HH, HL)
    # -----------------------------------
    # Thuật toán tìm Đỉnh/Đáy an toàn (Không Lookahead Bias)
    # Lùi lại nến để xác nhận đỉnh/đáy đã thực sự hình thành trong quá khứ
    highs = []
    lows = []
    
    # Quét qua lịch sử (bỏ qua các nến chưa đóng cửa hẳn ở sát hiện tại)
    for i in range(swing_length, len(df) - swing_length):
        # Đỉnh: Nến i có giá High cao nhất trong vùng [i - swing_length] đến [i + swing_length]
        window_high = df["high"].iloc[i-swing_length : i+swing_length+1].max()
        if df["high"].iloc[i] == window_high:
            highs.append(df["high"].iloc[i])
            
        # Đáy: Nến i có giá Low thấp nhất trong vùng [i - swing_length] đến [i + swing_length]
        window_low = df["low"].iloc[i-swing_length : i+swing_length+1].min()
        if df["low"].iloc[i] == window_low:
            lows.append(df["low"].iloc[i])

    # Cần ít nhất 2 đỉnh và 2 đáy để so sánh
    if len(highs) < 2 or len(lows) < 2:
        return False

    # Lấy 2 đỉnh, 2 đáy gần nhất
    prev_high, last_high = highs[-2], highs[-1]
    prev_low, last_low = lows[-2], lows[-1]

    # Kiểm tra cấu trúc: HH (Đỉnh sau cao hơn) và HL (Đáy sau cao hơn)
    is_dow_uptrend = (last_high > prev_high) and (last_low > prev_low)
    
    # -----------------------------------
    # ĐIỀU KIỆN 3: BẢO VỆ CẤU TRÚC
    # -----------------------------------
    # Giá hiện tại tuyệt đối không được sập thủng cái đáy gần nhất (last_low)
    structure_intact = current_close > last_low

    # Chỉ báo Tín hiệu Xanh khi thỏa mãn TẤT CẢ
    return is_dow_uptrend and structure_intact

# 2. Check toàn bộ Setup 15m (Sweep -> Break -> HL)
def check_setup(df_1h, df_15m):
    # ❌ Lọc trend 1H
    if not trend_ok(df_1h):
        return False

    # Định nghĩa cửa sổ quan sát (15 nến gần nhất) để tìm Setup
    lookback = 15
    window = df_15m.iloc[-lookback:]
    
    # Vùng đỉnh/đáy cũ (từ nến -30 đến nến -16) để làm tham chiếu
    prev_lows = df_15m["low"].iloc[-(lookback+15):-lookback]
    prev_highs = df_15m["high"].iloc[-(lookback+15):-lookback]
    
    if prev_lows.empty or prev_highs.empty:
        return False
        
    sweep_level = prev_lows.min()
    bos_level = prev_highs.max()
    
    sweep_found = False
    bos_found = False
    
    # Quét từ trái sang phải trong 15 nến gần nhất
    for i in range(len(window)):
        row = window.iloc[i]
        
        # 🔥 Bước 1: Tìm Sweep
        if not sweep_found:
            if row["low"] < sweep_level and row["close"] > sweep_level:
                sweep_found = True
                continue # Tìm thấy rồi thì xét nến tiếp theo
                
        # 🔥 Bước 2: Tìm Break (chỉ tính nến diễn ra SAU Sweep)
        if sweep_found and not bos_found:
            if row["close"] > bos_level:
                bos_found = True
                
    # 🔥 Bước 3: Check HL (Higher Low)
    # Nếu đã có đủ Sweep và Break, kiểm tra xem đáy nến hiện tại có giữ được trên đáy Sweep không
    if sweep_found and bos_found:
        current_low = df_15m["low"].iloc[-1]
        sweep_bottom = window["low"].min() # Đáy thấp nhất trong cửa sổ (chính là đáy sweep)
        
        if current_low > sweep_bottom:
            return True,sweep_bottom # ✅ FULL SETUP PASSED!

    return False, None