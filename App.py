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
    
    # Align and Calculate
    cpi = cpi.loc[start:end]
    data = djia.join(cpi, how='left').ffill().dropna()
    data['DJIA_Indexed'] = (data['DJIA'] / data['DJIA'].iloc[0]) * 100
    data['CPI_Indexed'] = (data['CPI'] / data['CPI'].iloc[0]) * 100
    data['Real_Value'] = (data['DJIA_Indexed'] / data['CPI_Indexed']) * 100
    return data

# 4. Main App Execution
try:
    data = get_data(start_date, end_date)

    # Visualization
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['DJIA_Indexed'], name="Dow Jones (Nominal)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['CPI_Indexed'], name="CPI (Inflation)"))
    fig.add_trace(go.Scatter(x=data.index, y=data['Real_Value'], name="DJIA (Inflation Adjusted)", line=dict(dash='dash')))
    fig.update_layout(title="Nominal vs. Real Returns (Base 100)", xaxis_title="Date", yaxis_title="Indexed Value")
    st.plotly_chart(fig, use_container_width=True)

    # KPIs
    st.header("🔍 Macro-Analytic Summary")
    total_return = ((data['DJIA_Indexed'].iloc[-1] / 100) - 1) * 100
    real_return = ((data['Real_Value'].iloc[-1] / 100) - 1) * 100
    erosion = total_return - real_return
    corr = data['DJIA_Indexed'].corr(data['CPI_Indexed'])

    col1, col2, col3 = st.columns(3)
    col1.metric("Nominal ROI", f"{total_return:.1f}%")
    col2.metric("Real ROI", f"{real_return:.1f}%", delta=f"{-erosion:.1f}%", delta_color="inverse")
    col3.metric("Correlation Factor", f"{corr:.2f}")

    # Automated Commentary
    st.subheader("🤖 Automated Market Commentary")
    with st.expander("Click to view detailed AI Analysis", expanded=True):
        sentiment = "High correlation" if corr > 0.7 else "Moderate correlation" if corr > 0.3 else "Low correlation"
        summary_text = (
            f"**Executive Summary:** Since {start_date.year}, the Dow Jones grew **{total_return:.1f}%**. "
            f"Adjusted for inflation, purchasing power grew **{real_return:.1f}%**. \n\n"
            f"**Portfolio Impact:** {sentiment}. To maintain real wealth, an investor needed to beat an inflation hurdle of **{erosion:.1f}%**."
        )
        st.markdown(summary_text)

except Exception as e:
    st.error(f"Data error: {e}")

# 5. Sidebar "About" (Placed outside the try/except block properly)
st.sidebar.markdown("---")
st.sidebar.subheader("About")
st.sidebar.info("This Augmented Analytics tool merges live equity data with macro fundamentals to reveal real purchasing power trends.")
st.sidebar.info("This tool demonstrates Augmented Analytics by merging live equity data with macro fundamentals to reveal real purchasing power trends.")

except Exception as e:
    st.error(f"An error occurred: {e}")
