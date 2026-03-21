import google.generativeai as genai
from PIL import Image
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

def analyze_with_ai(prompt: str, image_path: str) -> str:
    try:
        img = Image.open(image_path)

        model = genai.GenerativeModel("gemini-2.5-flash")

        response = model.generate_content([prompt, img])

        return response.text

    except FileNotFoundError:
        return f"Lỗi: Không tìm thấy tệp tại đường dẫn {image_path}."
    except Exception as e:
        return f"Lỗi API: {e}"