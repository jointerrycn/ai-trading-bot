import google.generativeai as genai
from PIL import Image
from config import GEMINI_API_KEY

# Cấu hình khóa API
genai.configure(api_key=GEMINI_API_KEY)

# Khởi tạo mô hình
model = genai.GenerativeModel("gemini-2.5-flash")

def analyze_with_ai(prompt: str, image_path: str) -> str:
    """
    Phân tích hình ảnh và lời nhắc (prompt) bằng mô hình Gemini.
    """
    try:
        # Mở hình ảnh bằng Pillow. 
        # SDK Gemini tự động hiểu các đối tượng PIL Image.
        img = Image.open(image_path)
        
        # Truyền trực tiếp văn bản và đối tượng hình ảnh
        response = model.generate_content([prompt, img])
        
        return response.text

    except FileNotFoundError:
        return f"Lỗi: Không tìm thấy tệp tại đường dẫn {image_path}."
    except Exception as e:
        return f"Đã xảy ra lỗi API hoặc lỗi xử lý: {e}"

# Ví dụ sử dụng:
# result = analyze_with_ai("Hãy mô tả những gì có trong bức ảnh này.", "path/to/your/image.jpg")
# print(result)