
import requests

def send_telegram_alert(message):
    token = "YOUR_BOT_TOKEN"
    chat_id = "@bobbysmithh01"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print("Telegram error:", e)
