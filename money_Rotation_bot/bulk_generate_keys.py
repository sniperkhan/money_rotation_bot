import json
import random
import string
from datetime import datetime

KEYS_FILE = "keys.json"

def generate_key():
    part1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    part2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"KEY-{part1}-{part2}"

def load_keys():
    try:
        with open(KEYS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_keys(keys):
    # 🔃 Sort keys: unused (False) first, used (True) last
    sorted_keys = dict(
        sorted(keys.items(), key=lambda item: item[1].get("used", False))
    )
    with open(KEYS_FILE, "w", encoding="utf-8") as f:
        f.seek(0)
        f.truncate()
        json.dump(sorted_keys, f, indent=4, ensure_ascii=False)

def bulk_generate(n):
    keys = load_keys()
    for _ in range(n):
        new_key = generate_key()
        while new_key in keys:
            new_key = generate_key()
        keys[new_key] = {
            "used": False
        }
    save_keys(keys)
    print(f"✅ {n} keys generated successfully.")

if __name__ == "__main__":
    bulk_generate(10)  # Change 10 to any number like 5000
