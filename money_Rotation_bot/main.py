# ✅ Auto delete old folders (MUST RUN FIRST)
from auto_delete_manager import delete_old_folders
delete_old_folders()

# 📦 Import key system
from key_manager import (
    is_valid_key, get_user_data,
    is_key_expired, get_key_expiry_date,
    activate_key, is_key_used_by_another_user
)

# 🟡 STEP: USER ACTIVATION
print("🔐 Please enter your activation key:")
user_key = input("➡ Key: ").strip()

if not is_valid_key(user_key):
    print("❌ Invalid key. Please contact support.")
    exit()

if is_key_expired(user_key):
    print("❌ Your key has expired. Please renew your subscription.")
    print(f"🕓 Expired on: {get_key_expiry_date(user_key)}")
    exit()

# 🟡 Ask for bot token only
print("📥 Please enter your Telegram Bot Token:")
TELEGRAM_TOKEN = input("➡ Bot Token: ").strip()

# 🔍 Auto detect chat ID
def get_chat_id(token):
    import time
    import requests
    print("📨 Now send ANY message to your Telegram bot...")
    for _ in range(10):
        try:
            updates = requests.get(f"https://api.telegram.org/bot{token}/getUpdates").json()
            messages = updates.get("result", [])
            for msg in reversed(messages):
                if "message" in msg and "chat" in msg["message"]:
                    return msg["message"]["chat"]["id"]
        except Exception as e:
            print("⏳ Waiting for message...")

        time.sleep(3)
    return None

TELEGRAM_CHAT_ID = get_chat_id(TELEGRAM_TOKEN)

if not TELEGRAM_CHAT_ID:
    print("❌ Failed to detect chat ID. Please send a message to your bot and try again.")
    exit()

# 🚫 Prevent key reuse by another user
if is_key_used_by_another_user(user_key, TELEGRAM_CHAT_ID):
    print("🚫 This key is already in use by another user.")
    exit()

# ✅ Auto activate key (if not already activated)
user_data = get_user_data(user_key)
if not user_data.get("used"):
    activate_key(user_key, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN)
    print(f"✅ Key successfully activated & expiry set for chat_id: {TELEGRAM_CHAT_ID}")

# ✅ Create user folder and created.txt
import os
from datetime import datetime

FOLDER_NAME = f"bots/{TELEGRAM_CHAT_ID}"
if not os.path.exists(FOLDER_NAME):
    os.makedirs(FOLDER_NAME)
    with open(os.path.join(FOLDER_NAME, "created.txt"), "w") as f:
        f.write(datetime.now().isoformat())

# ✅ Logging Setup (after folder creation)
import logging
from logging.handlers import RotatingFileHandler

log_file_path = os.path.join(FOLDER_NAME, "logs.txt")
log_handler = RotatingFileHandler(log_file_path, maxBytes=100 * 1024, backupCount=1)
log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
log_handler.setFormatter(log_formatter)

logging.basicConfig(
    level=logging.INFO,
    handlers=[log_handler, logging.StreamHandler()]
)
log = logging.getLogger()

# ⌛ Expiry system for bot
import requests
from expiry_manager import is_expired, get_expiry_date
expiry = get_expiry_date()
if not expiry or is_expired(expiry):
    log.error("❌ Bot expired. Please renew your subscription.")
    exit()

# 🧠 Bot core logic imports
from utils import (
    fetch_ohlcv, detect_rotating_sector,
    detect_market_cap_rotation
)
from evaluate import evaluate_coin
from config import get_all_spot_symbols
from filters import is_valid_symbol, has_already_sent, mark_sent

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
            log.error(f"Telegram error: {response.text}")
    except Exception as e:
        log.error(f"Telegram send failed: {e}")

# 🔔 Confirmation message after activation
send_telegram_message("✅ Bot activated successfully!\nNow scanning for trade setups...")

# 🔁 Main trading loop
import time

def main():
    while True:
        log.info("🔁 Checking market...")
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
                log.info(f"✅ Signal sent: {symbol}")
                time.sleep(2)
            else:
                log.info(f"[⛔] No valid setup for {symbol}")

        log.info("✅ Cycle complete. Sleeping 15 mins...\n")
        time.sleep(900)

if __name__ == "__main__":
    main()
