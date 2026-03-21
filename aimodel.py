import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

for m in genai.list_models():
    print(m.name, m.supported_generation_methods)