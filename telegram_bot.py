import requests
from config import API_TOKEN,CHAT_ID

def send_message(text):
    # Hàm cũ gửi chữ (giữ nguyên)
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

def send_photo_and_message(photo_path, caption):
    """Hàm VIP: Gửi kèm ảnh chart và nhận xét của AI"""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendPhoto"
    with open(photo_path, 'rb') as photo:
        payload = {
            "chat_id": CHAT_ID, 
            "caption": caption, 
            "parse_mode": "Markdown"
        }
        files = {"photo": photo}
        try:
            requests.post(url, data=payload, files=files)
        except Exception as e:
            print(f"Lỗi gửi Telegram Photo: {e}")