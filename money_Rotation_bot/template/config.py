import json
import ccxt

def load_config(chat_id):
    with open("keys.json", "r", encoding="utf-8") as f:
        keys = json.load(f)
    for key_data in keys.values():
        if str(key_data.get("chat_id")) == str(chat_id):
            return {
                "bot_token": key_data.get("bot_token"),
                "expiry": key_data.get("expiry_date")
            }
    return None

exchange = ccxt.binance({
    'enableRateLimit': True
})

def get_all_spot_symbols():
    symbols = []
    try:
        markets = exchange.load_markets()
        for symbol in markets:
            market = markets[symbol]
            if (
                market['quote'] == 'USDT' and
                market['spot'] and
                not market['symbol'].endswith('DOWN/USDT') and
                not market['symbol'].endswith('UP/USDT') and
                not market['symbol'].startswith('1000') and
                '/USDT' in market['symbol']
            ):
                symbols.append(market['symbol'])
    except Exception as e:
        print(f"[❌ CONFIG ERROR] Could not fetch Binance symbols | Reason: {e}")
    return symbols
