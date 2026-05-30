import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Stock Analysis Suite",
    page_icon="📈",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.main {
    background-color: #0E1117;
}

h1,h2,h3 {
    color: #4DA6FF;
}

.metric-card {
    background-color: #1C2333;
    padding: 15px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# STOCK LISTS
# =====================================================

INDIAN_STOCKS = {

    # Existing
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
    "Laurus Labs": "LAURUSLABS"
}

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
    "JNJ": "JNJ"
}

# =====================================================
# HEADER
# =====================================================

st.title("🚀 Stock Analysis Suite")

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("⚙️ Controls")

    option = st.selectbox(
        "Date Option",
        ["Today", "Yesterday"]
    )

    run_analysis = st.button(
        "🚀 Run Analysis",
        use_container_width=True
    )

# =====================================================
# KPI PLACEHOLDERS
# =====================================================

k1, k2, k3, k4 = st.columns(4)

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🇮🇳 Indian Stocks",
        "🎯 SMA10 Scanner",
        "🇺🇸 USA Stocks",
        "🔥 Strong Bullish"
    ]
)

# =====================================================
# EXCEL EXPORT
# =====================================================

def create_excel(df):

    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(
            writer,
            index=False
        )

    return output.getvalue()

# =====================================================
# ANALYSIS ENGINE
# =====================================================

def analyze_stock(
        name,
        symbol,
        market
):

    try:

        if market == "INDIA":
            ticker = symbol + ".NS"
        else:
            ticker = symbol

        data = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False
        )

        if data.empty:
            return None

        if isinstance(
                data.columns,
                pd.MultiIndex
        ):
            data.columns = (
                data.columns.get_level_values(0)
            )

        data = data.dropna()

        if len(data) < 50:
            return None

        # ====================
        # SMA
        # ====================

        data["SMA10"] = (
            data["Close"]
            .rolling(10)
            .mean()
        )

        data["SMA20"] = (
            data["Close"]
            .rolling(20)
            .mean()
        )

        data["SMA50"] = (
            data["Close"]
            .rolling(50)
            .mean()
        )

        # ====================
        # RSI
        # ====================

        delta = data["Close"].diff()

        gain = delta.clip(
            lower=0
        )

        loss = -delta.clip(
            upper=0
        )

        avg_gain = gain.ewm(
            alpha=1/14,
            adjust=False
        ).mean()

        avg_loss = loss.ewm(
            alpha=1/14,
            adjust=False
        ).mean()

        rs = avg_gain / avg_loss

        data["RSI"] = (
            100 -
            (100 / (1 + rs))
        )

        # ====================
        # BREAKOUT
        # ====================

        data["20D_High"] = (
            data["High"]
            .rolling(20)
            .max()
            .shift(1)
        )

        latest = data.iloc[-1]

        close = float(latest["Close"])
        sma10 = float(latest["SMA10"])
        sma20 = float(latest["SMA20"])
        sma50 = float(latest["SMA50"])
        rsi = float(latest["RSI"])
        high20 = float(latest["20D_High"])

        # ====================
        # YOUR LOGIC
        # ====================

        cond1 = 1 if close > sma10 else -1
        cond2 = 1 if sma10 > sma20 else -1
        cond3 = 1 if sma20 > sma50 else -1

        if rsi > 55:
            cond4 = 1
        elif rsi < 45:
            cond4 = -1
        else:
            cond4 = 0

        cond5 = 1 if close >= high20 else 0

        score = (
            cond1 +
            cond2 +
            cond3 +
            cond4 +
            cond5
        )

        if score >= 4:
            signal = "🔥 Strong Bullish"
        elif score >= 2:
            signal = "✅ Bullish"
        elif score <= -4:
            signal = "❌ Strong Bearish"
        elif score <= -2:
            signal = "⚠️ Bearish"
        else:
            signal = "➖ Neutral"

        distance = (
            abs(close - sma10)
            / sma10
        ) * 100

        return {

            "Stock": name,
            "Market": market,
            "Close": round(close, 2),
            "RSI": round(rsi, 2),
            "Score": score,
            "Signal": signal,
            "SMA10": round(sma10, 2),
            "Distance %": round(distance, 2)

        }

    except:
        return None

# =====================================================
# RUN ANALYSIS
# =====================================================

if run_analysis:

    indian_results = []
    usa_results = []
    sma_results = []
    bullish_results = []

    progress = st.progress(0)

    all_stocks = (
        len(INDIAN_STOCKS)
        +
        len(USA_STOCKS)
    )

    counter = 0

    # INDIA

    for name, symbol in INDIAN_STOCKS.items():

        result = analyze_stock(
            name,
            symbol,
            "INDIA"
        )

        counter += 1

        progress.progress(
            counter / all_stocks
        )

        if result:

            indian_results.append(
                result
            )

            if result["Distance %"] <= 2:
                sma_results.append(
                    result
                )

            if result["Score"] >= 4:
                bullish_results.append(
                    result
                )

    # USA

    for name, symbol in USA_STOCKS.items():

        result = analyze_stock(
            name,
            symbol,
            "USA"
        )

        counter += 1

        progress.progress(
            counter / all_stocks
        )

        if result:

            usa_results.append(
                result
            )

            if result["Distance %"] <= 2:
                sma_results.append(
                    result
                )

            if result["Score"] >= 4:
                bullish_results.append(
                    result
                )

    indian_df = pd.DataFrame(indian_results)
    usa_df = pd.DataFrame(usa_results)
    sma_df = pd.DataFrame(sma_results)
    bullish_df = pd.DataFrame(
        bullish_results
    )

    # KPI

    k1.metric(
        "🇮🇳 Stocks",
        len(indian_df)
    )

    k2.metric(
        "🇺🇸 Stocks",
        len(usa_df)
    )

    k3.metric(
        "🎯 SMA10",
        len(sma_df)
    )

    k4.metric(
        "🔥 Bullish",
        len(bullish_df)
    )

    # TAB 1

    with tab1:

        st.subheader(
            "Indian Stocks"
        )

        st.dataframe(
            indian_df.sort_values(
                "Score",
                ascending=False
            ),
            use_container_width=True
        )

    # TAB 2

    with tab2:

        st.subheader(
            "SMA10 Scanner"
        )

        st.dataframe(
            sma_df.sort_values(
                "Distance %",
                ascending=True
            ),
            use_container_width=True
        )

    # TAB 3

    with tab3:

        st.subheader(
            "USA Stocks"
        )

        st.dataframe(
            usa_df.sort_values(
                "Score",
                ascending=False
            ),
            use_container_width=True
        )

    # TAB 4

    with tab4:

        st.subheader(
            "Strong Bullish"
        )

        st.dataframe(
            bullish_df.sort_values(
                "Score",
                ascending=False
            ),
            use_container_width=True
        )

    # DOWNLOAD

    st.markdown("---")

    excel_data = create_excel(
        pd.concat(
            [
                indian_df,
                usa_df
            ]
        )
    )

    st.download_button(
        label="📥 Download Excel",
        data=excel_data,
        file_name="stock_analysis.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    # FUTURE

    st.info(
        "🔔 Telegram Alerts - Coming Soon"
    )
