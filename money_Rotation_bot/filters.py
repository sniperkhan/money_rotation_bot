# filters.py

import re

def is_valid_symbol(symbol):
    symbol_upper = symbol.upper()

    # ❌ Filter: Stablecoins
    if any(stable in symbol_upper for stable in ['USDT/USDT', 'BUSD', 'USDC']):
        return False

    # ❌ Filter: Meme Coins
    meme_coins = ['SHIB', 'DOGE', 'FLOKI', 'PEPE', 'PIT', 'ELON']
    if any(meme in symbol_upper for meme in meme_coins):
        return False

    # ❌ Filter: Test/Fake/Bear/Bull Tokens
    banned_keywords = ['TEST', 'BULL', 'BEAR', 'DOWN', 'UP', '3L', '3S', '5L', '5S']
    if any(keyword in symbol_upper for keyword in banned_keywords):
        return False

    return True


import json
import os

def get_sent_file_path(chat_id):
    folder = f"bots/{chat_id}"
    return os.path.join(folder, "sent.json")

def has_already_sent(symbol, chat_id):
    sent_file = get_sent_file_path(chat_id)
    if not os.path.exists(sent_file):
        return False
    with open(sent_file) as f:
        data = json.load(f)
    return symbol in data

def mark_sent(symbol, chat_id):
    sent_file = get_sent_file_path(chat_id)
    data = {}
    if os.path.exists(sent_file):
        with open(sent_file) as f:
            data = json.load(f)
    data[symbol] = True
    with open(sent_file, "w") as f:
        json.dump(data, f, indent=4)
def is_fake_pump(df):
    """
    Fake pump detect karta hai:
    1. Bina real volume ke spike
    2. Sirf wick pump
    3. No retest or continuation
    """
    if len(df) < 5:
        return False

    recent = df.iloc[-1]
    prev = df.iloc[-2]

    # 1. Wick-only pump: candle body choti ho aur wick zyada
    body = abs(recent['close'] - recent['open'])
    wick = recent['high'] - recent['low']
    if wick > 2 * body and body / recent['open'] < 0.01:
        return True

    # 2. Sudden volume spike without trend
    recent_vol = recent['volume']
    avg_vol = df['volume'].iloc[-6:-1].mean()
    if recent_vol > avg_vol * 4 and recent['close'] < prev['close']:
        return True

    # 3. Sudden pump without base or retest
    price_change = (recent['close'] - prev['close']) / prev['close']
    if price_change > 0.10 and recent['low'] > prev['high']:
        return True

    return False
