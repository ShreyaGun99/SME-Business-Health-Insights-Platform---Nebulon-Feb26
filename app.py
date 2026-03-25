import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta

st.set_page_config(page_title="Business Health Dashboard", layout="wide")

# =========================
# UI STYLING
# =========================
st.markdown("""
<style>
body { background: #f5f7fb; }

.main-title {
    font-size: 42px;
    font-weight: 800;
    background: linear-gradient(90deg, #2563eb, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.sub-text {
    font-size: 16px;
    color: #6b7280;
    margin-bottom: 25px;
}

.kpi-card {
    background: linear-gradient(145deg, #ffffff, #f1f5f9);
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    text-align: center;
}

.good { background: #ecfdf5; padding: 14px; border-radius: 12px; color: #047857; }
.warn { background: #fffbeb; padding: 14px; border-radius: 12px; color: #b45309; }
.bad { background: #fef2f2; padding: 14px; border-radius: 12px; color: #b91c1c; }
</style>
""", unsafe_allow_html=True)

# =========================
# MODE
# =========================
mode = st.sidebar.radio("Select Mode", ["Demo Data", "Upload CSV"])

# =========================
# LOAD DATA
# =========================
if mode == "Demo Data":
    if "df" not in st.session_state:
        df = pd.read_csv('final_sme_data.csv')
        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        df = df.sort_values('date')
        st.session_state.df = df
    df = st.session_state.df

else:
    st.sidebar.markdown("""
    ### CSV Format:
    date, Revenue, Total_Expenses
    """)

    file = st.sidebar.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip()

        if 'Date' in df.columns:
            df.rename(columns={'Date': 'date'}, inplace=True)

        required = ['date','Revenue','Total_Expenses']

        if not all(col in df.columns for col in required):
            st.error("CSV must contain date, Revenue, Total_Expenses")
            st.stop()

        df['date'] = pd.to_datetime(df['date'], dayfirst=True)
        df = df.sort_values('date')

        # Auto Profit
        df['Profit'] = df['Revenue'] - df['Total_Expenses']

        # =========================
        # ADD NEW DATA (UPLOAD MODE) 🔥
        # =========================
        st.sidebar.markdown("---")
        st.sidebar.header("Add New Data")

        revenue_input = st.sidebar.number_input("Revenue", min_value=0.0, key="u_rev")

        rent = st.sidebar.number_input("Rent", min_value=0.0, key="u_rent")
        salaries = st.sidebar.number_input("Employee Salaries", min_value=0.0, key="u_sal")
        utilities = st.sidebar.number_input("Utilities", min_value=0.0, key="u_util")

        marketing = st.sidebar.number_input("Marketing Spend", min_value=0.0, key="u_mark")
        materials = st.sidebar.number_input("Raw Materials", min_value=0.0, key="u_mat")

        add_data_upload = st.sidebar.button("Add Entry", key="u_add")

        total_expenses_input = rent + salaries + utilities + marketing + materials
        profit_input = revenue_input - total_expenses_input

        if add_data_upload and revenue_input > 0:
            new_date = df['date'].max() + timedelta(days=1)

            new_row = pd.DataFrame({
                'date': [new_date],
                'Revenue': [revenue_input],
                'Total_Expenses': [total_expenses_input],
                'Profit': [profit_input]
            })

            df = pd.concat([df, new_row], ignore_index=True)

    else:
        st.stop()

# =========================
# FILTER
# =========================
view = st.sidebar.selectbox("View", ["Daily","Weekly","Monthly","Yearly"])

start_date = st.sidebar.date_input("Start Date", df['date'].min())
end_date = st.sidebar.date_input("End Date", df['date'].max())

filtered_df = df[(df['date']>=pd.to_datetime(start_date)) &
                 (df['date']<=pd.to_datetime(end_date))]

MIN_POINTS = 10

if len(filtered_df) < MIN_POINTS:
    st.warning("Select a wider date range for meaningful analysis")

# =========================
# ADD NEW DATA (DEMO MODE)
# =========================
if mode == "Demo Data":

    st.sidebar.markdown("---")
    st.sidebar.header("Add New Data")

    revenue_input = st.sidebar.number_input("Revenue", min_value=0.0)

    rent = st.sidebar.number_input("Rent", min_value=0.0)
    salaries = st.sidebar.number_input("Employee Salaries", min_value=0.0)
    utilities = st.sidebar.number_input("Utilities", min_value=0.0)

    marketing = st.sidebar.number_input("Marketing Spend", min_value=0.0)
    materials = st.sidebar.number_input("Raw Materials", min_value=0.0)

    add_data = st.sidebar.button("Add Entry")

    total_expenses_input = rent + salaries + utilities + marketing + materials
    profit_input = revenue_input - total_expenses_input

    if add_data and revenue_input > 0:
        new_date = df['date'].max() + timedelta(days=1)

        new_row = pd.DataFrame({
            'date': [new_date],
            'Revenue': [revenue_input],
            'Total_Expenses': [total_expenses_input],
            'Profit': [profit_input]
        })

        st.session_state.df = pd.concat([df, new_row], ignore_index=True)
        df = st.session_state.df

