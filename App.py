import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# 1. Page Config
st.set_page_config(page_title="Macro-AI: DJIA vs Inflation", layout="wide")

st.title("📉 Augmented Analytics: DJIA vs. Inflation")
st.markdown("This app analyzes the **Dow Jones Industrial Average** against the **Consumer Price Index (CPI)** to determine real purchasing power.")

# 2. Sidebar for Inputs
st.sidebar.header("Analysis Settings")
start_date = st.sidebar.date_input("Start Date", datetime(2010, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now())

# 3. Data Fetching Logic
@st.cache_data
def get_data(start, end):
    # Fetch DJIA
    djia_raw = yf.download("^DJI", start=start, end=end)['Close']
    djia = pd.DataFrame(djia_raw)
    djia.columns = ['DJIA']
    
    # Fetch CPI
    cpi_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
    cpi = pd.read_csv(cpi_url)
    cpi.columns = ['Date', 'CPI']
    cpi['Date'] = pd.to_datetime(cpi['Date'])
    cpi.set_index('Date', inplace=True)
    
    # Filter CPI and Join
    cpi = cpi.loc[start:end]
    data = djia.join(cpi, how='left').ffill().dropna()
    
    # Analytics Calculations
    data['DJIA_Indexed'] = (data['DJIA'] / data['DJIA'].iloc[0]) * 100
    data['CPI_Indexed'] = (data['CPI'] / data['CPI'].iloc[0]) * 100
    data['Real_Value'] = (data['DJIA_Indexed'] / data['CPI_Indexed']) * 100
    return data

# 4. Main Execution Block
try:
    # Load Data
    data = get_data(start_date, end_date)

    # Charting
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['DJIA_Indexed'], name="Dow Jones (Nominal)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['CPI_Indexed'], name="CPI (Inflation)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Real_Value'], name="DJIA (Inflation Adjusted)", line=dict(dash='dash')))
    fig.update_layout(title="Nominal vs. Real Returns (Base 100)", xaxis_title="Date", yaxis_title="Indexed Value")
    st.plotly_chart(fig, use_container_width=True)

    # Metrics Section
    st.header("🔍 Macro-Analytic Summary")
    total_return = ((data['DJIA_Indexed'].iloc[-1] / 100) - 1) * 100
    real_return = ((data['Real_Value'].iloc[-1] / 100) - 1) * 100
    erosion = total_return - real_return
    corr = data['DJIA_Indexed'].corr(data['CPI_Indexed'])

    c1, c2, c3 = st.columns(3)
    c1.metric("Nominal ROI", f"{total_return:.1f}%")
    c2.metric("Real ROI", f"{real_return:.1f}%", delta=f"{-erosion:.1f}%", delta_color="inverse")
    c3.metric("Correlation", f"{corr:.2f}")

    # Insights Section
    st.subheader("🤖 Automated Market Commentary")
    sentiment = "High correlation" if corr > 0.7 else "Moderate correlation" if corr > 0.3 else "Low correlation"
    st.info(f"Since {start_date.year}, the Dow grew **{total_return:.1f}%**. After inflation, purchasing power grew **{real_return:.1f}%**. {sentiment} detected.")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")

# 5. Sidebar "About" (Enhanced Portfolio Description)
st.sidebar.markdown("---")
st.sidebar.subheader("📌 Project Intelligence")
st.sidebar.write("""
**Objective:** To quantify the 'Money Illusion' by comparing nominal stock market gains against real-world purchasing power using the Consumer Price Index (CPI).

**How it Works:** 1. **Live Sourcing:** Fetches real-time DJIA data from Yahoo Finance and monthly CPI data from the St. Louis FED (FRED).
2. **Indexing:** Normalizes both datasets to a 'Base 100' starting at your chosen date.
3. **Augmentation:** Calculates the **Real Return** by dividing the Nominal Index by the Inflation Index ($Real = \frac{Nominal}{CPI} \times 100$).
4. **AI Analysis:** Runs a Pearson Correlation coefficient to determine how much inflation is driving market movements.

**Why this matters:** Investors often see the Dow at all-time highs and assume wealth growth. This tool reveals if those gains are beating the rising cost of living.
""")
