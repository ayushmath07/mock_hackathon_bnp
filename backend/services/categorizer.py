from typing import Tuple

CATEGORY_RULES = [
    ("Salary / Payroll", "Inflow", ["SALARY", "PAYROLL", "MONTHLY WAGES", "EMPLOYER"]),
    ("Gig / Freelance Inflow", "Inflow", ["UPWORK", "FIVERR", "RAZORPAY", "FREELANCE", "CLIENT PAY", "ESCROW"]),
    ("Business Merchant UPI", "Inflow", ["PAYTM-QR", "PHONEPE-QR", "BHARATPE", "MERCHANT SETTLEMENT", "QR-MERC"]),
    ("Rent & Housing", "Essential", ["RENT", "LANDLORD", "HOUSING", "SOCIETY MAINT"]),
    ("Utilities & Bills", "Essential", ["MSEDCL", "BESCOM", "TNEB", "ELECTRICITY", "AIRTEL", "JIO", "BROADBAND", "WATER", "BILLDESK"]),
    ("Groceries & Food Staples", "Essential", ["BLINKIT", "ZEPTO", "BIGBASKET", "DMART", "NATURES BASKET", "GROCERY"]),
    ("Supplier & Inventory", "Business Expense", ["METRO-CASH", "UDAAN", "HUL-CONSUMER", "WHOLESALE", "DISTRIBUTION"]),
    ("Discretionary & Dining", "Discretionary", ["SWIGGY", "ZOMATO", "STARBUCKS", "MCDONALDS", "DOMINOS", "RESTAURANT"]),
    ("Entertainment & Shopping", "Discretionary", ["AMAZON", "FLIPKART", "MYNTRA", "NETFLIX", "SPOTIFY", "BOOKMYSHOW"]),
    ("Mobility & Travel", "Discretionary", ["UBER", "OLA", "RAPIDO", "IRCTC", "MAKEMYTRIP", "PETROL", "FUEL"]),
    ("Bank Charges & Penalties", "Risk Penalty", ["MIN BAL", "CHQ RETURN", "BOUNCE", "OVERDRAFT CHG", "ECS REJECT", "PENALTY"])
]

def categorize_transaction(narration: str, txn_type: str) -> Tuple[str, str]:
    if not isinstance(narration, str):
        return ("General Transfer", "Other")
    
    upper = narration.upper()
    for cat_name, group, keywords in CATEGORY_RULES:
        if any(kw in upper for kw in keywords):
            return (cat_name, group)
            
    return ("General Inflow", "Inflow") if txn_type.upper() == "CREDIT" else ("General Expense", "Discretionary")