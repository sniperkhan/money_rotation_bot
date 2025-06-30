# ✅ Auto delete expired bot folders
from auto_delete_manager import delete_old_folders
delete_old_folders()

# ✅ Key management system
from key_manager import (
    is_valid_key, get_user_data,
    is_key_expired, get_key_expiry_date,
    activate_key, is_key_used_by_another_user
)

# 🔐 STEP 1: User Activation
print("🔐 Please enter your activation key:")
user_key = input("➡ Key: ").strip()

if not is_valid_key(user_key):
    print("❌ Invalid key. Please contact support.")
    exit()

print("📥 Please enter your Telegram Bot Token:")
bot_token = input("➡ Bot Token: ").strip()

# 🕵 STEP 2: Detect Chat ID (by asking user to message the bot)
import time, requests

print("📨 Now send ANY message to your Telegram bot...")
chat_id = None
for _ in range(30):  # Try for ~30 seconds
    time.sleep(1)
    try:
        updates = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates").json()
        messages = updates.get("result", [])
        for msg in reversed(messages):
            if "message" in msg:
                chat_id = msg["message"]["chat"]["id"]
                break
        if chat_id:
            break
    except Exception:
        pass

if not chat_id:
    print("❌ Failed to detect chat ID. Please send a message to your bot and try again.")
    exit()

chat_id = str(chat_id)

# 🚫 Check misuse
if is_key_used_by_another_user(user_key, chat_id):
    print("🚫 This key is already in use by another user.")
    exit()

if is_key_expired(user_key):
    print(f"❌ Your key has expired. Expiry date: {get_key_expiry_date(user_key)}")
    exit()

user_data = get_user_data(user_key)

if not user_data.get("used"):
    activate_key(user_key, chat_id, bot_token)

# 🗂 Folder and logging setup
import os
from datetime import datetime

FOLDER = f"bots/{chat_id}"
os.makedirs(FOLDER, exist_ok=True)
with open(os.path.join(FOLDER, "created.txt"), "w") as f:
    f.write(datetime.now().isoformat())

# 📝 Logging
import logging
from logging.handlers import RotatingFileHandler

log_file = os.path.join(FOLDER, "logs.txt")
handler = RotatingFileHandler(log_file, maxBytes=100000, backupCount=1)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[handler, logging.StreamHandler()])
log = logging.getLogger()

# 🕓 Check expiry again
from expiry_manager import is_expired, get_expiry_date
if is_expired(get_expiry_date()):
    log.error("❌ Bot expired. Please renew your subscription.")
    exit()

# 📤 Send activation message
def send_telegram(msg):
    try:
        r = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", json={
            "chat_id": chat_id, "text": msg, "parse_mode": "Markdown"
        })
        if r.status_code != 200:
            log.error(f"Telegram error: {r.text}")
    except Exception as e:
        log.error(f"Telegram send failed: {e}")

send_telegram("✅ Bot activated successfully!\nNow scanning for trade setups...")

# ♻ Bot core
import time
from utils import fetch_ohlcv, detect_rotating_sector, detect_market_cap_rotation
from evaluate import evaluate_coin
from config import get_all_spot_symbols
from filters import is_valid_symbol, has_already_sent, mark_sent

def main():
    while True:
        log.info("🔁 Checking market...")
        sector, sector_coins = detect_rotating_sector()
        cap = detect_market_cap_rotation()
        btc_df = fetch_ohlcv("BTC/USDT", '4h', 100)

        symbols = get_all_spot_symbols()
        for symbol in symbols:
            if not is_valid_symbol(symbol):
                continue
            if has_already_sent(symbol, chat_id):
                continue

            msg = evaluate_coin(symbol, btc_df, sector, sector_coins, cap)
            if msg:
                send_telegram(msg)
                mark_sent(symbol, chat_id)
                log.info(f"✅ Signal sent: {symbol}")
                time.sleep(2)
            else:
                log.info(f"[⛔] No valid setup for {symbol}")

        log.info("✅ Cycle complete. Sleeping 15 mins...\n")
        time.sleep(900)

if __name__ == "__main__":
    main()
