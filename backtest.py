import pandas as pd
import numpy as np
from models.kbd1 import signal


def trailing_sl(df, idx, direction):
    """
    idx = current candle index (integer position)
    direction = 1 for buy, -1 for sell
    """

    if idx < 3:
        return np.nan

    window = df.iloc[idx - 3 : idx]  # previous 3 completed candles

    if direction == 1:
        return window["low"].min()
    else:
        return window["high"].max()


def backtest_kbd1(df: pd.DataFrame):
    df = df.copy()
    trades = []

    position = None

    for i in range(3, len(df)):
        row = df.iloc[i]

        # --------------------------------------------------
        # ENTRY
        # --------------------------------------------------
        if position is None:
            sig = signal(df.iloc[: i + 1])

            if sig.iloc[0]["signal"] == "buy":
                position = {
                    "side": "buy",
                    "entry_idx": i,
                    "entry_date": df.index[i],
                    "entry_price": sig.iloc[0]["entry_price"],
                }

            elif sig.iloc[0]["signal"] == "sell":
                position = {
                    "side": "sell",
                    "entry_idx": i,
                    "entry_date": df.index[i],
                    "entry_price": sig.iloc[0]["entry_price"],
                }

            continue

        # --------------------------------------------------
        # EXIT (TRAILING STOP)
        # --------------------------------------------------
        direction = 1 if position["side"] == "buy" else -1
        sl = trailing_sl(df, i, direction)

        # BUY exit
        if position["side"] == "buy" and row["low"] <= sl:
            exit_price = sl
            trades.append(
                {
                    **position,
                    "exit_date": df.index[i],
                    "exit_price": exit_price,
                    "pnl": exit_price - position["entry_price"],
                }
            )
            position = None

        # SELL exit
        elif position["side"] == "sell" and row["high"] >= sl:
            exit_price = sl
            trades.append(
                {
                    **position,
                    "exit_date": df.index[i],
                    "exit_price": exit_price,
                    "pnl": position["entry_price"] - exit_price,
                }
            )
            position = None

    return pd.DataFrame(trades)
