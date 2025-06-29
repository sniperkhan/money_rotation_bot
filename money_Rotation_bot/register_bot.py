import json
import os
from datetime import datetime

KEYS_FILE = "keys.json"

def load_keys():
    if not os.path.exists(KEYS_FILE):
        return {}
    with open(KEYS_FILE) as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, "w") as f:
        json.dump(keys, f, indent=4)

def main():
    keys = load_keys()

    print("🔐 Enter activation key:")
    user_key = input("➡ Key: ").strip()

    if user_key not in keys:
        print("❌ Key not found. Please make sure it's correct.")
        return

    # ✅ Check if key is already used
    if keys[user_key].get("used"):
        print("🚫 This key is already registered.")
        return

    print("👤 Enter your name:")
    name = input("➡ Name: ").strip()

    print("💬 Enter your Telegram Chat ID:")
    chat_id = input("➡ Chat ID: ").strip()

    print("🤖 Enter your Telegram Bot Token:")
    bot_token = input("➡ Bot Token: ").strip()

    keys[user_key]["name"] = name
    keys[user_key]["chat_id"] = chat_id
    keys[user_key]["bot_token"] = bot_token
    keys[user_key]["created"] = datetime.utcnow().strftime("%Y-%m-%d")
    keys[user_key]["used"] = True  # ✅ Mark as used

    save_keys(keys)
    print("✅ Bot registered successfully!")

if __name__ == "__main__":
    main()
