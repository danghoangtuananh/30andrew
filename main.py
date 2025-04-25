
import os
import requests
import time
from collections import deque

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
CHECK_INTERVAL = 900

def send_alert(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    requests.post(url, data=data)

def get_btc_and_dominance():
    try:
        global_data = requests.get("https://api.coingecko.com/api/v3/global").json()["data"]
        btc_price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()["bitcoin"]["usd"]
        return btc_price, global_data["market_cap_percentage"]["btc"]
    except:
        return None, None

def check_market():
    btc_price, dominance = get_btc_and_dominance()
    if btc_price is None or dominance is None:
        send_alert("⚠️ Không lấy được dữ liệu BTC hoặc Dominance.")
    else:
        send_alert(f"✅ BTC: {btc_price}$ | Dominance: {dominance:.2f}%")

if __name__ == "__main__":
    while True:
        check_market()
        time.sleep(CHECK_INTERVAL)
