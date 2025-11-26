import streamlit as st
import pandas as pd
import os
from datetime import timedelta
import plotly.express as px

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="Retail Shop Dashboard", layout="wide")

# -------------------------------
# LOAD AND PREPARE DATA
# -------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(__file__)             # ensures path resolves on hosts
    csv_path = os.path.join(BASE_DIR, "retail_shop_data.csv")
    df = pd.read_csv(csv_path)
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['PROFIT'] = df['SALES'] - (df['PURCHASES'] + df['UTILITIES'] + df['TRANSPORT'])
    df['REVENUE'] = df['SALES']
    return df

df = load_data()

# -------------------------------
# SIDEBAR CONTROLS
# -------------------------------
st.sidebar.title("DSMA Weekend Retail Shop Dashboard 🏪")
st.sidebar.header("⚙️ Settings")

min_date, max_date = df['DATE'].min(), df['DATE'].max()

start_date = st.sidebar.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
end_date = st.sidebar.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

chart_type = st.sidebar.selectbox("Chart Type", ["Bar", "Line", "Area", "Scatter", "Pie"])

# Filter data
mask = (df['DATE'] >= pd.Timestamp(start_date)) & (df['DATE'] <= pd.Timestamp(end_date))
df_filtered = df.loc[mask].sort_values('DATE')

# -------------------------------
# SUMMARY METRICS (TOP ROW)
# -------------------------------
st.title("Retail Shop Performance Dashboard")
st.subheader("Summary Over Selected Period")

total_revenue = df_filtered['REVENUE'].sum()
total_purchases = df_filtered['PURCHASES'].sum()
total_profit = df_filtered['PROFIT'].sum()
avg_turnover = df_filtered['TURNOVER'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"{total_revenue:,.0f} UGX")
col2.metric("Total Purchases", f"{total_purchases:,.0f} UGX")
col3.metric("Total Profit", f"{total_profit:,.0f} UGX")
col4.metric("Avg Turnover", f"{avg_turnover:.1f} Items")

# -------------------------------
# MAIN VISUALIZATIONS
# -------------------------------
st.subheader("Visualizations")

# 1️⃣ Bar / Line / Area Chart - Revenue, Purchases, Profit over time
if chart_type in ["Bar", "Line", "Area"]:
    st.write(f"**{chart_type} Chart: Sales, Purchases, and Profit Over Time**")
    chart_data = df_filtered[['DATE', 'REVENUE', 'PURCHASES', 'PROFIT']].set_index('DATE')
    if chart_type == "Bar":
        st.bar_chart(chart_data)
    elif chart_type == "Line":
        st.line_chart(chart_data)
    elif chart_type == "Area":
        st.area_chart(chart_data)

# 2️⃣ Scatter Plot - Purchases vs Profit (using Plotly for explicit x/y)
if chart_type == "Scatter":
    st.write("**Scatter Plot: Purchases vs Profit**")
    if not df_filtered.empty:
        fig = px.scatter(df_filtered, x="PURCHASES", y="PROFIT",
                         hover_data=["DATE", "REVENUE", "TURNOVER"],
                         title="Purchases vs Profit")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected period.")

# 3️⃣ Pie Chart - Expense Breakdown
if chart_type == "Pie":
    st.write("**Pie Chart: Total Expense Distribution**")
    if not df_filtered.empty:
        expense_sum = df_filtered[['PURCHASES', 'UTILITIES', 'TRANSPORT']].sum().reset_index()
        expense_sum.columns = ['Category', 'Amount']
        fig = px.pie(expense_sum, values='Amount', names='Category', title='Expense Breakdown')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data for the selected period.")

# -------------------------------
# DATA TABLE
# -------------------------------
st.subheader("📋 Data Table (Filtered Period)")
st.dataframe(df_filtered)
