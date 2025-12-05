import pandas as pd
from ssc import SwingPoints2
import streamlit as st
from config import eod
from streamlit_bokeh import streamlit_bokeh
from datetime import datetime, timedelta
from tools import asc, lv, weekly_rdata, ddt2
from models import kbd1


def main():
    st.set_page_config(page_title="SSC Data Viewer", layout="wide")
    symbol = "NIFTY"
    symbol = st.selectbox(
        "Select Symbol",
        ["CRUDEOIL", "GOLD", "SILVER", "NATURALGAS", "NIFTY", "BANKNIFTY"],
        index=0,
    )

    df_ohlc = eod(symbol, "2020-06-01", "2025-12-31")
    # df_ohlc = pd.read_csv(f"data/{symbol.lower()}-ohlc-data.csv")
    df = ut(df_ohlc)
    df.to_csv(f"data/{symbol.lower()}-ohlc-data.csv")

    signals = kbd1.signal(df, setup="buy")
    st.write(signals)
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
