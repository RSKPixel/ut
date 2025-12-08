from urllib.parse import quote_plus
import pandas as pd
import sqlalchemy


def get_sqlalchemy_engine():
    try:
        host = "trialnerror.in"
        database = "tfw"
        user = "sysadmin"
        password = quote_plus("Apple@1239")

        conn_string = f"postgresql+psycopg2://{user}:{password}@{host}:5432/{database}"
        engine = sqlalchemy.create_engine(conn_string)

        with engine.connect() as connection:
            pass  # Test connection

    except Exception as e:
        print(f"Error connecting to database: {e}")
    return engine


def get_symbols(table: str = "tfw_eod") -> list:
    engine = get_sqlalchemy_engine()
    query = f"SELECT DISTINCT symbol FROM {table} ORDER BY symbol ASC;"
    df = pd.read_sql(query, engine)
    symbols = df["symbol"].tolist()
    return symbols


def eod(
    symbol: str,
    from_date: str,
    to_date: str,
    table: str = "tfw_eod",
) -> pd.DataFrame:

    engine = get_sqlalchemy_engine()
    query = f"""
        SELECT datetime AT TIME ZONE 'Asia/Kolkata' AS local_time, *
        FROM {table}
        WHERE symbol = %s AND datetime >= %s AND datetime <= %s
        ORDER BY datetime ASC;
    """
    df = pd.read_sql(query, engine, params=(symbol, from_date, to_date))

    df = df[["local_time", "open", "high", "low", "close", "volume"]]
    df.rename(columns={"local_time": "date"}, inplace=True)
    return df
