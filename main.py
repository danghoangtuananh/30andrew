import os
import requests
import time

TELEGRAM_TOKEN = os.getenv("7487518680:AAGYIWG3nWuZtZLb4DWMkXtAKytSycURYy8")
CHAT_ID = os.getenv("690843443")
TAAPI_SECRET = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjgwOGJiMDM4MDZmZjE2NTFlYWE3MzM3IiwiaWF0IjoxNzQ1NDEwNjk2LCJleHAiOjMzMjQ5ODc0Njk2fQ.CQBtzsamPnFajjkUI3xODyRNHywFCW_Inr-7Wks9Aa0")
INTERVAL = "1h"
COINS = ["BTC", "ETH", "BNB", "SOL", "ADA", "MATIC", "XRP", "APT", "ARB"]
CHECK_INTERVAL = 900  # 15 phút

def send_alert(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"Lỗi gửi Telegram: {e}")

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
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        return requests.get(url).json()[symbol]["usd"]
    except:
        return None

def coin_to_cgid(symbol):
    mapping = {
        "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
        "SOL": "solana", "ADA": "cardano", "MATIC": "matic-network",
        "XRP": "ripple", "APT": "aptos", "ARB": "arbitrum"
    }
    return mapping.get(symbol.upper())

def calc_rr(entry, sl, tp):
    try:
        return round(abs(tp - entry) / abs(entry - sl), 2)
    except:
        return 0

def build_alert(symbol, price, rsi, ema21, ema50):
    entry = price
    sl = round(entry * 0.97, 4)
    tp1 = round(entry * 1.03, 4)
    tp2 = round(entry * 1.05, 4)
    rr = calc_rr(entry, sl, tp1)
    trend = "Long"

    if rsi > 70 and price < ema21 and price < ema50:
        trend = "Short"
        sl = round(entry * 1.03, 4)
        tp1 = round(entry * 0.97, 4)
        tp2 = round(entry * 0.95, 4)
        rr = calc_rr(entry, tp1, sl)

    msg = f"""📢 *Kèo Margin x5 - {symbol}/USDT*
Hướng: *{trend}*
Entry: {entry}
SL: {sl}
TP1: {tp1}
TP2: {tp2}
R:R = {rr}:1

📊 RSI: {rsi:.2f}
📈 EMA21: {ema21:.2f}, EMA50: {ema50:.2f}
"""
    if rr >= 2:
        msg += "\n🔥 Chiến lược: Scale-in mạnh, giữ lâu"
    elif rr >= 1.4:
        msg += "\n✅ Vào 5%, scale-in nếu breakout xác nhận"
    elif rr >= 1.2:
        msg += "\n⚠️ Vào nhẹ, SL chặt. TP1 chốt 50%, TP2 giữ tiếp"
    else:
        msg += "\n🚫 R:R thấp. Không nên vào lệnh này"

    return msg

def check_all():
    for coin in COINS:
        cg_id = coin_to_cgid(coin)
        price = get_price(cg_id)
        rsi, ema21, ema50 = get_taapi(coin)
        if price and rsi and ema21 and ema50:
            if (price > ema21 and rsi > 50) or (rsi > 70 and price < ema21):
                alert = build_alert(coin, round(price, 4), rsi, ema21, ema50)
                send_alert(alert)
        else:
            print(f"Bỏ qua {coin} do thiếu dữ liệu.")

if __name__ == "__main__":
    while True:
        check_all()
        time.sleep(CHECK_INTERVAL)
