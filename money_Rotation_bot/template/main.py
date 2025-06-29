# ✅ Auto delete old folders (7 days after expiry)
from auto_delete_manager import delete_old_folders
delete_old_folders()

# 🔐 Key activation logic
from key_manager import (
    is_valid_key, get_user_data,
    is_key_expired, get_key_expiry_date,
    activate_key, is_key_used_by_another_user
)

print("🔐 Please enter your activation key:")
user_key = input("➡ Key: ").strip()

if not is_valid_key(user_key):
    print("❌ Invalid key. Please contact support.")
    exit()

if is_key_expired(user_key):
    print("❌ Your key has expired. Please renew your subscription.")
    print(f"🕓 Expired on: {get_key_expiry_date(user_key)}")
    exit()

user_data = get_user_data(user_key)
TELEGRAM_CHAT_ID = user_data.get("chat_id")
TELEGRAM_TOKEN = user_data.get("bot_token")

if is_key_used_by_another_user(user_key, TELEGRAM_CHAT_ID):
    print("🚫 This key is already in use by another user.")
    exit()

# ✅ Auto activate key
if not user_data.get("used"):
    activate_key(user_key, TELEGRAM_CHAT_ID)
    print("✅ Key activated & expiry date set.")

# 📁 Create user folder and created.txt
import os
from datetime import datetime

FOLDER_NAME = f"bots/{TELEGRAM_CHAT_ID}"
if not os.path.exists(FOLDER_NAME):
    os.makedirs(FOLDER_NAME)
    with open(os.path.join(FOLDER_NAME, "created.txt"), "w") as f:
        f.write(datetime.now().isoformat())

# ⏳ Check expiry again (to be safe)
from expiry_manager import is_expired, get_expiry_date
expiry = get_expiry_date()
if not expiry or is_expired(expiry):
    print("❌ Bot expired. Please renew your subscription.")
    exit()

# ⚙ Trading logic
from utils import (
    fetch_ohlcv, detect_rotating_sector,
    detect_market_cap_rotation
)
from evaluate import evaluate_coin
from config import get_all_spot_symbols
from filters import is_valid_symbol, has_already_sent, mark_sent

import requests
import time

# 📤 Telegram message sender
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Telegram error: {response.text}")
    except Exception as e:
        print(f"Telegram send failed: {e}")

# ✅ Activation complete message
send_telegram_message("✅ Bot activated successfully!\nNow scanning for trade setups...")

# 🔁 Main market scanning loop
def main():
    while True:
        print("🔁 Checking market...")
        sector, sector_coins = detect_rotating_sector()
        cap = detect_market_cap_rotation()
        btc_df = fetch_ohlcv("BTC/USDT", '4h', 100)
        all_symbols = get_all_spot_symbols()

        for symbol in all_symbols:
            if not is_valid_symbol(symbol):
                continue
            if has_already_sent(symbol, TELEGRAM_CHAT_ID):
                continue

            msg = evaluate_coin(symbol, btc_df, sector, sector_coins, cap)
            if msg:
                send_telegram_message(msg)
                mark_sent(symbol, TELEGRAM_CHAT_ID)
                time.sleep(2)
            else:
                print(f"[⛔] No setup for {symbol}")

        print("✅ Cycle complete. Sleeping 15 mins...\n")
        time.sleep(900)

if __name__ == "__main__":
    main()
