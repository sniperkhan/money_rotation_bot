import json
import ccxt
import pandas as pd
import time
from datetime import datetime
import os

def load_keys():
    with open("keys.json", "r", encoding="utf-8") as f:
        return json.load(f)

exchange = ccxt.binance({
    'enableRateLimit': True
})

def fetch_ohlcv(symbol, timeframe='4h', limit=100):
    """Binance se OHLCV data fetch karta hai"""
    ...
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        print(f"[❌ ERROR] Failed to fetch data for {symbol} | Reason: {e}")
        return None

def calculate_ema(df, period=50):
    """EMA calculate karta hai"""
    return df['close'].ewm(span=period, adjust=False).mean()

def is_bullish_trend(df):
    """EMA50 > EMA200 aur price above dono EMAs ho"""
    df['ema50'] = calculate_ema(df, 50)
    df['ema200'] = calculate_ema(df, 200)
    last = df.iloc[-1]
    return (
        last['ema50'] > last['ema200'] and
        last['close'] > last['ema50'] and
        last['close'] > last['ema200']
    )

def detect_support(df, bounce_limit=3, lookback=50):
    """
    Simple support detection using bounce logic
    - Looks back last X candles
    - Finds price levels with repeated touches (bounces)
    """
    supports = []
    lows = df['low'].tail(lookback).values

    for i in range(len(lows)):
        count = 0
        for j in range(i + 1, len(lows)):
            if abs(lows[i] - lows[j]) / lows[i] < 0.01:  # less than 1% difference
                count += 1
        if count >= bounce_limit:
            supports.append(lows[i])

    # Remove duplicates / similar supports
    final_supports = []
    for s in supports:
        if not any(abs(s - fs) / s < 0.01 for fs in final_supports):
            final_supports.append(s)
    return final_supports

def is_price_near_support(current_price, support_levels, margin=0.015):
    """
    Check if current price is near any detected support level
    Margin default is 1.5%
    """
    for level in support_levels:
        if abs(current_price - level) / current_price <= margin:
            return True
    return False

def detect_rotating_sector():
    """
    Detects which sector is currently rotating based on 1D & 3D price change
    Returns best sector and coins in that sector
    """
    try:
        with open("sectors.json") as f:
            sectors = json.load(f)
    except Exception as e:
        print("Error loading sector file:", e)
        return None, []

    best_sector = None
    best_performance = -999
    sector_coins = []

    for sector, coins in sectors.items():
        total_change = 0
        count = 0

        for coin in coins:
            df = fetch_ohlcv(coin, '1d', 4)
            if df is None or len(df) < 4:
                continue
            change_1d = (df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1]
            change_3d = (df['close'].iloc[-1] - df['open'].iloc[-3]) / df['open'].iloc[-3]
            total_change += (change_1d + change_3d)
            count += 1

        if count > 0:
            avg_change = total_change / count
            if avg_change > best_performance:
                best_performance = avg_change
                best_sector = sector
                sector_coins = sectors[sector]

    return best_sector, sector_coins

def detect_market_cap_rotation():
    """
    Detects current cap rotation: Large / Mid / Small
    Based on 1D + 3D % change average
    """
    try:
        with open("market_caps.json") as f:
            caps = json.load(f)
    except Exception as e:
        print("Error loading market cap file:", e)
        return None

    best_cap = None
    best_performance = -999

    for cap_type, coins in caps.items():
        total_change = 0
        count = 0

        for coin in coins:
            df = fetch_ohlcv(coin, '1d', 4)
            if df is None or len(df) < 4:
                continue
            change_1d = (df['close'].iloc[-1] - df['open'].iloc[-1]) / df['open'].iloc[-1]
            change_3d = (df['close'].iloc[-1] - df['open'].iloc[-3]) / df['open'].iloc[-3]
            total_change += (change_1d + change_3d)
            count += 1

        if count > 0:
            avg_change = total_change / count
            if avg_change > best_performance:
                best_performance = avg_change
                best_cap = cap_type

    return best_cap
