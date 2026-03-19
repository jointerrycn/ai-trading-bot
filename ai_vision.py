import mplfinance as mpf
import google.generativeai as genai
import os

# 🔥 CẤU HÌNH API GEMINI (Lấy miễn phí tại Google AI Studio)
GEMINI_API_KEY = "AIzaSyBdJ1T-DdoebF0AhESqpv7uLQT3sEdKqZ4"
genai.configure(api_key=GEMINI_API_KEY)

def create_chart_image(df, symbol, filename="temp_chart.png"):
    """Vẽ biểu đồ nến từ DataFrame và lưu thành file ảnh"""
    df_plot = df.copy()
    
    # mplfinance yêu cầu index phải là DatetimeIndex
    df_plot['time'] = pd.to_datetime(df_plot['time'], unit='ms') # Đảm bảo đúng định dạng thời gian
    df_plot.set_index('time', inplace=True)
    
    # Chỉ vẽ 50 nến gần nhất cho AI dễ nhìn (không bị nén quá nhỏ)
    df_recent = df_plot.iloc[-50:]
    
    # Vẽ và lưu ảnh (style 'yahoo' nhìn giống TradingView)
    mpf.plot(df_recent, type='candle', style='yahoo', 
             title=f"{symbol} - 15m Setup", 
             volume=False, # Tạm tắt volume cho chart đỡ rối, nếu thích bật lên là True
             savefig=filename)
    
    return filename

def get_ai_evaluation(image_path):
    """Gửi ảnh cho Gemini Vision để nhận xét"""
    try:
        # Sử dụng model Gemini 1.5 Flash (Cực nhanh và xịn cho xử lý ảnh)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Upload ảnh lên hệ thống của Google
        sample_file = genai.upload_file(path=image_path)
        
        # 🔥 Câu Prompt (Thần chú) định hướng tư duy cho AI
        prompt = """
        Bạn là một Trader Price Action thực chiến. Đây là biểu đồ 15 phút vừa xuất hiện setup LONG (Quét thanh khoản đáy -> Phá vỡ cấu trúc đỉnh -> Tạo đáy sau cao hơn). 
        Nhiệm vụ của bạn:
        1. Đánh giá vùng giá hiện tại có bị nhiễu (choppy/nhiều râu nến) hay không?
        2. Chấm điểm setup này từ 1 đến 10 dựa trên độ mượt của cấu trúc.
        Trả lời CỰC KỲ NGẮN GỌN dưới 50 chữ.
        """
        
        # Gọi AI sinh text
        response = model.generate_content([sample_file, prompt])
        
        # Dọn dẹp file trên server Google để tránh rác
        genai.delete_file(sample_file.name)
        
        return response.text
    except Exception as e:
        return f"⚠️ AI Vision tạm thời bận: {e}"