# =========================
# AGGREGATION
# =========================
if view == "Daily":
    data = filtered_df.copy()

elif view == "Weekly":
    data = filtered_df.copy()

    data['week'] = data['date'].dt.to_period('W').apply(lambda r: r.start_time)

    data = data.groupby('week').agg({
        'Revenue': 'sum',
        'Total_Expenses': 'sum',
        'Profit': 'sum'
    }).reset_index()

    data.rename(columns={'week': 'date'}, inplace=True)

elif view == "Monthly":
    data = filtered_df.resample('M', on='date').sum().reset_index()

elif view == "Yearly":
    data = filtered_df.resample('YE', on='date').sum().reset_index()

# =========================
# METRICS
# =========================
avg_rev = filtered_df['Revenue'].mean()
avg_exp = filtered_df['Total_Expenses'].mean()

burn = avg_exp - avg_rev
cash = filtered_df['Revenue'].sum()
runway = cash / (avg_exp*30) if avg_exp!=0 else 0
ratio = filtered_df['Total_Expenses'].sum()/filtered_df['Revenue'].sum()

# =========================
# HEADER
# =========================
st.markdown('<div class="main-title">Business Health Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Monitor financial performance and support decision-making</div>', unsafe_allow_html=True)

# =========================
# KPI
# =========================
c1,c2,c3,c4 = st.columns(4)

c1.markdown(f'<div class="kpi-card"><h4>Revenue</h4><h2>{round(filtered_df["Revenue"].sum(),0):,}</h2></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><h4>Profit</h4><h2>{round(filtered_df["Profit"].sum(),0):,}</h2></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><h4>Runway</h4><h2>{round(runway,1)}</h2></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><h4>Burn Rate</h4><h2>{round(burn,1)}</h2></div>', unsafe_allow_html=True)

# =========================
# CHARTS
# =========================
st.markdown("### Revenue vs Expenses")
st.line_chart(data.set_index('date')[['Revenue','Total_Expenses']])

data['Burn'] = data['Total_Expenses'] - data['Revenue']
st.markdown("### Cash Burn Trend")
st.line_chart(data.set_index('date')['Burn'])

data['Expense_Ratio'] = data['Total_Expenses']/data['Revenue']
st.markdown("### Expense Ratio Trend")
st.line_chart(data.set_index('date')['Expense_Ratio'])

# =========================
# FORECAST
# =========================
st.markdown("### Revenue Forecast")

if len(filtered_df) >= MIN_POINTS:
    y = filtered_df['Revenue'].values
    x = np.arange(len(y))

    slope, intercept = np.polyfit(x,y,1)

    future_x = np.arange(len(y), len(y)+10)
    forecast = slope*future_x + intercept

    freq_map = {"Daily":"D","Weekly":"W","Monthly":"M","Yearly":"Y"}

    future_dates = pd.date_range(start=filtered_df['date'].max(),
                                 periods=10,
                                 freq=freq_map[view])

    forecast_df = pd.DataFrame({'date':future_dates,'Revenue':forecast})

    combined = pd.concat([filtered_df[['date','Revenue']], forecast_df])

    st.line_chart(combined.set_index('date'))

# =========================
# INSIGHTS
# =========================
st.markdown("### Insights")

flag=False

if runway < 3:
    st.markdown('<div class="bad">Business may not survive beyond 3 months — urgent cost control needed</div>', unsafe_allow_html=True)
    flag=True

if ratio > 0.7:
    st.markdown('<div class="warn">Expenses are high relative to revenue — optimize cost structure</div>', unsafe_allow_html=True)
    flag=True

if burn > 0:
    st.markdown('<div class="bad">Business is operating at a loss — immediate action required</div>', unsafe_allow_html=True)
    flag=True

# =========================
# TREND
# =========================
if len(filtered_df) >= MIN_POINTS:

    y = filtered_df['Revenue'].values
    x = np.arange(len(y))

    raw_slope = np.polyfit(x,y,1)[0]
    mean_rev = np.mean(y)
    norm_slope = raw_slope / mean_rev if mean_rev!=0 else 0

    if norm_slope > 0.05:
        trend_msg = "Strong growth — excellent opportunity to scale the business"
    elif norm_slope > 0.01:
        trend_msg = "Moderate growth — good opportunity to expand operations"
    elif norm_slope > -0.01:
        trend_msg = "Stable performance — business is steady with potential to grow"
    elif norm_slope > -0.05:
        trend_msg = "Slight decline — monitor performance and adjust strategy"
    else:
        trend_msg = "Significant decline — strategic intervention required"

    st.caption(f"Trend: {trend_msg} ({round(norm_slope*100,2)}% change)")

# =========================
# POSITIVE DEFAULT
# =========================
if not flag:
    st.markdown('<div class="good">Business is performing well — strong opportunity to grow and scale</div>', unsafe_allow_html=True)
