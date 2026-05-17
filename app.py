import streamlit as st
import yfinance as yf
import pandas as pd
import time
from datetime import datetime

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    layout="wide"
)

st.title("📈 Stock Analysis Dashboard")

# =========================
# STOCKS
# =========================
stocks = {
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
    "Hindalco": "HINDALCO"
}

# =========================
# USER INPUT
# =========================
option = st.selectbox(
    "Select Date Option",
    ["Today", "Yesterday", "Custom Date"]
)

custom_date = None

if option == "Custom Date":
    custom_date = st.date_input("Choose Date")

# =========================
# RUN BUTTON
# =========================
if st.button("Run Analysis"):

    progress = st.progress(0)
    status = st.empty()

    results = []

    total_stocks = len(stocks)
    count = 0

    for name, base in stocks.items():

        try:
            count += 1

            status.text(f"Processing {name}...")

            symbol = base + ".NS"

            # =========================
            # DOWNLOAD DAILY DATA
            # =========================
            data = yf.download(
                symbol,
                period="6mo",
                interval="1d",
                progress=False
            )

            if data.empty:
                continue

            # Flatten columns if needed
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.get_level_values(0)

            if "Close" not in data.columns:
                continue

            data = data.dropna(subset=["Close"])

            if len(data) < 50:
                continue

            # =========================
            # INDICATORS
            # =========================
            data["SMA_10"] = data["Close"].rolling(10).mean()
            data["SMA_20"] = data["Close"].rolling(20).mean()
            data["SMA_50"] = data["Close"].rolling(50).mean()

            # RSI
            delta = data["Close"].diff()

            gain = delta.clip(lower=0)
            loss = -delta.clip(upper=0)

            avg_gain = gain.ewm(
                alpha=1/14,
                min_periods=14,
                adjust=False
            ).mean()

            avg_loss = loss.ewm(
                alpha=1/14,
                min_periods=14,
                adjust=False
            ).mean()

            rs = avg_gain / avg_loss

            data["RSI"] = 100 - (100 / (1 + rs))

            # 20 Day High Low
            data["20D_High"] = data["High"].rolling(20).max().shift(1)
            data["20D_Low"] = data["Low"].rolling(20).min().shift(1)

            # =========================
            # DATE SELECTION
            # =========================
            now = datetime.now()
            today = now.date()

            last_date = data.index[-1].date()

            if option == "Today":

                latest = data.iloc[-1]

            elif option == "Yesterday":

                latest = data.iloc[-2]

            elif option == "Custom Date":

                data["Date"] = data.index.date

                filtered = data[data["Date"] <= custom_date]

                if filtered.empty:
                    continue

                latest = filtered.iloc[-1]

            else:
                continue

            # =========================
            # VALUES
            # =========================
            close_price = latest["Close"]
            sma10 = latest["SMA_10"]
            sma20 = latest["SMA_20"]
            sma50 = latest["SMA_50"]
            rsi = latest["RSI"]
            high20 = latest["20D_High"]
            low20 = latest["20D_Low"]

            if any(pd.isna([
                close_price,
                sma10,
                sma20,
                sma50,
                rsi,
                high20,
                low20
            ])):
                continue

            # =========================
            # CONDITIONS
            # =========================
            cond1 = 1 if close_price > sma10 else -1
            cond2 = 1 if sma10 > sma20 else -1
            cond3 = 1 if sma20 > sma50 else -1

            if rsi > 55:
                cond4 = 1
            elif rsi < 45:
                cond4 = -1
            else:
                cond4 = 0

            if close_price >= high20:
                cond5 = 1
            elif close_price < low20:
                cond5 = -1
            else:
                cond5 = 0

            total_score = (
                cond1 +
                cond2 +
                cond3 +
                cond4 +
                cond5
            )

            # =========================
            # SIGNAL
            # =========================
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

            # =========================
            # RESULTS
            # =========================
            results.append({
                "Stock": name,
                "Date": str(latest.name.date()),
                "Close": round(close_price, 2),
                "RSI": round(rsi, 2),
                "Score": total_score,
                "Signal": signal
            })

            progress.progress(count / total_stocks)

            time.sleep(0.1)

        except Exception as e:
            st.error(f"{name} Error: {e}")

    # =========================
    # DISPLAY RESULTS
    # =========================
    if results:

        df = pd.DataFrame(results)

        df = df.sort_values(
            by="Score",
            ascending=False
        )

        st.success("Analysis Completed")

        st.dataframe(
            df,
            use_container_width=True
        )

        # =========================
        # DOWNLOAD EXCEL
        # =========================
        excel_file = "stock_analysis.xlsx"

        df.to_excel(excel_file, index=False)

        with open(excel_file, "rb") as file:
            st.download_button(
                label="📥 Download Excel",
                data=file,
                file_name=excel_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:
        st.warning("No Data Generated")