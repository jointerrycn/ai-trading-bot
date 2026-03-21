from google import genai
from PIL import Image
from config import GEMINI_API_KEY

# Khởi tạo client
client = genai.Client(api_key=GEMINI_API_KEY)
print(GEMINI_API_KEY)
def analyze_with_ai(prompt: str, image_path: str) -> str:
    try:
        img = Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, img]
        )

        return response.text

    except FileNotFoundError:
        return f"Lỗi: Không tìm thấy tệp tại đường dẫn {image_path}."
    except Exception as e:
        return f"Lỗi API: {e}"