import requests

TELEGRAM_BOT_TOKEN = "7710715037:AAGNf0JKGeQi37HzySiSOM8tsZr_unnXoXg"
TELEGRAM_CHAT_ID = "bobbysmithh01"

def send_telegram_alert(message):
    if TELEGRAM_BOT_TOKEN == "7710715037:AAGNf0JKGeQi37HzySiSOM8tsZr_unnXoXg":
        print("[TELEGRAM MOCK] " + message)
        return
    try:
        url = f"https://api.telegram.org/bot7710715037:{AAGNf0JKGeQi37HzySiSOM8tsZr_unnXoXg}/sendMessage"
        data = {"chat_id": bobbysmithh01, "text": message}
        requests.post(url, json=data)
    except Exception as e:
        print(f"Telegram error: {e}")
