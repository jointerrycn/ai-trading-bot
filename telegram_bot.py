import requests
from config import TELEGRAM_TOKEN, CHAT_ID


def send_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")


def send_photo_and_message(photo_path, caption):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"

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