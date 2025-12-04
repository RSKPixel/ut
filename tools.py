import numpy as np
import pandas as pd


def ddt(df: pd.DataFrame) -> pd.DataFrame:
    # Daily Dow Theory (DDT) Indicator
    df = df.copy()
    n = len(df)
    df["dow_high"] = np.nan
    df["dow_low"] = np.nan
    df["dow_points"] = np.nan
    df["direction"] = np.nan
    current_high = -np.inf
    current_low = np.inf

    for d in range(1, n):
        current_high = (
            df.iloc[d - 1]["swing_point"]
            if df.iloc[d]["swing"] == "high"
            else current_high
        )
        current_low = (
            df.iloc[d - 1]["swing_point"]
            if df.iloc[d]["swing"] == "low"
            else current_low
        )
        low = df.iloc[d - 1]["low"]
        high = df.iloc[d - 1]["high"]

        if np.isnan(current_high) and np.isnan(current_low):
            continue

        if current_high > high:
            df.at[df.index[d], "dow_high"] = current_high
            df.at[df.index[d], "dow_points"] = current_high
            df.at[df.index[d], "direction"] = -1
        elif current_low < low:
            df.at[df.index[d], "dow_low"] = current_low
            df.at[df.index[d], "dow_points"] = current_low
            df.at[df.index[d], "direction"] = 1

    return df


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
