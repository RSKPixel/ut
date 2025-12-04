import pandas as pd
import numpy as np
from ssc import SwingPoints2
import streamlit as st
from config import eod
from bokeh_chart import plot_tv_ohlc_bokeh
from streamlit_bokeh import streamlit_bokeh
from datetime import datetime, timedelta
from tools import asc, lv, weekly_rdata, ddt


def main():
    st.set_page_config(page_title="SSC Data Viewer", layout="wide")
    symbol = "NIFTY"
    symbol = st.selectbox(
        "Select Symbol",
        ["CRUDEOIL", "GOLD", "SILVER", "NATURALGAS", "NIFTY", "BANKNIFTY"],
        index=0,
    )
    # df_ohlc = eod(symbol, "2020-01-01", "2025-11-29")
    df_ohlc = pd.read_csv(f"data/{symbol.lower()}-ohlc-data.csv")
    df_ohlc["date"] = pd.to_datetime(df_ohlc["date"])
    df_ohlc.set_index("date", inplace=True)
    df = df_ohlc.copy()
    df.to_csv(f"data/{symbol.lower()}-ohlc-data.csv")
    df = SwingPoints2(df)

    # Identify duplicate swings
    s = df.loc[df["swing"].isin(["high", "low"]), "swing"]
    dup = s.eq(s.shift(1))
    df["duplicate_swings"] = False
    df.loc[dup.index, "duplicate_swings"] = dup

    df["asc"] = asc(df["close"], lookback=20)
    df["mvf"] = (df["asc"] - df["low"]) / df["asc"] * 100
    df.drop(columns=["asc"], inplace=True)
    df["ldv"] = lv(df["high"], df["low"], df["close"], lookback=4)

    df = weekly_rdata(df)
    df = df[df.index >= df.index.max() - timedelta(days=180)]
    df = ddt(df)

    # df = ddt(df)
    df["x"] = range(len(df))
    fig_bokeh = plot_tv_ohlc_bokeh(
        df,
        swing=True,
        debugging=True,
        compare=False,
        dt=True,
        title="SSC Chart - Bokeh",
    )

    streamlit_bokeh(
        fig_bokeh, use_container_width=True, theme="streamlit", key="my_unique_key"
    )

    st.title("SSC Data Viewer")
    st.dataframe(
        df[
            [
                "open",
                "high",
                "low",
                "close",
                "bar_type",
                "swing_point",
                "swing",
                "dow_point",
                "direction",
                "mvf",
                "ldv",
                "lwv",
                "weekly_open",
                "weekly_high",
                "weekly_low",
                "weekly_close",
            ]
        ]
    )


if __name__ == "__main__":
    main()
