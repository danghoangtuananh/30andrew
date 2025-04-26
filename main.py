import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("7487518680:AAGYIWG3nWuZtZLb4DWMkXtAKytSycURYy8")
CHAT_ID = os.getenv("690843443")
TAAPI_SECRET = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjgwOGJiMDM4MDZmZjE2NTFlYWE3MzM3IiwiaWF0IjoxNzQ1NDEwNjk2LCJleHAiOjMzMjQ5ODc0Njk2fQ.CQBtzsamPnFajjkUI3xODyRNHywFCW_Inr-7Wks9Aa0""TAAPI_SECRET")
INTERVAL = "1h"
COINS = ["BTC", "ETH"]  # Test trước 2 coin
CHECK_INTERVAL = 900  # 15 phút

def send_alert(msg):
    print("📨 Đang gửi telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, data=data)
        print("✅ Đã gửi Telegram:", res.status_code)
    except Exception as e:
        print("❌ Lỗi gửi:", e)

def get_taapi(symbol):
    base = "https://api.taapi.io"
    try:
        rsi = requests.get(f"{base}/rsi?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}/USDT&interval={INTERVAL}").json()["value"]
        ema21 = requests.get(f"{base}/ema?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}/USDT&interval={INTERVAL}&optInTimePeriod=21").json()["value"]
        ema50 = requests.get(f"{base}/ema?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}/USDT&interval={INTERVAL}&optInTimePeriod=50").json()["value"]
        return rsi, ema21, ema50
    except:
        return None, None, None

def get_price(symbol):
    try:
        return requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd").json()[symbol]["usd"]
    except:
        return None

def coin_to_cgid(symbol):
    return {
        "BTC": "bitcoin", "ETH": "ethereum"
    }.get(symbol.upper())

def build_alert(symbol, price, rsi, ema21, ema50):
    msg = f"""📢 *Test tín hiệu {symbol}/USDT*
Giá: {price}
RSI: {rsi:.2f}
EMA21: {ema21:.2f}
EMA50: {ema50:.2f}

✅ Đây là bản test. Bot đã chạy thành công!
"""
    return msg

def check_all():
    for coin in COINS:
        cg_id = coin_to_cgid(coin)
        price = get_price(cg_id)
        rsi, ema21, ema50 = get_taapi(coin)
        print(f"→ {coin}: giá={price}, RSI={rsi}, EMA21={ema21}")
        if price and rsi and ema21 and ema50:
            alert = build_alert(coin, round(price, 2), rsi, ema21, ema50)
            send_alert(alert)
        else:
            print(f"Bỏ qua {coin} do thiếu dữ liệu.")

if __name__ == "__main__":
    while True:
        print("🔁 Bắt đầu quét thị trường...")
        check_all()
        print("⏳ Chờ 15 phút...\n")
        time.sleep(CHECK_INTERVAL)
