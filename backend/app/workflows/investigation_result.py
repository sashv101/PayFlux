from enum import Enum

from pydantic import BaseModel, Field


class RecommendedAction(str, Enum):
    ESCALATE_SETTLEMENT = "escalate_settlement"
    EXPLAIN_SETTLEMENT_SCHEDULE = "explain_settlement_schedule"
    EXPLAIN_PAYMENT_FAILURE = "explain_payment_failure"
    REQUEST_DIAGNOSTICS = "request_diagnostics"
    ROUTE_COMPLIANCE_REVIEW = "route_compliance_review"


class InvestigationResult(BaseModel):
    ticket_id: str = Field(
        description="The ticket ID that was investigated."
    )

    issue_verified: bool = Field(
        description="Whether database evidence supports the reported issue."
    )

    verified_facts: list[str] = Field(
        description="Facts verified through tool calls."
    )

    policy_source: str = Field(
        description="The policy document used during the investigation."
    )

    assessment: str = Field(
        description="A concise evidence-based assessment of the issue."
    )

    recommended_action: RecommendedAction = Field(
        description="The action recommended by the agent."
    )

    merchant_response: str = Field(
        description="A clear response that support can send to the merchant."
    )

    approval_required: bool = Field(
        description="Whether human approval is required before execution."
    )

    action_executed: bool = Field(
        description=(
            "Whether the recommended action was actually executed. "
            "This must be false when no execution tool was called."
        )
    )