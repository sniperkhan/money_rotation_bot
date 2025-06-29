import json
import os
import shutil
from datetime import datetime, timedelta
import requests

KEYS_FILE = "keys.json"
BOTS_FOLDER = "bots"
TEMPLATE_FOLDER = "template"  # ✅ Make sure this folder name is correct


def load_keys():
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_keys(keys):
    sorted_keys = dict(sorted(keys.items(), key=lambda x: x[1].get("used", False)))
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted_keys, f, indent=4, ensure_ascii=False)


def send_telegram_message(chat_id, message, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Telegram message failed to {chat_id}: {e}")


def is_valid_key(key):
    keys = load_keys()
    return key in keys and not keys[key].get("used", False)


def is_key_expired(key):
    keys = load_keys()
    if not keys[key].get("used", False):
        return False

    expiry_str = keys[key].get("expiry_date")
    if not expiry_str:
        return True

    try:
        expiry = datetime.fromisoformat(expiry_str)
        return datetime.now() > expiry
    except ValueError:
        return True


def get_key_expiry_date(key):
    keys = load_keys()
    return keys[key].get("expiry_date")


def is_key_used_by_another_user(key, chat_id):
    keys = load_keys()
    assigned = keys[key].get("assigned_to")
    return assigned and str(assigned) != str(chat_id)


def get_user_data(key):
    keys = load_keys()
    return keys.get(key, {})


def activate_key(new_key, chat_id, bot_token, name="User"):
    keys = load_keys()

    # 🔍 Check if user already has an expired key
    old_key = None
    for k, v in keys.items():
        if v.get("chat_id") == str(chat_id) and v.get("expired", False):
            old_key = k
            break

    now = datetime.now()
    expiry = now + timedelta(days=90)  # ✅ 90 days validity

    if old_key:
        print(f"♻ Renewing expired key {old_key} → {new_key}")
        old_data = keys[old_key]
        del keys[old_key]  # 🔥 Remove old key

        keys[new_key] = {
            "used": True,
            "chat_id": str(chat_id),
            "bot_token": bot_token,
            "activation_date": now.isoformat(),
            "expiry_date": expiry.isoformat(),
            "assigned_to": str(chat_id),
            "name": old_data.get("name", name)
        }

        # 🔔 Send renewal message
        send_telegram_message(chat_id,
            f"🔄 Renewal Successful!\nAapki subscription 90 din ke liye renew ho gae hai.\n✅ New key: {new_key}",
            bot_token
        )

    else:
        keys[new_key] = {
            "used": True,
            "chat_id": str(chat_id),
            "bot_token": bot_token,
            "activation_date": now.isoformat(),
            "expiry_date": expiry.isoformat(),
            "assigned_to": str(chat_id),
            "name": name
        }

        # ✅ Send fresh activation message
        send_telegram_message(chat_id,
            f"✅ Activation Successful!\nAapka bot 90 din k liay active ho gaya hai.\n🔐 Key: {new_key}",
            bot_token
        )

    save_keys(keys)
    print(f"🔐 Key activated and saved for chat_id: {chat_id}")

    # 📁 Create user bot folder
    user_folder = os.path.join(BOTS_FOLDER, str(chat_id))
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        print(f"📁 Folder created for chat_id: {chat_id}")
    else:
        print(f"📁 Folder already exists. Reusing for chat_id: {chat_id}")

    # 🕓 created.txt file update
    created_file = os.path.join(user_folder, "created.txt")
    with open(created_file, "w") as f:
        f.write(now.isoformat())

    # 📁 Copy files from template folder to user bot folder
    if os.path.exists(TEMPLATE_FOLDER):
        for filename in os.listdir(TEMPLATE_FOLDER):
            src = os.path.join(TEMPLATE_FOLDER, filename)
            dst = os.path.join(user_folder, filename)
            shutil.copy(src, dst)
            print(f"✅ Copied {filename} to {user_folder}")
    else:
        print("⚠ Template folder missing. Cannot copy bot files.")
