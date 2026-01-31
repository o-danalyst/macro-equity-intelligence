import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Page Config
st.set_page_config(page_title="Macro-AI: DJIA vs Inflation", layout="wide")

st.title("📉 Augmented Analytics: DJIA vs. Inflation")
st.markdown("This app analyzes the **Dow Jones Industrial Average** against the **Consumer Price Index (CPI)** to determine real purchasing power.")

# 1. Sidebar for Inputs
st.sidebar.header("Analysis Settings")
start_date = st.sidebar.date_input("Start Date", datetime(2010, 1, 1))
end_date = st.sidebar.date_input("End Date", datetime.now())

# 2. Data Fetching (Cached for speed)
@st.cache_data
def get_data(start, end):
    # Fetch DJIA from Yahoo Finance
    djia = yf.download("^DJI", start=start, end=end)['Close']
    
    # Fetch CPI directly from FRED CSV
    cpi_url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL"
    cpi = pd.read_csv(cpi_url, index_col='DATE', parse_dates=True)
    cpi = cpi.rename(columns={'CPIAUCSL': 'CPI'})
    
    # Filter CPI to match the user's selected date range
    cpi = cpi.loc[start:end]
    
    # Align dates
    data = pd.DataFrame({'DJIA': djia}).join(cpi).ffill().dropna()
    
    # Calculate Indexed Returns (Base 100)
    data['DJIA_Indexed'] = (data['DJIA'] / data['DJIA'].iloc[0]) * 100
    data['CPI_Indexed'] = (data['CPI'] / data['CPI'].iloc[0]) * 100
    
    # Augmented Logic: Inflation Adjusted Value
    data['Real_Value'] = (data['DJIA_Indexed'] / data['CPI_Indexed']) * 100
    return data

try:
    data = get_data(start_date, end_date)

    # 3. Visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['DJIA_Indexed'], name="Dow Jones (Nominal)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['CPI_Indexed'], name="CPI (Inflation)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Real_Value'], name="DJIA (Inflation Adjusted)", line=dict(dash='dash')))

    fig.update_layout(title="Nominal vs. Real Returns (Base 100)", xaxis_title="Date", yaxis_title="Indexed Value")
    st.plotly_chart(fig, use_container_width=True)

    # 4. Refined AI/Automated Insights Layer
    st.header("🔍 Macro-Analytic Summary")

    # Calculations for Insights
    total_return = ((data['DJIA_Indexed'].iloc[-1] / 100) - 1) * 100
    real_return = ((data['Real_Value'].iloc[-1] / 100) - 1) * 100
    erosion = total_return - real_return
    corr = data['DJIA_Indexed'].corr(data['CPI_Indexed'])

    # Display Key Performance Indicators
    col1, col2, col3 = st.columns(3)
    col1.metric("Nominal ROI", f"{total_return:.1f}%")
    col2.metric("Real ROI (Inflation Adj.)", f"{real_return:.1f}%", delta=f"{-erosion:.1f}%", delta_color="inverse")
    col3.metric("Correlation Factor", f"{corr:.2f}")

    # Professional Narrative Logic
    st.subheader("🤖 Automated Market Commentary")

    with st.expander("Click to view detailed AI Analysis", expanded=True):
        if corr > 0.7:
            sentiment = "High positive correlation detected. The Dow is currently scaling with monetary expansion/inflation."
        elif corr < 0.3:
            sentiment = "Low correlation. Market drivers are likely decoupled from CPI fluctuations (e.g., Tech-driven growth)."
        else:
            sentiment = "Moderate correlation. Market is sensitive but not entirely dictated by CPI trends."

        # We construct the string first to avoid syntax errors
        summary_text = (
            f"**Executive Summary:** Since the start of this period, the Dow Jones has grown by **{total_return:.1f}%**. "
            f"However, when accounting for the Consumer Price Index (CPI), the actual increase in purchasing power is only **{real_return:.1f}%**. \n\n"
            f"**Portfolio Impact:** {sentiment} \n"
            f"To maintain 'Real Wealth,' an investor during this period needed to outpace an inflation hurdle of **{erosion:.1f}%**. "
            "Any growth below this threshold represents a loss in real-world value despite nominal gains."
        )
        st.markdown(summary_text)

except Exception as e:
    st.error(f"An error occurred: {e}")
