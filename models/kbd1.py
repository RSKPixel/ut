import pandas as pd
import numpy as np


def signal(df: pd.DataFrame):
    # KBD1 - Key Breakout Day 1 - Trading Model
    # Author: Brent Penfold
    # When dow_cross occurs in the direction of the trend, enter a trade.
    # Exit with a trailing stop of high if bullish or low if bearish of the previous three candles.

    df = df.copy()
    signal = {
        "model": "KBD1",
        "signal": None,
        "setup_candle": None,
        "entry_date": None,
        "entry_price": None,
        "entry_day_sl": None,
    }

    if df.iloc[-1]["dow_cross"] and df.iloc[-1]["direction"] == 1:
        # Bullish Setup
        # Check for previous dow cross to identify setup candle
        buy_price = df.iloc[-1]["dow_cross"]
        sell_price = np.nan
        profit_points = np.nan
        setup_bar = False

        for i in range(len(df) - 2, -1, -1):
            if df.iloc[i]["direction"] == -1:
                sell_price = df.iloc[i]["dow_cross"]
                break

        if not np.isnan(sell_price):
            profit_points = buy_price - sell_price
            setup_bar = True

        if setup_bar and profit_points < 0:
            signal["signal"] = "buy"
            signal["entry_price"] = buy_price
            signal["setup_candle"] = df.index[-1]
            signal["entry_date"] = df.index[-1]
            signal["entry_day_sl"] = df.iloc[-1]["low"]

    if df.iloc[-1]["dow_cross"] and df.iloc[-1]["direction"] == -1:
        # Bearish Setup
        # Check for previous dow cross to identify setup candle

        sell_price = df.iloc[-1]["dow_cross"]
        buy_price = np.nan
        profit_points = np.nan
        setup_bar = False

        for i in range(len(df) - 2, -1, -1):
            if df.iloc[i]["direction"] == 1:
                buy_price = df.iloc[i]["dow_cross"]
                break

        if not np.isnan(buy_price):
            profit_points = sell_price - buy_price
            setup_bar = True

        if setup_bar and profit_points < 0:
            signal["signal"] = "sell"
            signal["entry_price"] = sell_price
            signal["setup_candle"] = df.index[-1]
            signal["entry_date"] = df.index[-1]
            signal["entry_day_sl"] = df.iloc[-1]["high"]

    return pd.DataFrame([signal])
