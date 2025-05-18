import streamlit as st


import pandas as pd
import fitz  # PyMuPDF
import re
from datetime import datetime
import openai
import os


st.set_page_config(page_title="UPI Analyzer", layout="wide")
st.title("📄 UPI Statement Analyzer with AI Advice")

uploaded_file = st.file_uploader(
    "📂 Upload your UPI statement PDF (Paytm, GPay, PhonePe, Bank)",
    type=["pdf"]
)


if not uploaded_file:
    st.warning("👆 Please upload a PDF file to continue.")
    st.stop()

# --------------- PDF Extraction --------------- #
def extract_text_lines(uploaded_file):
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        all_text = ""
        for page in doc:
            all_text += page.get_text()
    return all_text.split("\n")

# --------------- Transaction Block Parsing --------------- #
def group_transaction_blocks(lines):
    blocks = []
    current_block = []

    for line in lines:
        if re.match(r"\d{2} \w{3} \d{2}", line):
            if current_block:
                blocks.append(" ".join(current_block))
                current_block = []
        current_block.append(line.strip())

    if current_block:
        blocks.append(" ".join(current_block))

    return blocks

# --------------- Block to Transaction Parsing --------------- #
def parse_transaction_blocks(blocks):
    transactions = []
    for block in blocks:
        date_match = re.search(r"(\d{2} \w{3} \d{2})", block)
        amount_match = re.search(r"(\d{1,3}(?:,\d{3})*(?:\.\d{2}))", block)

        if date_match and amount_match:
            try:
                date = datetime.strptime(date_match.group(1), "%d %b %y").strftime("%Y-%m-%d")
                amount = float(amount_match.group(1).replace(",", ""))
                desc = re.sub(r"\d{2} \w{3} \d{2}", "", block).strip()
                tx_type = "Credit" if "RETURN" in block.upper() or "INTEREST" in block.upper() else "Debit"

                transactions.append({
                    "date": date,
                    "description": desc,
                    "amount": amount,
                    "type": tx_type
                })
            except:
                continue
    return transactions

# --------------- Categorization --------------- #
def categorize_transaction(description):
    desc = description.lower()
    if "zomato" in desc or "swiggy" in desc:
        return "Food"
    elif "googlepay" in desc or "paytm" in desc or "upi" in desc:
        return "UPI Payment"
    elif "imps" in desc or "transfer" in desc:
        return "Bank Transfer"
    elif "interest" in desc or "salary" in desc:
        return "Income"
    elif "recharge" in desc or "bill" in desc:
        return "Utilities"
    else:
        return "Others"

# --------------- LLM Insight (OpenAI for now) --------------- #
def get_llm_insight(transactions_summary):
    openai.api_key = st.secrets["OPENAI_API_KEY"]  # Set this in Hugging Face Secrets tab

    prompt = f"""
    Analyze the user's monthly transaction summary below:
    {transactions_summary}

    Provide:
    - Monthly savings percentage
    - Unnecessary spending areas
    - 3 personalized financial suggestions
    """

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

# --------------- Streamlit UI --------------- #
st.set_page_config(page_title="UPI Analyzer AI", layout="wide")
st.title("📄 UPI Statement Analyzer with AI Advice")

uploaded_file = st.file_uploader("Upload your UPI statement PDF (Paytm, GPay, PhonePe)", type=["pdf"])

if uploaded_file:
    st.info("Extracting and processing your file...")
    lines = extract_text_lines(uploaded_file)
    blocks = group_transaction_blocks(lines)
    txns = parse_transaction_blocks(blocks)

    for txn in txns:
        txn["category"] = categorize_transaction(txn["description"])

    df = pd.DataFrame(txns)
    df["date"] = pd.to_datetime(df["date"])

    st.success("✅ Transactions parsed and categorized!")

    # Show Data Table
    st.subheader("📊 Transaction Table")
    st.dataframe(df)

    # Summary Metrics
    st.subheader("📌 Summary")
    income = df[df["type"] == "Credit"]["amount"].sum()
    expense = df[df["type"] == "Debit"]["amount"].sum()
    savings = income - expense
    savings_percent = (savings / income) * 100 if income > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{income:,.2f}")
    col2.metric("Total Expenses", f"₹{expense:,.2f}")
    col3.metric("Savings %", f"{savings_percent:.2f}%")

    # Bar Chart: Category Spending
    st.subheader("💸 Category-wise Expenses")
    cat_chart = df[df["type"] == "Debit"].groupby("category")["amount"].sum()
    st.bar_chart(cat_chart)

    # AI Insights
    st.subheader("🤖 Personalized Financial Advice")
    summary_dict = df.groupby("category")["amount"].sum().to_dict()
    insights = get_llm_insight(summary_dict)
    st.markdown(insights)

    # Download Button
    st.download_button("📥 Download Transactions CSV", df.to_csv(index=False), file_name="transactions.csv", mime="text/csv")
