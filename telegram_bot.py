import requests
from config import API_TOKEN, CHAT_ID

def send_message(text):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text
    }
    requests.post(url, data=data)