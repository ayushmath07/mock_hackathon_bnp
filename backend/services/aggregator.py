import pandas as pd
import numpy as np
from typing import Dict, Any
from .privacy import mask_pii, is_self_transfer
from .categorizer import categorize_transaction

def process_and_aggregate_transactions(df: pd.DataFrame, applicant_id: str, persona_name: str) -> Dict[str, Any]:
    if df.empty:
        raise ValueError("Provided transaction dataset is empty.")

    df.columns = [c.strip().lower() for c in df.columns]
    df["datetime"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["datetime"]).sort_values("datetime").reset_index(drop=True)
    df["date"] = df["datetime"].dt.date
    df["month_year"] = df["datetime"].dt.strftime("%b %Y")
    df["month_sort"] = df["datetime"].dt.strftime("%Y-%m")

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0).abs()
    df["type"] = df["type"].astype(str).str.strip().str.upper()

    # Reconstruct running balance if absent
    if "balance_after" not in df.columns:
        running_bal = 10000.0
        balances = []
        for _, row in df.iterrows():
            running_bal += row["amount"] if row["type"] == "CREDIT" else -row["amount"]
            balances.append(round(running_bal, 2))
        df["balance_after"] = balances
    else:
        df["balance_after"] = pd.to_numeric(df["balance_after"], errors="coerce").ffill().fillna(0.0)

    # Redaction & Categorization
    df["masked_narration"] = df["narration"].apply(mask_pii)
    df["is_self"] = df["narration"].apply(is_self_transfer)
    
    cats, groups = [], []
    for _, row in df.iterrows():
        cat, grp = categorize_transaction(row["narration"], row["type"])
        cats.append(cat)
        groups.append(grp)
    df["category"], df["group"] = cats, groups

    valid_txns = df[~df["is_self"]].copy()

    # Cash Inflow/Outflow
    total_inflow = float(valid_txns[valid_txns["type"] == "CREDIT"]["amount"].sum())
    total_outflow = float(valid_txns[valid_txns["type"] == "DEBIT"]["amount"].sum())
    net_cash_flow = total_inflow - total_outflow

    # Average Daily Balance (calendar day re-indexed with forward-fill)
    min_date, max_date = df["date"].min(), df["date"].max()
    full_day_range = pd.date_range(start=min_date, end=max_date, freq="D").date
    daily_last_bal = df.groupby("date")["balance_after"].last()
    avg_daily_balance = float(daily_last_bal.reindex(full_day_range).ffill().bfill().mean())

    # Monthly Cash Flows
    monthly_grouped = df.groupby(["month_sort", "month_year"]).apply(
        lambda g: pd.Series({
            "inflow": float(g[(g["type"] == "CREDIT") & (~g["is_self"])]["amount"].sum()),
            "outflow": float(g[(g["type"] == "DEBIT") & (~g["is_self"])]["amount"].sum())
        })
    ).reset_index()

    monthly_cash_flows = [
        {"month": str(r["month_year"]), "inflow": round(float(r["inflow"]), 2), "outflow": round(float(r["outflow"]), 2)}
        for _, r in monthly_grouped.iterrows()
    ]

    num_months = max(len(monthly_grouped), 1)
    avg_monthly_inflow = total_inflow / num_months
    savings_rate_pct = max(0.0, (net_cash_flow / total_inflow * 100)) if total_inflow > 0 else 0.0

    # Inflow Volatility (Coefficient of Variation)
    monthly_inflow_vals = monthly_grouped["inflow"].values
    volatility_score = float(np.std(monthly_inflow_vals) / np.mean(monthly_inflow_vals)) if len(monthly_inflow_vals) > 1 and np.mean(monthly_inflow_vals) > 0 else 0.0

    # Spending Split
    spending = valid_txns[valid_txns["type"] == "DEBIT"].groupby("group")["amount"].sum().to_dict()
    penalty_count = int((df["group"] == "Risk Penalty").sum())

    # Recent Sanitized Transactions
    recent_txns = [
        {
            "id": str(row.get("transaction_id", f"TXN-{row.name}")),
            "date": str(row["date"]),
            "narration": str(row["masked_narration"]),
            "category": str(row["category"]),
            "group": str(row["group"]),
            "type": str(row["type"]),
            "amount": round(float(row["amount"]), 2),
            "balance": round(float(row["balance_after"]), 2)
        }
        for _, row in df.tail(50).iloc[::-1].iterrows()
    ]

    return {
        "applicant_id": applicant_id,
        "persona_name": persona_name,
        "data_period": {"start": str(min_date), "end": str(max_date), "total_days": len(full_day_range)},
        "summary_metrics": {
            "average_daily_balance": round(avg_daily_balance, 2),
            "average_monthly_inflow": round(avg_monthly_inflow, 2),
            "total_inflow": round(total_inflow, 2),
            "total_outflow": round(total_outflow, 2),
            "net_cash_flow": round(net_cash_flow, 2),
            "net_savings_rate_pct": round(savings_rate_pct, 2),
            "inflow_volatility_score": round(volatility_score, 2),
            "penalty_count": penalty_count
        },
        "monthly_cash_flows": monthly_cash_flows,
        "spending_split": {
            "essentials": round(float(spending.get("Essential", 0.0)), 2),
            "discretionary": round(float(spending.get("Discretionary", 0.0)), 2),
            "business_expense": round(float(spending.get("Business Expense", 0.0)), 2)
        },
        "sanitized_transactions": recent_txns
    }