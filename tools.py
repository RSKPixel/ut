import numpy as np
import pandas as pd

import numpy as np
import pandas as pd


import numpy as np
import pandas as pd


def compute_dow_points(df):
    df = df.copy()
    print(df.head())

    # -------------------------------------
    # 1) Normalize swing column
    # -------------------------------------
    # Convert high/low or H/L to direction signals
    swing_map = {"H": -1, "high": -1, "L": 1, "low": 1}

    df["dir"] = df["swing"].map(swing_map)

    # If your swing is already numeric like 1 / -1
    df["dir"] = df["dir"].fillna(df["swing"])

    df["dir"] = df["dir"].ffill().fillna(0)

    # -------------------------------------
    # 2) First bar of new direction
    # -------------------------------------
    df["dfirstBarNewDir"] = np.where(df["dir"] != df["dir"].shift(), df["dir"], 0)

    # -------------------------------------
    # 3) Peaks and Troughs
    # -------------------------------------
    df["dPeak"] = df["swing_point"].where(df["dfirstBarNewDir"] == -1)
    df["dTrough"] = df["swing_point"].where(df["dfirstBarNewDir"] == 1)

    # -------------------------------------
    # 4) Build Dow Trend Line
    # -------------------------------------
    df["ddow_trend"] = np.nan
    trend = None

    for i in range(len(df)):
        row = df.iloc[i]
        H = row["high"]
        L = row["low"]
        peak = row["dPeak"]
        trough = row["dTrough"]

        if trend is None:
            trend = (H + L) / 2

        prev_L = df["low"].shift().iloc[i]
        prev_H = df["high"].shift().iloc[i]

        # Uptrend region
        if prev_L >= trend:
            if L < trend:
                trend = max(peak if not pd.isna(peak) else -np.inf, H)
            else:
                trend = max(trough if not pd.isna(trough) else trend, trend)
        # Downtrend region
        else:
            if H > trend:
                trend = min(trough if not pd.isna(trough) else np.inf, L)
            else:
                trend = min(peak if not pd.isna(peak) else trend, trend)

        df.iloc[i, df.columns.get_loc("ddow_trend")] = trend

    # -------------------------------------
    # 5) Direction & signal
    # -------------------------------------
    df["mid"] = (df["high"] + df["low"]) / 2
    df["ddow_dir"] = np.sign(df["mid"] - df["ddow_trend"])

    df["ddow_signal"] = np.where(
        df["ddow_dir"] != df["ddow_dir"].shift(), df["ddow_dir"], 0
    )
    print(df[["dPeak", "dTrough", "ddow_trend", "ddow_dir", "ddow_signal"]].head(20))
    return df


# def ddt(df: pd.DataFrame) -> pd.DataFrame:
#     # Daily Dow Theory (DDT) Indicator
#     df = df.copy()
#     n = len(df)
#     df["dow_high"] = np.nan
#     df["dow_low"] = np.nan
#     df["dow_points"] = np.nan
#     df["direction"] = np.nan
#     current_high = -np.inf
#     current_low = np.inf
#     direction = 0  # 1=up, -1=down, 0=unknown

#     for d in range(1, n):
#         current_high = (
#             df.iloc[d - 1]["swing_point"]
#             if df.iloc[d]["swing"] == "high"
#             else current_high
#         )
#         current_low = (
#             df.iloc[d - 1]["swing_point"]
#             if df.iloc[d]["swing"] == "low"
#             else current_low
#         )
#         low = df.iloc[d - 1]["low"]
#         high = df.iloc[d - 1]["high"]
#         swing = df.iloc[d]["swing"] if df.iloc[d]["swing"] in ["high", "low"] else swing

#         if np.isnan(current_high) and np.isnan(current_low):
#             continue

#     return df


def asc(close: pd.Series, lookback=20) -> pd.Series:
    n = len(close)
    seq_close = np.full(n, np.nan)
    seq_hl = np.where(close > close.shift(-1), True, False)

    for d in range(n):
        # d = 25

        if d < lookback - 1:
            continue

        lookarea = close[d - lookback + 1 : d + 1]
        seq_cond = seq_hl[d - lookback + 1 : d + 1]

        if close.iloc[d] > close.iloc[d - lookback + 1]:
            seq_close[d] = close.iloc[d]
            continue

        seq_closes = []
        found_high = False
        i = 0

        try:

            for i in range(0, len(lookarea) - 1, 1):
                if found_high and not seq_hl[i]:
                    break

                if seq_cond[i]:
                    found_high = True

                if found_high:
                    seq_closes.append(lookarea.iloc[i])

            seq_close[d] = max(seq_closes)
        except Exception as e:
            print(e)

    return pd.Series(seq_close, index=close.index)


def lv(high: pd.Series, low: pd.Series, close: pd.Series, lookback=4) -> pd.Series:
    """Long Day Volatility (LDV) = 1 when 4-day close range <= 4-day ATR"""

    # ---- ATR(4) using simplified TR = max(high, prev_close)-min(low, prev_close) ----
    prev_close = close.shift(1)

    # element-wise max and min
    true_high = pd.concat([high, prev_close], axis=1).max(axis=1)
    true_low = pd.concat([low, prev_close], axis=1).min(axis=1)

    tr = true_high - true_low  # simplified TR

    atr4 = tr.rolling(4).mean()  # simple 4-period average

    # ---- 4-day Close Range ----
    cr4 = close.rolling(lookback).max() - close.rolling(lookback).min()

    # ---- LDV Condition: 1 if close range <= ATR ----
    ldv_value = (cr4 <= atr4).astype(int)

    return ldv_value


def weekly_rdata(data: pd.DataFrame) -> pd.DataFrame:
    """Resample daily OHLC data to weekly OHLC data."""
    data = data.copy()
    weekly_data = (
        data.resample("W-MON", label="left", closed="left")
        .agg({"open": "first", "high": "max", "low": "min", "close": "last"})
        .dropna()
    )
    weekly_data.rename(
        columns={
            "open": "weekly_open",
            "high": "weekly_high",
            "low": "weekly_low",
            "close": "weekly_close",
        },
        inplace=True,
    )

    weekly_data["lwv"] = lv(
        weekly_data["weekly_high"],
        weekly_data["weekly_low"],
        weekly_data["weekly_close"],
        lookback=4,
    )

    data = data.join(weekly_data, how="left", rsuffix="_weekly")

    return data
