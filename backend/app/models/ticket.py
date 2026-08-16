from pydantic import BaseModel


class TicketSummary(BaseModel):
    ticket_id: str
    merchant_id: str
    payment_id: str | None
    settlement_id: str | None
    subject: str
    category: str
    priority: str
    status: str
    created_at: str

class MerchantEvidence(BaseModel):
    merchant_id: str
    business_name: str
    business_type: str
    city: str
    kyc_status: str
    settlement_cycle_days: int


class PaymentEvidence(BaseModel):
    payment_id: str
    amount_paise: int
    payment_method: str
    status: str
    failure_code: str | None
    created_at: str


class SettlementEvidence(BaseModel):
    settlement_id: str
    amount_paise: int
    status: str
    scheduled_at: str
    settled_at: str | None
    hold_reason: str | None


class TicketDetail(BaseModel):
    ticket_id: str
    subject: str
    description: str
    category: str
    priority: str
    status: str
    created_at: str
    merchant: MerchantEvidence
    payment: PaymentEvidence | None
    settlement: SettlementEvidence | None   