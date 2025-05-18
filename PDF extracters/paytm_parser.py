import pdfplumber
import re
from datetime import datetime

def is_date(line):
    return re.match(r"\d{2} \w{3} \d{2}", line.strip()) is not None

def extract_transactions_from_pdf(pdf_path):
    transactions = []
    with pdfplumber.open(pdf_path) as pdf:
        current_date = None
        for page in pdf.pages:
            text = page.extract_text()
            lines = text.split('\n')

            for line in lines:
                # Check if line starts with a date
                date_match = re.match(r"(\d{2} \w{3} \d{2})", line.strip())
                if date_match:
                    current_date = datetime.strptime(date_match.group(1), "%d %b %y").strftime("%Y-%m-%d")

                # Match UPI lines with amount
                if "UPI/" in line or "IMPS" in line or "REWARD" in line:
                    # Try to extract amount from end of line
                    amount_match = re.search(r"\s+([\d,]+\.\d{2})\s+[\d,]+\.\d{2}", line)
                    if amount_match:
                        amount = float(amount_match.group(1).replace(",", ""))
                        desc = line.strip()
                        transactions.append({
                            "date": current_date,
                            "description": desc,
                            "amount": amount,
                            "type": "Debit" if amount > 0 else "Credit"
                        })

    return transactions

