import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import pytz

from datetime import datetime
from io import BytesIO

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(page_title="Stock Analysis Suite V2", page_icon="📈", layout="wide")

# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
<style>

.main {
    background-color: #0E1117;
}

.block-container {
    padding-top: 1rem;
}

.metric-card {
    background-color: #1C2333;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stMetric"] {
    background-color: #1C2333;
    border: 1px solid #2F3B52;
    padding: 15px;
    border-radius: 12px;
}

</style>
""",
    unsafe_allow_html=True,
)

# ==========================================================
# HEADER
# ==========================================================

st.title("🚀 Stock Analysis Suite V2")

st.markdown("India + USA Stocks | SMA10 Scanner | Bullish / Neutral / Bearish")

# ==========================================================
# TIME SECTION
# ==========================================================

india_tz = pytz.timezone("Asia/Kolkata")
usa_tz = pytz.timezone("America/New_York")

india_time = datetime.now(india_tz)
usa_time = datetime.now(usa_tz)

c1, c2 = st.columns(2)

with c1:
    st.info(f"🇮🇳 IST Time : " f"{india_time.strftime('%d-%b-%Y %I:%M:%S %p')}")

with c2:
    st.info(f"🇺🇸 New York Time : " f"{usa_time.strftime('%d-%b-%Y %I:%M:%S %p')}")

# ==========================================================
# INDIAN STOCKS
# ==========================================================

INDIAN_STOCKS = {
    "M&M": "M&M",
    "Hero Motocorp": "HEROMOTOCO",
    "KPIT Technology": "KPITTECH",
    "LTM": "LTIM",
    "Mphasis": "MPHASIS",
    "Maruti": "MARUTI",
    "DLF": "DLF",
    "Dixon": "DIXON",
    "SHRIRAM Finance": "SHRIRAMFIN",
    "Indigo": "INDIGO",
    "Eicher Motors": "EICHERMOT",
    "Bajaj Auto": "BAJAJ-AUTO",
    "VEDL": "VEDL",
    "HAL": "HAL",
    "JSW Steel": "JSWSTEEL",
    "LT": "LT",
    "SBIN": "SBIN",
    "Persistent Systems": "PERSISTENT",
    "Tata Steel": "TATASTEEL",
    "BHEL": "BHEL",
    "ABB": "ABB",
    "Siemens": "SIEMENS",
    "NTPC": "NTPC",
    "National Aluminium": "NATIONALUM",
    "Kaynes": "KAYNES",
    "MCX": "MCX",
    "BSE": "BSE",
    "Trent": "TRENT",
    "Asian Paints": "ASIANPAINT",
    "OFSS": "OFSS",
    "Hindalco": "HINDALCO",
    # New
    "Cummins India": "CUMMINSIND",
    "TCS": "TCS",
    "Infosys": "INFY",
    "Tata Elxsi": "TATAELXSI",
    "Bajaj Finance": "BAJFINANCE",
    "Polycab": "POLYCAB",
    "ICICI Bank": "ICICIBANK",
    "Lupin": "LUPIN",
    "Laurus Labs": "LAURUSLABS",
    "NIFTY 50": "^NSEI",
}

# ==========================================================
# USA STOCKS
# ==========================================================

USA_STOCKS = {
    "MU": "MU",
    "GOOGL": "GOOGL",
    "NVDA": "NVDA",
    "AVGO": "AVGO",
    "CAT": "CAT",
    "AMAT": "AMAT",
    "AMZN": "AMZN",
    "WMT": "WMT",
    "AMD": "AMD",
    "GS": "GS",
    "MSFT": "MSFT",
    "BA": "BA",
    "AAPL": "AAPL",
    "LRCX": "LRCX",
    "JPM": "JPM",
    "META": "META",
    "COST": "COST",
    "HD": "HD",
    "PG": "PG",
    "TSLA": "TSLA",
    "LLY": "LLY",
    "JNJ": "JNJ",
}

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.header("⚙️ Controls")

    option = st.selectbox("Select Date Option", ["Today", "Yesterday", "Custom Date"])

    custom_date = None

    if option == "Custom Date":

        custom_date = st.date_input("Choose Date", format="DD/MM/YYYY")

    st.markdown("---")

    st.subheader("🎯 Scanner Settings")

    sma_threshold = st.slider(
        "SMA10 Distance %", min_value=0.5, max_value=5.0, value=2.0, step=0.5
    )

    run_analysis = st.button("🚀 Run Analysis", use_container_width=True)
# ==========================================================
# KPI PLACEHOLDERS
# ==========================================================

k1, k2, k3, k4, k5, k6 = st.columns(6)

# ==========================================================
# TABS
# ==========================================================

tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
    [
        "🇮🇳 Indian Stocks",
        "🎯 SMA10 Scanner",
        "📈 EMA10 Above",
        "📉 EMA10 Below",
        "🇺🇸 USA Stocks",
        "🔥 Strong Bullish",
        "➖ Neutral",
        "⚠️ Bearish",
    ]
)

# ==========================================================
# RESULT CONTAINERS
# ==========================================================

indian_results = []
usa_results = []

sma_results = []

ema_above_results = []

ema_below_results = []

bullish_results = []
neutral_results = []
bearish_results = []

# ==========================================================
# EXCEL EXPORT
# ==========================================================


def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        df.to_excel(writer, index=False)

    return output.getvalue()


# ==========================================================
# ANALYSIS ENGINE
# ==========================================================


@st.cache_data(ttl=900)
def analyze_stock(stock_name, symbol, market, option, custom_date):

    try:

        # ==========================================
        # TICKER
        # ==========================================

        if market == "INDIA":
            if symbol.startswith("^"):
                ticker = symbol
            else:
                ticker = symbol + ".NS"

        # ==========================================
        # DOWNLOAD DATA
        # ==========================================

        data = yf.download(ticker, period="6mo", interval="1d", progress=False)

        if data.empty:
            return None

        # ==========================================
        # FLATTEN COLUMNS
        # ==========================================

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        if "Close" not in data.columns:
            return None

        data = data.dropna(subset=["Close"])

        if len(data) < 50:
            return None

        # ==========================================
        # SMA
        # ==========================================

        data["SMA10"] = data["Close"].rolling(10).mean()

        data["SMA20"] = data["Close"].rolling(20).mean()

        data["SMA50"] = data["Close"].rolling(50).mean()

        # ==========================================
        # EMA
        # ==========================================

        data["EMA10"] = data["Close"].ewm(span=10, adjust=False).mean()

        # ==========================================
        # RSI
        # ==========================================

        delta = data["Close"].diff()

        gain = delta.clip(lower=0)

        loss = -delta.clip(upper=0)

        avg_gain = gain.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()

        avg_loss = loss.ewm(alpha=1 / 14, min_periods=14, adjust=False).mean()

        rs = avg_gain / avg_loss

        data["RSI"] = 100 - (100 / (1 + rs))

        # ==========================================
        # 20 DAY HIGH LOW
        # ==========================================

        data["20D_High"] = data["High"].rolling(20).max().shift(1)

        data["20D_Low"] = data["Low"].rolling(20).min().shift(1)

        # ==========================================
        # DATE SELECTION
        # ==========================================

        if option == "Today":

            latest = data.iloc[-1]

        elif option == "Yesterday":

            if len(data) < 2:
                return None

            latest = data.iloc[-2]

        elif option == "Custom Date":

            data["Date"] = data.index.date

            filtered = data[data["Date"] <= custom_date]

            if filtered.empty:
                return None

            latest = filtered.iloc[-1]

        else:
            return None

        # ==========================================
        # VALUES
        # ==========================================

        close_price = float(latest["Close"])

        sma10 = float(latest["SMA10"])

        sma20 = float(latest["SMA20"])

        sma50 = float(latest["SMA50"])

        ema10 = float(latest["EMA10"])

        rsi = float(latest["RSI"])

        high20 = float(latest["20D_High"])

        low20 = float(latest["20D_Low"])

        if any(pd.isna([close_price, sma10, sma20, sma50, rsi, high20, low20])):
            return None

        # ==========================================
        # ORIGINAL CONDITIONS
        # ==========================================

        cond1 = 1 if close_price > sma10 else -1

        cond2 = 1 if sma10 > sma20 else -1

        cond3 = 1 if sma20 > sma50 else -1

        # RSI

        if rsi > 55:
            cond4 = 1

        elif rsi < 45:
            cond4 = -1

        else:
            cond4 = 0

        # BREAKOUT

        if close_price >= high20:

            cond5 = 1

        elif close_price < low20:

            cond5 = -1

        else:

            cond5 = 0

        # ==========================================
        # TOTAL SCORE
        # ==========================================

        total_score = cond1 + cond2 + cond3 + cond4 + cond5

        # ==========================================
        # SIGNAL
        # ==========================================

        if total_score >= 4:

            signal = "🔥 Strong Bullish"

        elif total_score >= 2:

            signal = "✅ Bullish"

        elif total_score <= -4:

            signal = "❌ Strong Bearish"

        elif total_score <= -2:

            signal = "⚠️ Bearish"

        else:

            signal = "➖ Neutral"

        # ==========================================
        # SMA10 DISTANCE
        # ==========================================

        distance = (abs(close_price - sma10) / sma10) * 100

        ema_distance = (abs(close_price - ema10) / ema10) * 100

        side = "Above SMA10" if close_price > sma10 else "Below SMA10"

        # ==========================================
        # RETURN
        # ==========================================

        return {
            "Stock": stock_name,
            "Market": market,
            "Date": str(latest.name.date()),
            "Close": round(close_price, 2),
            "SMA10": round(sma10, 2),
            "SMA20": round(sma20, 2),
            "SMA50": round(sma50, 2),
            "EMA10": round(ema10, 2),
            "EMA Distance %": round(ema_distance, 2),
            "RSI": round(rsi, 2),
            "Distance %": round(distance, 2),
            "Side": side,
            "Score": total_score,
            "Signal": signal,
        }

    except Exception:

        return None


# ==========================================================
# RUN ANALYSIS
# ==========================================================

if run_analysis:

    progress_bar = st.progress(0)

    total_stocks = len(INDIAN_STOCKS) + len(USA_STOCKS)

    counter = 0

    # ======================================================
    # INDIA
    # ======================================================

    for stock_name, symbol in INDIAN_STOCKS.items():

        result = analyze_stock(stock_name, symbol, "INDIA", option, custom_date)

        counter += 1

        progress_bar.progress(counter / total_stocks)

        if result is None:
            continue

        indian_results.append(result)

        # ==========================================
        # SMA10 SCANNER
        # ==========================================

        if result["Distance %"] <= sma_threshold:

            sma_results.append(result)

        # ==========================================
        # EMA SCANNER
        # ==========================================

        if result["Close"] > result["EMA10"]:

            ema_above_results.append(result)

        else:

            ema_below_results.append(result)

        # SMA10

        if result["Distance %"] <= sma_threshold:

            sma_results.append(result)

        # EMA

        if result["Close"] > result["EMA10"]:

            ema_above_results.append(result)

        else:

            ema_below_results.append(result)

        # ==========================================
        # SIGNAL BUCKETS
        # ==========================================

        if result["Signal"] in ["🔥 Strong Bullish", "✅ Bullish"]:

            bullish_results.append(result)

        elif result["Signal"] == "➖ Neutral":

            neutral_results.append(result)

        elif result["Signal"] in ["⚠️ Bearish", "❌ Strong Bearish"]:

            bearish_results.append(result)

    # ======================================================
    # USA
    # ======================================================

    for stock_name, symbol in USA_STOCKS.items():

        result = analyze_stock(stock_name, symbol, "USA", option, custom_date)

        counter += 1

        progress_bar.progress(counter / total_stocks)

        if result is None:
            continue

        usa_results.append(result)

        # ==========================================
        # SMA10 SCANNER
        # ==========================================

        if result["Distance %"] <= 2:

            sma_results.append(result)

            # ==========================================
        # EMA SCANNER
        # ==========================================

        if result["Close"] > result["EMA10"]:

            ema_above_results.append(result)

        else:

            ema_below_results.append(result)

        # ==========================================
        # SIGNAL BUCKETS
        # ==========================================

        if result["Signal"] in ["🔥 Strong Bullish", "✅ Bullish"]:

            bullish_results.append(result)

        elif result["Signal"] == "➖ Neutral":

            neutral_results.append(result)

        elif result["Signal"] in ["⚠️ Bearish", "❌ Strong Bearish"]:

            bearish_results.append(result)

    # ======================================================
    # DATAFRAMES
    # ======================================================

    indian_df = pd.DataFrame(indian_results)

    usa_df = pd.DataFrame(usa_results)

    sma_df = pd.DataFrame(sma_results)

    ema_above_df = pd.DataFrame(ema_above_results)

    ema_below_df = pd.DataFrame(ema_below_results)

    bullish_df = pd.DataFrame(bullish_results)

    neutral_df = pd.DataFrame(neutral_results)

    bearish_df = pd.DataFrame(bearish_results)

    # ======================================================
    # KPI CARDS
    # ======================================================

    with k1:

        st.metric("🇮🇳 India", len(indian_df))

    with k2:

        st.metric("🇺🇸 USA", len(usa_df))

    with k3:

        st.metric("🎯 SMA10", len(sma_df))

    with k4:

        st.metric("🔥 Bullish", len(bullish_df))

    with k5:

        st.metric("➖ Neutral", len(neutral_df))

    with k6:

        st.metric("⚠️ Bearish", len(bearish_df))

    # ==========================================================
    # SORT DATAFRAMES
    # ==========================================================

    if not indian_df.empty:

        indian_df = indian_df.sort_values(by="Score", ascending=False)

    if not usa_df.empty:

        usa_df = usa_df.sort_values(by="Score", ascending=False)

    if not sma_df.empty:

        sma_df = sma_df.sort_values(by="Distance %", ascending=True)

    if not bullish_df.empty:

        bullish_df = bullish_df.sort_values(by="Score", ascending=False)

    if not neutral_df.empty:

        neutral_df = neutral_df.sort_values(by="Score", ascending=False)

    if not bearish_df.empty:

        bearish_df = bearish_df.sort_values(by="Score", ascending=True)

    # ==========================================================
    # TAB 1 - INDIA
    # ==========================================================

    with tab1:

        st.subheader("🇮🇳 Indian Stocks Analysis")

        st.dataframe(indian_df, use_container_width=True, height=700)

    # ==========================================================
    # TAB 2 - SMA10
    # ==========================================================

    with tab2:

        st.subheader(f"🎯 Stocks Within {sma_threshold}% Of SMA10")

        if sma_df.empty:

            st.warning("No Stocks Found Near SMA10")

        else:

            st.dataframe(sma_df, use_container_width=True, height=700)

        # ==========================================================
    # TAB 3 - EMA ABOVE
    # ==========================================================

    with tab3:

        st.subheader("📈 Stocks Above EMA10")

        st.dataframe(ema_above_df, use_container_width=True)

    # ==========================================================
    # TAB 4 - EMA BELOW
    # ==========================================================

    with tab4:

        st.subheader("📉 Stocks Below EMA10")

        st.dataframe(ema_below_df, use_container_width=True)

    # ==========================================================
    # TAB 3 - USA
    # ==========================================================

    with tab5:

        st.subheader("🇺🇸 USA Stocks Analysis")

        st.dataframe(usa_df, use_container_width=True, height=700)

    # ==========================================================
    # TAB 4 - BULLISH
    # ==========================================================

    with tab6:

        st.subheader("🔥 Bullish Stocks")

        if bullish_df.empty:

            st.warning("No Bullish Stocks Found")

        else:

            st.dataframe(bullish_df, use_container_width=True, height=700)

    # ==========================================================
    # TAB 5 - NEUTRAL
    # ==========================================================

    with tab7:

        st.subheader("➖ Neutral Stocks")

        if neutral_df.empty:

            st.warning("No Neutral Stocks Found")

        else:

            st.dataframe(neutral_df, use_container_width=True, height=700)

    # ==========================================================
    # TAB 6 - BEARISH
    # ==========================================================

    with tab8:

        st.subheader("⚠️ Bearish Stocks")

        if bearish_df.empty:

            st.warning("No Bearish Stocks Found")

        else:

            st.dataframe(bearish_df, use_container_width=True, height=700)

    # ==========================================================
    # EXCEL DOWNLOADS
    # ==========================================================

    st.markdown("---")

    st.subheader("📥 Downloads")

    d1, d2, d3 = st.columns(3)

    with d1:

        if not indian_df.empty:

            st.download_button(
                label="📥 India Excel",
                data=create_excel(indian_df),
                file_name="india_stocks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    with d2:

        if not usa_df.empty:

            st.download_button(
                label="📥 USA Excel",
                data=create_excel(usa_df),
                file_name="usa_stocks.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    with d3:

        if not sma_df.empty:

            st.download_button(
                label="📥 SMA Scanner Excel",
                data=create_excel(sma_df),
                file_name="sma_scanner.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # ==========================================================
    # SUMMARY SECTION
    # ==========================================================

    st.markdown("---")

    st.subheader("📊 Analysis Summary")

    s1, s2, s3 = st.columns(3)

    with s1:

        st.success(f"🔥 Bullish Stocks : {len(bullish_df)}")

    with s2:

        st.info(f"➖ Neutral Stocks : {len(neutral_df)}")

    with s3:

        st.error(f"⚠️ Bearish Stocks : {len(bearish_df)}")

    # ==========================================================
    # TELEGRAM PLACEHOLDER
    # ==========================================================

    st.markdown("---")

    st.info("🔔 Telegram Alerts Module Coming Soon")

# ==========================================================
# END
# ==========================================================
