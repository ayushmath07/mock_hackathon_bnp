from pydantic import BaseModel, Field
from typing import List, Dict, Any

class Persona(BaseModel):
    id: str
    name: str
    title: str
    category: str
    description: str
    stated_monthly_income: float
    avatar_url: str

class SimulateAARequest(BaseModel):
    persona_id: str = Field(..., description="ID of the persona (e.g., 'priya_freelancer')")

class SummaryMetrics(BaseModel):
    average_daily_balance: float
    average_monthly_inflow: float
    total_inflow: float
    total_outflow: float
    net_cash_flow: float
    net_savings_rate_pct: float
    inflow_volatility_score: float
    penalty_count: int

class MonthlyCashFlow(BaseModel):
    month: str
    inflow: float
    outflow: float

class SpendingSplit(BaseModel):
    essentials: float
    discretionary: float
    business_expense: float

class SanitizedTransaction(BaseModel):
    id: str
    date: str
    narration: str
    category: str
    group: str
    type: str
    amount: float
    balance: float

class IngestionResponse(BaseModel):
    applicant_id: str
    persona_name: str
    data_period: Dict[str, Any]
    summary_metrics: SummaryMetrics
    monthly_cash_flows: List[MonthlyCashFlow]
    spending_split: SpendingSplit
    sanitized_transactions: List[SanitizedTransaction]