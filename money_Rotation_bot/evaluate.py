from utils import fetch_ohlcv, is_bullish_trend, detect_support, is_price_near_support
import json

def evaluate_coin(symbol, btc_df, active_sector, sector_coins, active_cap):
    print(f"\n➡ Evaluating {symbol}")  # ⬅ YEH LINE 1ST

    df = fetch_ohlcv(symbol, '4h', 100)
    if df is None or len(df) < 50:
        print(f"❌ {symbol} rejected: Data fetch issue or too short")
        return None

    if not is_bullish_trend(df):
        print(f"❌ {symbol} rejected: Not bullish trend")
        return None

    support_levels = detect_support(df)
    current_price = df['close'].iloc[-1]
    if not is_price_near_support(current_price, support_levels):
        print(f"❌ {symbol} rejected: Not near support")
        return None

    if btc_df is None or len(btc_df) < 50:
        print(f"❌ {symbol} rejected: BTC data missing")
        return None

    btc_supports = detect_support(btc_df)
    btc_price = btc_df['close'].iloc[-1]
    if not is_price_near_support(btc_price, btc_supports):
        print(f"❌ {symbol} rejected: BTC not near support")
        return None

    if symbol not in sector_coins:
        print(f"❌ {symbol} rejected: Not in active sector")
        return None

    with open("market_caps.json") as f:
        caps = json.load(f)
    cap_type = next((ct for ct, coins in caps.items() if symbol in coins), None)
    if cap_type != active_cap:
        print(f"❌ {symbol} rejected: Market cap mismatch")
        return None

    sl = min(support_levels)
    risk = current_price - sl
    if risk <= 0:
        print(f"❌ {symbol} rejected: Invalid risk calculation")
        return None

    tp1 = current_price + (risk * 2)
    tp2 = current_price + (risk * 2.5) if ((risk * 2.5) / current_price) * 100 >= 7 else None
    tp3 = current_price + (risk * 3) if ((risk * 3) / current_price) * 100 >= 9 else None

    rr = round((tp1 - current_price) / risk, 2)
    tp1_percent = ((tp1 - current_price) / current_price) * 100
    if rr < 2 or tp1_percent < 5:
        print(f"❌ {symbol} rejected: RR < 2 or TP1 < 5%")
        return None

    print(f"✅ {symbol} PASSED! Sending signal...")

    reason = "Bullish trend + Price near support + BTC support + Sector & Cap matched"
    signal_msg = f"""
📊 Trade Signal Generated

🔹 Symbol: {symbol}
🎯 Entry: ${round(current_price, 4)}
🔻 Stop-loss: ${round(sl, 4)}
🎯 Take Profit 1: ${round(tp1, 4)}

"""  # 🧠 TP2 & TP3 conditionally append:
    if tp2:
        signal_msg += f"🎯 Take Profit 2: ${round(tp2, 4)}\n"
    if tp3:
        signal_msg += f"🎯 Take Profit 3: ${round(tp3, 4)}\n"

    signal_msg += f"""📈 Risk-Reward: {rr}:1

🏷 Sector: {active_sector}
🏷 Market Cap: {cap_type}

📌 Reason: {reason}
"""

    return signal_msg
