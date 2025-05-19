# Must be first
import streamlit as st
st.set_page_config(page_title="AI Personal Finance Assistant", page_icon="💰", layout="wide")

import os
import PyPDF2
import google.generativeai as genai

# === Gemini API key from Streamlit secrets ===
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    /* Animated Gradient Background */
    html, body, .stApp {
        background: linear-gradient(270deg, #f556ad, #f6b73c, #2af598, #009efd, #f556ad);
        background-size: 1000% 1000%;
        animation: gradientBackground 30s ease infinite;
        font-family: 'Segoe UI', sans-serif;
        color: #1a1a1a;
    }

    @keyframes gradientBackground {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 900;
        background: linear-gradient(to right, #1a2a6c, #b21f1f, #fdbb2d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-top: 20px;
        margin-bottom: 10px;
    }

    .sub-title {
        text-align: center;
        font-size: 20px;
        color: #f1f1f1;
        font-weight: 500;
        margin-bottom: 30px;
        text-shadow: 1px 1px 5px rgba(0, 0, 0, 0.4);
    }

    .result-card {
        background: rgba(255, 255, 255, 0.12);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.25);
        color: #fff;
    }

    .success-banner {
        background: linear-gradient(to right, #ff416c, #ff4b2b);
        color: white;
        padding: 18px;
        font-size: 18px;
        font-weight: bold;
        border-radius: 12px;
        text-align: center;
        margin-top: 30px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    /* Sidebar container with solid background */
    section[data-testid="stSidebar"] {
        background-color: #143070;
        color: white;
        padding: 20px;
        border-top-right-radius: 12px;
        border-bottom-right-radius: 12px;
    }

    /* Ensure all text in sidebar is white */
    section[data-testid="stSidebar"] * {
        color: white !important;
    }

    .stButton > button {
        background: linear-gradient(to right, #00c9ff, #92fe9d);
        border: none;
        color: black;
        font-weight: bold;
        padding: 10px 20px;
        border-radius: 50px;
        font-size: 16px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        transition: all 0.3s ease-in-out;
    }

    .stButton > button:hover {
        background: linear-gradient(to right, #92fe9d, #00c9ff);
        transform: scale(1.05);
        box-shadow: 0 6px 18px rgba(0,0,0,0.3);
    }

    .css-1aumxhk {
        background-color: transparent;
    }

    .css-1cpxqw2 {
        background-color: transparent;
    }

    /* Optional: style tables */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        background-color: white;
    }
    </style>
""", unsafe_allow_html=True)


# --- Sidebar ---
st.sidebar.title("ℹ️ How to Use")
st.sidebar.write("""
1. Upload your UPI or Paytm transaction PDF  
2. The AI will extract and analyze the data  
3. Get monthly financial insights and advice
""")

# --- Page Title ---
st.markdown('<h1 class="main-title">💰 AI-Powered Personal Finance Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Upload your UPI or Paytm Transaction PDF</p>', unsafe_allow_html=True)

# --- File Uploader ---
uploaded_file = st.file_uploader("📂 Upload PDF File", type=["pdf"], help="Only PDF files are supported")

# --- Extractor with Fallback ---
def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"

    if text.strip():
        return text

    # Fallback to PyMuPDF
    import fitz
    with fitz.open(file_path) as doc:
        return "\n".join(page.get_text() for page in doc)

# --- Gemini Prompt ---
def analyze_financial_data(text):
    model = genai.GenerativeModel("gemini-1.5-flash")
    prompt = f"""
    You are a financial assistant. Analyze the following raw transaction data from a user's UPI PDF statement.

    Extract meaningful insights from the transactions.

    1. Provide a clean **Monthly Summary**:
     - Total Income
     - Total Expenses
     - Net Savings and Savings Percentage

    2. Highlight **Top 3 Spending Categories** with amounts.

    3. Detect any **Unnecessary or Irregular Expenses**:
     - List items that are unusual, recurring small amounts, or impulse-like.

    4. Identify **Spending Trends**:
     - Peaks (which days or categories)
     - Patterns (e.g. weekend spikes, late-night orders)

    5. Give **3 Personalized Financial Recommendations**:
     - Budget suggestions
     - Cost-saving tips
     - Expense optimization advice

    Here is the extracted data:
        {text}
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip() if response else "⚠️ No response from Gemini."
    except Exception as e:
        return f"⚠️ Gemini API Error: {e}"

# --- Main Logic ---
if uploaded_file is not None:
    file_path = f"temp_{uploaded_file.name}"
    with open(file_path, "wb") as f:
        f.write(uploaded_file.read())

    st.success("✅ File uploaded successfully!")

    with st.spinner("📄 Extracting text from PDF..."):
        extracted_text = extract_text_from_pdf(file_path)

    if not extracted_text.strip():
        st.error("⚠️ Failed to extract text. Try a different PDF or ensure it's not scanned.")
    else:
        progress = st.progress(10)
        with st.spinner("🤖 This AI is analyzing your financial data..."):
            insights = analyze_financial_data(extracted_text)
        progress.progress(100)

        st.subheader("📊 Financial Insights Report")
        st.markdown(f'<div class="result-card"><b>📄 Report for {uploaded_file.name}</b></div>', unsafe_allow_html=True)
        st.markdown(insights)
        st.markdown('<div class="success-banner">🎉 Done! Use these insights to improve your finances.</div>', unsafe_allow_html=True)
        st.snow()

    # Cleanup
    try:
        os.remove(file_path)
    except:
        pass
