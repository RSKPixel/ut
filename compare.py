import pandas as pd
from ssc import SwingPoints2
import streamlit as st
from bokeh_chart import plot_tv_ohlc_bokeh
from streamlit_bokeh import streamlit_bokeh


def compare_main():
    st.set_page_config(page_title="SSC Data Viewer - Compare", layout="wide")
    # df = pd.read_csv("data/penfold-dataset.csv")
    # df = pd.read_csv("data/penfold-dataset-lh.csv")
    df = pd.read_csv("data/crudeoil-ohlc-data.csv")
    # no_of_months = st.slider("Select number of months", 1, 100, 1)
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df.set_index("date", inplace=True)
    print(df[["low", "high"]].head())
    df = df.round(4)
    df_ssc = SwingPoints2(df)

    df_ssc["x"] = range(len(df_ssc))
    # df_ssc["error"] = df_ssc["swing_point"] != df_ssc["swing_point_penfold"]
    # df_ssc["error"] = (
    #     ~df_ssc["swing_point"].fillna("X").eq(df_ssc["swing_point_penfold"].fillna("X"))
    # )

    # df_ssc["error_bartype"] = (
    #     ~df_ssc["bar_type"].fillna("X").eq(df_ssc["bar_type_penfold"].fillna("X"))
    # )
    fig_bokeh = plot_tv_ohlc_bokeh(
        df_ssc,
        title="SSC Chart - Bokeh",
        compare=False,
        debugging=True,
    )
    # st.write(
    #     f"Errors count {len(df_ssc[df_ssc['error']])} out of {len(df_ssc)} which is {len(df_ssc[df_ssc['error']]) / len(df_ssc) * 100:.2f}%"
    # )
    streamlit_bokeh(
        fig_bokeh, use_container_width=True, theme="streamlit", key="my_unique_key"
    )

    st.dataframe(
        df_ssc[
            [
                "open",
                "high",
                "low",
                "close",
                "bar_type",
                # "bar_type_penfold",
                # "bar_type_1",
                # "swing_point_penfold",
                "swing_point",
                "swing",
                # "swing_penfold",
                # "error",
                # "error_bartype",
            ]
        ]
    )


if __name__ == "__main__":
    compare_main()
