import os
import requests
import logging

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.error("Telegram token or chat_id is not set")
        return None

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    try:
        r = requests.post(url, json=payload)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        logging.error(f"Error sending Telegram message: {e}")
        return None