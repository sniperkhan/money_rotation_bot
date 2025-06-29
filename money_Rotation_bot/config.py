import ccxt

exchange = ccxt.binance({
    'enableRateLimit': True
})

def get_all_spot_symbols():
    """
    Sirf Binance ke real spot symbols (USDT pairs) return karta hai
    - No leveraged, testnet, meme or fake pairs
    """
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

