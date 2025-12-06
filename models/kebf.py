import numpy as np
import pandas as pd


def signal(df: pd.DataFrame):

    df = df.copy()
    if df.iloc[-1]["swing"] not in ["high", "low"]:
        return
    df = df[df["swing_point"].notna()].tail(6)

    if len(df) < 6:
        return

    # Reverse so index 0 = MOST RECENT swing
    swing_points = df["swing_point"][::-1].to_list()
    swings = df["swing"][::-1].to_list()
    swing_dates = df.index[::-1].to_list()

    buy_pattern = swings == ["low", "high", "low", "high", "low", "high"]
    sell_pattern = swings == ["high", "low", "high", "low", "high", "low"]

    # 0 = latest, 5 = oldest

    bf_buy = buy_pattern and (
        swing_points[0] < swing_points[2]
        and swing_points[0] < swing_points[4]
        and swing_points[1] < swing_points[3]
        and swing_points[2] > swing_points[4]
        and swing_points[3] < swing_points[5]
    )

    bf_sell = sell_pattern and (
        swing_points[0] > swing_points[2]
        and swing_points[0] > swing_points[4]
        and swing_points[1] > swing_points[3]
        and swing_points[2] < swing_points[4]
        and swing_points[3] > swing_points[5]
    )

    if bf_buy or bf_sell:
        print(
            "Trigger swing (latest):",
            swing_dates[0],
            "Points:",
            swing_points,
            "BUY:",
            bf_buy,
            "SELL:",
            bf_sell,
        )
        # print(swing_points)
