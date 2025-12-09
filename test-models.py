import pandas as pd
from ssc import SwingPoints2
import streamlit as st
from config import eod, get_symbols
from streamlit_bokeh import streamlit_bokeh
from datetime import datetime, timedelta
from tools import asc, lv, weekly_rdata, ddt2
from models import kbd1
from backtest import backtest_kbd1
from bokeh_chart import plot_tv_ohlc_bokeh
from models.kebf import signal as butterfly_signal


def main():
    st.set_page_config(page_title="KBD1 - Testing Model", layout="wide")
    col1, col2 = st.columns(2)

    with col2:
        timeframe = st.selectbox("Select Timeframe", ["tfw_eod", "tfw_idata_15m"])

    with col1:
        symbol = st.selectbox(
            "Select Symbol",
            get_symbols(table=timeframe),
            index=0,
        )

    df_ohlc = eod(symbol, "2024-06-01", "2025-12-31", table=timeframe)
    # df_ohlc = pd.read_csv(f"data/{symbol.lower()}-ohlc-data.csv")
    df = ut(df_ohlc)
    df.to_csv(f"data/{symbol.lower()}-ohlc-data.csv")
    signals = []
    for d in range(1, len(df)):
        s = kbd1.signal(df.iloc[:d])
        if s.iloc[0]["signal"] is not None:
            signals.append(s)

    signal_df = pd.DataFrame()
    signal_df = pd.concat(signals)
    signal_df.reset_index(drop=True, inplace=True)
    signal_df.sort_values(by="setup_candle", inplace=True, ascending=False)
    signal_df = signal_df.round(2)
    signal_df = signal_df[
        signal_df["setup_candle"].dt.date == signal_df["setup_candle"].dt.date.max()
    ]
    st.write(signal_df)

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

    # for d in range(1, len(df)):
    #     bf_df = butterfly_signal(df.iloc[:d])
    return df


def ut(df_ohlc: pd.DataFrame) -> pd.DataFrame:
    df_ohlc["date"] = pd.to_datetime(df_ohlc["date"])
    df_ohlc.set_index("date", inplace=True)
    df = df_ohlc.copy()

    # Populating trader's framework data
    df = SwingPoints2(df)
    df["asc"] = asc(df["close"], lookback=20)
    df["mvf"] = (df["asc"] - df["low"]) / df["asc"] * 100
    df["ldv"] = lv(df["high"], df["low"], df["close"], lookback=4)
    df = weekly_rdata(df)
    df = ddt2(df)
    df.drop(columns=["asc"], inplace=True)

    return df


if __name__ == "__main__":
    main()
