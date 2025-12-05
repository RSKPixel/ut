import pandas as pd
import numpy as np


def signal(df: pd.DataFrame, setup: str = "buy"):
    # KBD1 - Key Breakout Day 1 - Trading Model
    # Author: Brent Penfold
    df = df.copy()
    signal = {
        "setup_candle": None,
        "entry_candle": None,
        "entry_day_sl": None,
        "tailing_sl": None,
        "target": False,
    }

    dow_trend_signals = df[df["intersection"].notna()][["intersection", "direction"]][
        -2:
    ]

    print(dow_trend_signals)

    return pd.DataFrame([signal])
