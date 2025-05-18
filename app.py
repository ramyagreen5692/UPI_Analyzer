import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load parsed data
df = pd.read_csv("D://UPI_Analyzer//PDF extractors//parsed_transactions.csv")

# Convert date column to datetime
df["date"] = pd.to_datetime(df["date"])

# Sidebar filters
st.sidebar.title("Filters")
date_range = st.sidebar.date_input("Select Date Range", [df["date"].min(), df["date"].max()])
selected_category = st.sidebar.multiselect("Select Categories", df["category"].unique(), default=df["category"].unique())

# Filter data
filtered_df = df[
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1])) &
    (df["category"].isin(selected_category))
]

# App title
st.title("📊 UPI Transaction Analyzer")
st.markdown("Visualize your UPI transaction data with insights.")

# Show raw table
st.subheader("📄 Filtered Transactions")
st.dataframe(filtered_df)

# Summary metrics
total_spent = filtered_df[filtered_df["type"] == "Debit"]["amount"].sum()
total_income = filtered_df[filtered_df["type"] == "Credit"]["amount"].sum()
net_savings = total_income - total_spent

st.metric("Total Income", f"₹{total_income:,.2f}")
st.metric("Total Expenses", f"₹{total_spent:,.2f}")
st.metric("Net Savings", f"₹{net_savings:,.2f}")

# Pie chart: Category-wise spend
st.subheader("💸 Category-wise Expense Distribution")
category_spend = filtered_df[filtered_df["type"] == "Debit"].groupby("category")["amount"].sum()

fig1, ax1 = plt.subplots()
ax1.pie(category_spend, labels=category_spend.index, autopct="%1.1f%%", startangle=90)
ax1.axis("equal")
st.pyplot(fig1)

# Bar chart: Spending over time
st.subheader("📆 Daily Spending Trend")
daily_expense = filtered_df[filtered_df["type"] == "Debit"].groupby("date")["amount"].sum()

st.line_chart(daily_expense)

# Option to download filtered data
st.download_button("Download Filtered CSV", filtered_df.to_csv(index=False), "filtered_transactions.csv", "text/csv")
