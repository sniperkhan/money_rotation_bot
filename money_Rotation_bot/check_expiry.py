import json
import os
import shutil
import datetime
import requests

KEYS_FILE = "keys.json"
BOTS_FOLDER = "bots"

def load_keys():
    with open(KEYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_keys(keys):
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4, ensure_ascii=False)

def send_telegram_message(chat_id, message, bot_token):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print(f"❌ Message send failed to {chat_id}: {e}")

def check_expiry():
    print("🔍 Checking for expired keys...\n")
    now = datetime.datetime.now()
    today = now.date()
    keys = load_keys()
    keys_to_delete = []
    changed = False

    for key, info in keys.items():
        if not info.get("used"):
            continue

        try:
            expiry_str = info.get("expiry_date")
            if not expiry_str:
                continue

            expiry_date = datetime.datetime.fromisoformat(expiry_str).date()
            days_left = (expiry_date - today).days
            expired = today > expiry_date

            chat_id = info["chat_id"]
            token = info["bot_token"]
            bot_folder = os.path.join(BOTS_FOLDER, str(chat_id))

            # 🔔 7 din pehle reminder
            if days_left == 7 and not info.get("reminded", False):
                msg = (
                    "⚠ Warning!\n"
                    "Aapka bot 7 din baad expire ho jae ga.\n"
                    "🔁 Renewal ke liye team se rabta karein.\n"
                    "📞 Ya Sirf Reminder hai, Expiry se 1 din pehly renew karna behtar hoga!"
                )
                send_telegram_message(chat_id, msg, token)
                keys[key]["reminded"] = True
                print(f"📨 Reminder sent to: {chat_id}")
                changed = True

            # ❌ Bot expire ho gaya
            if expired and not info.get("expired", False):
                msg = (
                    "❌ Afsos!\n"
                    "Aapka bot expire ho chuka hai.\n"
                    "🛠 Data loss se bachny k liay within 7 days renew ker len, Dobara active karwane ke liye team se raabta karein."
                )
                send_telegram_message(chat_id, msg, token)
                keys[key]["expired"] = True
                print(f"📩 Expiry message sent to: {chat_id}")
                changed = True

            # 🧹 Purane expired bots delete karo (7 din ke baad)
            if info.get("expired", False):
                expiry_datetime = datetime.datetime.fromisoformat(expiry_str)
                if (now - expiry_datetime).days > 7:
                    if os.path.exists(bot_folder):
                        shutil.rmtree(bot_folder)
                        print(f"🗑 Deleted bot folder: {chat_id}")
                    else:
                        print(f"⚠ Folder not found for: {chat_id}")
                    keys_to_delete.append(key)
                    print(f"🧹 Removed from keys.json: {key}")
                    changed = True

        except Exception as e:
            print(f"⚠ Error processing key {key}: {e}")

    # Remove keys from keys.json
    for key in keys_to_delete:
        del keys[key]

    if changed:
        save_keys(keys)

    print("\n✅ Expiry check complete.")

if __name__ == "__main__":
    check_expiry()
