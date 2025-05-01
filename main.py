import os
import requests
import time

# Khai báo thông tin cần thiết
TELEGRAM_TOKEN = os.getenv("7487518680:AAGYIWG3nWuZtZLb4DWMkXtAKytSycURYy8")
CHAT_ID = os.getenv("690843443")
TAAPI_SECRET = os.getenv("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjbHVlIjoiNjgwOGJiMDM4MDZmZjE2NTFlYWE3MzM3IiwiaWF0IjoxNzQ1Nzc5MDY4LCJleHAiOjMzMjUwMjQzMDY4fQ.2dmcZqnmM2nfAXvQp-ITizP9TGrRkuyZeaWwj0N9u9E")

INTERVAL = "1h"
COINS = ["BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "MATIC", "DOGE", "LTC", "APT"]
CHECK_INTERVAL = 900  # 15 phút

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        res = requests.post(url, data=payload)
        print(f"✅ Gửi telegram status: {res.status_code}")
    except Exception as e:
        print(f"❌ Lỗi gửi telegram:", e)

def get_taapi(symbol):
    base = "https://api.taapi.io"
    try:
        time.sleep(2)
        rsi_res = requests.get(f"{base}/rsi?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}/USDT&interval={INTERVAL}").json()
        ema21_res = requests.get(f"{base}/ema?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}/USDT&interval={INTERVAL}&optInTimePeriod=21").json()
        ema50_res = requests.get(f"{base}/ema?secret={TAAPI_SECRET}&exchange=binance&symbol={symbol}/USDT&interval={INTERVAL}&optInTimePeriod=50").json()

        rsi = rsi_res.get("value")
        ema21 = ema21_res.get("value")
        ema50 = ema50_res.get("value")

        if rsi is None or ema21 is None or ema50 is None:
            print(f"❌ Lỗi lấy TAAPI {symbol}: thiếu dữ liệu")
            print(f"RSI: {rsi_res} | EMA21: {ema21_res} | EMA50: {ema50_res}")
            return None, None, None

        return rsi, ema21, ema50
    except Exception as e:
        print(f"❌ Lỗi get_taapi({symbol}):", e)
        return None, None, None

def get_price(symbol):
    try:
        cg_mapping = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "SOL": "solana", "XRP": "ripple", "ADA": "cardano",
            "MATIC": "matic-network", "DOGE": "dogecoin",
            "LTC": "litecoin", "APT": "aptos"
        }
        id = cg_mapping.get(symbol.upper())
        price_res = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=usd").json()
        return price_res.get(id, {}).get("usd")
    except Exception as e:
        print(f"❌ Lỗi get_price({symbol}):", e)
        return None

def build_signal(symbol, price, rsi, ema21, ema50):
    entry = round(price, 4)
    trend = "Long"
    sl = round(entry * 0.97, 4)
    tp1 = round(entry * 1.03, 4)
    tp2 = round(entry * 1.05, 4)

    if rsi > 70 and price < ema21 and price < ema50:
        trend = "Short"
        sl = round(entry * 1.03, 4)
        tp1 = round(entry * 0.97, 4)
        tp2 = round(entry * 0.95, 4)

    rr = round(abs(tp1 - entry) / abs(entry - sl), 2) if entry != sl else 0

    msg = f"""📢 *{symbol}/USDT - {trend}*
Entry: {entry}
SL: {sl}
TP1: {tp1}
TP2: {tp2}
R:R = {rr}:1
RSI: {rsi:.2f}
EMA21: {ema21:.2f}
EMA50: {ema50:.2f}
"""
    return msg

def check_market():
    signals = []
    for coin in COINS:
        price = get_price(coin)
        rsi, ema21, ema50 = get_taapi(coin)
        print(f"→ {coin}: giá={price}, RSI={rsi}, EMA21={ema21}, EMA50={ema50}")
        if price and rsi and ema21 and ema50:
            if (price > ema21 and price > ema50 and rsi > 50) or (rsi > 70 and price < ema21 and price < ema50):
                signal = build_signal(coin, price, rsi, ema21, ema50)
                signals.append(signal)
        else:
            print(f"Bỏ qua {coin} vì thiếu dữ liệu.")

    if signals:
        all_signals = "\n\n".join(signals)
        send_telegram(f"🚀 *Tổng hợp tín hiệu Margin X5:*\n\n{all_signals}")
    else:
        send_telegram("❌ Không có tín hiệu đẹp, chờ chu kỳ tiếp theo!")

if __name__ == "__main__":
    while True:
        print("🔁 Bắt đầu quét thị trường...")
        check_market()
        print("⏳ Chờ 15 phút...\n")
        time.sleep(CHECK_INTERVAL)
