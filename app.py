import streamlit as st
import pandas as pd

# Load your dataset
df = pd.read_csv('final_data_coffee_sme.csv')
df['date'] = pd.to_datetime(df['date'], dayfirst=True)
df = df.sort_values('date')

# =========================
# DATE FILTER
# =========================
st.sidebar.header("Filter")

start_date = st.sidebar.date_input("Start Date", df['date'].min())
end_date = st.sidebar.date_input("End Date", df['date'].max())

filtered_df = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

# safety
if filtered_df.empty:
    st.warning("No data for selected date range")
    st.stop()

# =========================
# VIEW SELECTION
# =========================
view = st.sidebar.selectbox("Select View", ["Daily", "Weekly", "Monthly", "Yearly"])

# =========================
# AGGREGATION
# =========================
if view == "Daily":
    data = filtered_df.copy()
    data['label'] = data['date'].dt.strftime('%d %b')

elif view == "Weekly":
    data = filtered_df.copy()

    # create week index relative to selected range
    data = data.sort_values('date')
    data['week_num'] = ((data['date'] - data['date'].min()).dt.days // 7) + 1

    # group by this custom week
    data = data.groupby('week_num').agg({
        'Revenue': 'sum',
        'Total_Expenses': 'sum',
        'Profit': 'sum'
    }).reset_index()

    # clean label
    data['label'] = 'W' + data['week_num'].astype(str)

elif view == "Monthly":
    data = filtered_df.resample('M', on='date').sum().reset_index()
    data['label'] = data['date'].dt.strftime('%b %Y')

elif view == "Yearly":
    data = filtered_df.resample('YE', on='date').sum().reset_index()
    data['label'] = data['date'].dt.strftime('%Y')

# =========================
# BUSINESS METRICS (NEW 🔥)
# =========================

avg_revenue = filtered_df['Revenue'].mean()
avg_expense = filtered_df['Total_Expenses'].mean()

burn_rate = avg_expense - avg_revenue  # positive = bad

cash_balance = filtered_df['Revenue'].sum()
monthly_expense = avg_expense * 30

runway = cash_balance / monthly_expense if monthly_expense != 0 else 0

expense_ratio = filtered_df['Total_Expenses'].sum() / filtered_df['Revenue'].sum()

# =========================
# BUSINESS HEALTH (NEW LOGIC 🔥)
# =========================
if runway < 3:
    health = "At Risk"
elif expense_ratio > 0.7:
    health = "Moderate"
else:
    health = "Healthy"

# =========================
# TITLE
# =========================
st.title("📊 SME Business Health Dashboard")

# =========================
# KPI SECTION (UPGRADED 🔥)
# =========================
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Revenue", round(filtered_df['Revenue'].sum(), 2))
col2.metric("Profit", round(filtered_df['Profit'].sum(), 2))
col3.metric("Runway (Months)", round(runway, 2))
col4.metric("Burn Rate", round(burn_rate, 2))

st.subheader(f"Business Health: {health}")

# =========================
# CHARTS (UPGRADED 🔥)
# =========================

# Revenue vs Expenses
st.subheader("Revenue vs Expenses")
st.line_chart(data.set_index('label')[['Revenue', 'Total_Expenses']])

# Burn Trend
data['Burn'] = data['Total_Expenses'] - data['Revenue']
st.subheader("Cash Burn Trend")
st.line_chart(data.set_index('label')['Burn'])

# Expense Ratio Trend
data['Expense_Ratio'] = data['Total_Expenses'] / data['Revenue']
st.subheader("Expense Ratio Trend")
st.line_chart(data.set_index('label')['Expense_Ratio'])

# =========================
# SMART DECISION INSIGHTS
# =========================

st.subheader("What Should You Do?")

if runway < 3:
    st.error("🚨 Business may not survive beyond 3 months — reduce costs immediately")

elif expense_ratio > 0.7:
    st.warning("⚠️ High expenses — consider cutting operational costs")

elif burn_rate > 0:
    st.error("🔥 You are losing money — increase revenue or reduce spending")

elif filtered_df['Revenue'].tail(7).mean() < filtered_df['Revenue'].head(7).mean():
    st.warning("📉 Revenue is declining — consider marketing or pricing changes")

else:
    st.success("✅ Business is financially stable — focus on growth")

# =========================
# SUMMARY
# =========================
st.subheader("Summary")

st.write(f"""
This system evaluates business survivability using:

- Runway: {round(runway,2)} months  
- Burn Rate: {round(burn_rate,2)}  
- Expense Ratio: {round(expense_ratio,2)}  

It helps identify when to intervene, cut costs, or improve revenue strategies.
""")