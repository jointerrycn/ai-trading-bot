import pandas as pd
import time
from data import get_ohlc
from strategy import check_setup

SYMBOL = "BTC/USDT"

print(f"📥 Đang tải dữ liệu {SYMBOL} qua CCXT...")
# Lưu ý: Tăng limit lên 1500 để có đủ data test dài ngày
df_15m = get_ohlc(SYMBOL, "15m", limit=1500) 
df_1h = get_ohlc(SYMBOL, "1h", limit=1000)

print(f"📊 Dữ liệu 15m: {len(df_15m)} nến | 1H: {len(df_1h)} nến")
print("🚀 Bắt đầu quét Backtest (Giả lập Real-time)...\n")

trades = []
last_signal_time = None
in_trade = False

entry_price = sl_price = tp_price = 0

# Bắt đầu từ nến 200 để có đủ data 1H tính EMA
for i in range(200, len(df_15m)):
    current_time = df_15m.index[i] if isinstance(df_15m.index, pd.DatetimeIndex) else df_15m['time'].iloc[i]
    current_candle = df_15m.iloc[i]
    
    # 1. QUẢN LÝ LỆNH ĐANG CHẠY
    if in_trade:
        if current_candle['low'] <= sl_price:
            trades[-1]['status'] = '❌ Thua (Cắn SL)'
            trades[-1]['exit_time'] = current_time
            in_trade = False
            continue
            
        if current_candle['high'] >= tp_price:
            trades[-1]['status'] = '✅ Thắng (Chạm TP)'
            trades[-1]['exit_time'] = current_time
            in_trade = False
            continue

    # 2. TÌM LỆNH MỚI (Gọi hàm TỪ FILE STRATEGY CỦA BẠN)
    if not in_trade:
        sub_df_15m = df_15m.iloc[:i+1]
        
        # Nếu data của bạn dùng index là time thì dùng loc, nếu không thì so sánh cột
        if isinstance(df_1h.index, pd.DatetimeIndex):
            sub_df_1h = df_1h[df_1h.index <= current_time]
        else:
            sub_df_1h = df_1h[df_1h['time'] <= current_time]
        
        if len(sub_df_1h) < 200: continue
            
        # 🔥 GỌI HÀM CỦA BẠN TẠI ĐÂY
        is_setup, sweep_bottom = check_setup(sub_df_1h, sub_df_15m)
        
        if is_setup and current_time != last_signal_time:
            entry_price = current_candle['close']
            sl_price = sweep_bottom
            risk = entry_price - sl_price
            tp_price = entry_price + (risk * 2) # RR 1:2
            
            trades.append({
                'entry_time': current_time,
                'entry_price': entry_price,
                'sl': sl_price,
                'tp': tp_price,
                'status': 'Đang chạy...',
                'exit_time': None
            })
            
            last_signal_time = current_time
            in_trade = True

# 3. IN KẾT QUẢ
print("="*40)
print(f"🏆 KẾT QUẢ BACKTEST {SYMBOL}")
print("="*40)

win = loss = pending = 0
for t in trades:
    print(f"🕒 {t['entry_time']} | Entry: ${t['entry_price']:.1f} | SL: ${t['sl']:.1f} | TP: ${t['tp']:.1f}")
    if 'Thắng' in t['status']: win += 1
    elif 'Thua' in t['status']: loss += 1
    else: pending += 1
    print(f"   => {t['status']}")
    print("-" * 30)

print(f"\n📊 TỔNG KẾT: {len(trades)} lệnh (✅ {win} Thắng | ❌ {loss} Thua | ⏳ {pending} Đang chạy)")
if (win + loss) > 0:
    print(f"🎯 Win Rate: {(win / (win + loss) * 100):.1f}%")