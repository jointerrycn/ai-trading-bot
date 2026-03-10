import requests

TOKEN = "8686620867:AAHmSBZUww3ySTfLA40bpM0Bs_3r1-7pSMg"
CHAT_ID = "1969573200"

def send_alert(message):

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    requests.post(url, data={
        "chat_id": CHAT_ID,
        "text": message
    })