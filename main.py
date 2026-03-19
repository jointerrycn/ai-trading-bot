import time
import os # Thêm thư viện này để dọn rác (xóa ảnh temp)
from config import SYMBOLS, TIMEFRAME_1H, TIMEFRAME_15M
from data import get_ohlc
from strategy import check_setup, trend_ok 

# 🔥 Cập nhật Import: Thêm các hàm AI và hàm gửi ảnh Telegram
from telegram_bot import send_message, send_photo_and_message
from ai_vision import create_chart_image, get_ai_evaluation

# Sổ tay ghi nhớ chống spam
last_signaled_time = {} 

def run():
    for symbol in SYMBOLS:
        try:
            print(f"\n🔍 Checking {symbol}...")

            # 1. Lấy data
            df_1h = get_ohlc(symbol, TIMEFRAME_1H)
            df_15m = get_ohlc(symbol, TIMEFRAME_15M)

            # 2. Debug nhanh
            trend = trend_ok(df_1h)
            print(f"👉 Trend 1H: {'✅ Tốt' if trend else '❌ Xấu'}")

            # 3. Check toàn bộ setup (Trend -> Sweep -> Break -> HL)
            is_setup_valid,sl_price = check_setup(df_1h, df_15m)

            if is_setup_valid:
                current_candle_time = df_15m['time'].iloc[-1] 
                
                # 🔥 4. KIỂM TRA CHỐNG SPAM
                if symbol not in last_signaled_time or last_signaled_time[symbol] != current_candle_time:
                    
                    print(f"✅ Đã xác nhận Setup Toán học cho {symbol}. Đang nhờ AI Vision đánh giá...")
                    
                    # --- TÍCH HỢP AI VISION TẠI ĐÂY ---
                    # Bước A: Bot tự động vẽ chart và lưu ảnh
                    image_filename = create_chart_image(df_15m, symbol)
                    
                    # Bước B: Gửi ảnh cho Gemini đọc và lấy nhận xét
                    ai_comment = get_ai_evaluation(image_filename)
                    
                    # Bước C: Soạn tin nhắn VIP
                    msg = f"🔥 **BẮT ĐƯỢC SETUP: {symbol} (LONG)** 🔥\n\n"
                    msg += f"✅ Đã xác nhận chuỗi: Trend ➔ Sweep ➔ Break ➔ HL.\n\n"
                    msg += f"🤖 **AI ĐÁNH GIÁ (GEMINI):**\n_{ai_comment}_\n\n"
                    msg += f"👉 Chờ giá Retest lại vùng HL để Entry!"
                    msg += f"🛑 Stoploss tại: {sl_price}"
                    # Bước D: Bắn Telegram kèm hình ảnh chart
                    send_photo_and_message(image_filename, msg)
                    print(f"🚀 Đã gửi Telegram + AI cho {symbol}!")
                    
                    # Bước E: Xóa ảnh temp trên máy tính cho nhẹ ổ cứng
                    if os.path.exists(image_filename):
                        os.remove(image_filename)
                    # ----------------------------------
                    
                    # Ghi nhớ lại thời gian của nến này
                    last_signaled_time[symbol] = current_candle_time
                else:
                    print(f"👉 Full Setup (15m): ✅ HỢP LỆ (Nhưng đã báo Telegram rồi, đang chờ qua nến mới...)")
            else:
                print(f"👉 Full Setup (15m): ⏳ Đang chờ...")

        except Exception as e:
            print(f"❌ Error {symbol}: {e}")

# Vòng lặp chạy liên tục
while True:
    print("\n" + "="*30)
    print("🔄 BẮT ĐẦU LƯỢT QUÉT MỚI")
    print("="*30)
    
    run()
    
    # Nghỉ 5 phút (300 giây) rồi quét lại
    time.sleep(300)