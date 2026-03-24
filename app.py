import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

st.set_page_config(page_title="ProfitPilot", layout="wide")

# =========================
# UI STYLING (PREMIUM)
# =========================
st.markdown("""
<style>

/* Background */
body {
    background: #f5f7fb;
}

/* Title */
.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

/* Subtitle */
.sub-text {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 25px;
}

/* KPI Cards */
.kpi-card {
    background: linear-gradient(145deg, #ffffff, #f1f5f9);
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    text-align: center;
    transition: 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-3px);
}

.kpi-card h4 {
    color: #6b7280;
    font-size: 14px;
    margin-bottom: 5px;
}

.kpi-card h2 {
    font-size: 28px;
    font-weight: 700;
    color: #111827;
}

/* Insight boxes */
.good {
    background: #ecfdf5;
    padding: 14px;
    border-radius: 12px;
    color: #047857;
    font-weight: 500;
}

.warn {
    background: #fffbeb;
    padding: 14px;
    border-radius: 12px;
    color: #b45309;
    font-weight: 500;
}

.bad {
    background: #fef2f2;
    padding: 14px;
    border-radius: 12px;
    color: #b91c1c;
    font-weight: 500;
}

</style>
""", unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
if "df" not in st.session_state:
    df = pd.read_csv('final_sme_data.csv')
    df['date'] = pd.to_datetime(df['date'], dayfirst=True)
    df = df.sort_values('date')
    st.session_state.df = df

df = st.session_state.df

# =========================
# SIDEBAR
# =========================
view = st.sidebar.selectbox("View", ["Daily", "Weekly", "Monthly", "Yearly"])

st.sidebar.header("Filters")
start_date = st.sidebar.date_input("Start Date", df['date'].min())
end_date = st.sidebar.date_input("End Date", df['date'].max())

if start_date > end_date:
    st.error("Invalid date range")
    st.stop()

# =========================
# USER INPUT
# =========================
st.sidebar.markdown("---")
st.sidebar.header("Add New Data")

revenue_input = st.sidebar.number_input("Revenue", min_value=0.0)

rent = st.sidebar.number_input("Rent", min_value=0.0)
salaries = st.sidebar.number_input("Salaries", min_value=0.0)
utilities = st.sidebar.number_input("Utilities", min_value=0.0)

marketing = st.sidebar.number_input("Marketing Spend", min_value=0.0)
materials = st.sidebar.number_input("Raw Materials", min_value=0.0)

add_data = st.sidebar.button("Add Entry")

fixed_costs = rent + salaries + utilities
variable_costs = marketing + materials
total_expenses_input = fixed_costs + variable_costs
profit_input = revenue_input - total_expenses_input

# =========================
# APPEND DATA
# =========================
if add_data and revenue_input > 0:
    last_date = df['date'].max()

    if view == "Daily":
        delta = timedelta(days=1)
    elif view == "Weekly":
        delta = timedelta(weeks=1)
    elif view == "Monthly":
        delta = pd.DateOffset(months=1)
    else:
        delta = pd.DateOffset(years=1)

    new_date = last_date + delta

    new_row = pd.DataFrame({
        'date': [new_date],
        'Revenue': [revenue_input],
        'Total_Expenses': [total_expenses_input],
        'Profit': [profit_input]
    })

    st.session_state.df = pd.concat([df, new_row], ignore_index=True)
    st.session_state.df = st.session_state.df.sort_values('date')

    df = st.session_state.df
    end_date = new_date

# =========================
# FILTER DATA
# =========================
filtered_df = df[(df['date'] >= pd.to_datetime(start_date)) &
                 (df['date'] <= pd.to_datetime(end_date))]

if filtered_df.empty:
    st.warning("No data available")
    st.stop()

# =========================
# AGGREGATION
# =========================
if view == "Daily":
    data = filtered_df.copy()

elif view == "Weekly":
    data = filtered_df.copy()
    data['year'] = data['date'].dt.isocalendar().year
    data['week'] = data['date'].dt.isocalendar().week

    data = data.groupby(['year', 'week']).agg({
        'date': 'min',
        'Revenue': 'sum',
        'Total_Expenses': 'sum',
        'Profit': 'sum'
    }).reset_index()

elif view == "Monthly":
    data = filtered_df.resample('M', on='date').sum().reset_index()

elif view == "Yearly":
    data = filtered_df.resample('YE', on='date').sum().reset_index()

data = data.sort_values('date')

# =========================
# METRICS
# =========================
avg_revenue = filtered_df['Revenue'].mean()
avg_expense = filtered_df['Total_Expenses'].mean()

burn_rate = avg_expense - avg_revenue

cash_balance = filtered_df['Revenue'].sum()
monthly_expense = avg_expense * 30

runway = cash_balance / monthly_expense if monthly_expense != 0 else 0

expense_ratio = filtered_df['Total_Expenses'].sum() / filtered_df['Revenue'].sum()

# =========================
# HEADER
# =========================
st.markdown('<div class="main-title">SME Business Health Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Analyze financial performance and support business decisions</div>', unsafe_allow_html=True)

# =========================
# KPI
# =========================
col1, col2, col3, col4 = st.columns(4)

col1.markdown(f'<div class="kpi-card"><h4>Revenue</h4><h2>{round(filtered_df["Revenue"].sum(),0):,}</h2></div>', unsafe_allow_html=True)
col2.markdown(f'<div class="kpi-card"><h4>Profit</h4><h2>{round(filtered_df["Profit"].sum(),0):,}</h2></div>', unsafe_allow_html=True)
col3.markdown(f'<div class="kpi-card"><h4>Runway</h4><h2>{round(runway,1)}</h2></div>', unsafe_allow_html=True)
col4.markdown(f'<div class="kpi-card"><h4>Burn Rate</h4><h2>{round(burn_rate,1)}</h2></div>', unsafe_allow_html=True)

# =========================
# CHARTS
# =========================
st.markdown("### Revenue vs Expenses")
st.line_chart(data.set_index('date')[['Revenue', 'Total_Expenses']])

data['Burn'] = data['Total_Expenses'] - data['Revenue']
st.markdown("### Cash Burn Trend")
st.line_chart(data.set_index('date')['Burn'])

data['Expense_Ratio'] = data['Total_Expenses'] / data['Revenue']
st.markdown("### Expense Ratio Trend")
st.line_chart(data.set_index('date')['Expense_Ratio'])

# =========================
# FORECAST (FIXED)
# =========================
st.markdown("### Revenue Forecast")

if len(filtered_df) > 5:
    df_forecast = filtered_df.copy().sort_values('date')

    y = df_forecast['Revenue'].values
    x = np.arange(len(y))

    slope, intercept = np.polyfit(x, y, 1)

    future_x = np.arange(len(y), len(y) + 10)
    forecast = slope * future_x + intercept

    last_date = df_forecast['date'].max()
    future_dates = pd.date_range(start=last_date, periods=10, freq='D')

    forecast_df = pd.DataFrame({
        'date': future_dates,
        'Revenue': forecast
    })

    combined = pd.concat([
        df_forecast[['date', 'Revenue']],
        forecast_df
    ])

    st.line_chart(combined.set_index('date'))

else:
    st.info("Select a wider range for forecasting")

# =========================
# INSIGHTS
# =========================
st.markdown("### Insights")

if runway < 3:
    st.markdown('<div class="bad">Business may not survive beyond 3 months</div>', unsafe_allow_html=True)

elif expense_ratio > 0.7:
    st.markdown('<div class="warn">High expenses — reduce costs</div>', unsafe_allow_html=True)

elif burn_rate > 0:
    st.markdown('<div class="bad">Business is losing money</div>', unsafe_allow_html=True)

else:
    st.markdown('<div class="good">Business is stable</div>', unsafe_allow_html=True)
