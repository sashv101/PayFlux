from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    ESCALATE_SETTLEMENT = "escalate_settlement"
    ROUTE_COMPLIANCE_REVIEW = "route_compliance_review"
    REQUEST_DIAGNOSTICS = "request_diagnostics"
    ADD_SUPPORT_NOTE = "add_support_note"


class ActionStatus(str, Enum):
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class ProposedAction(BaseModel):
    action_id: str = Field(
        description="Unique identifier for the proposed action."
    )

    ticket_id: str = Field(
        description="Ticket that caused the action to be proposed."
    )

    action_type: ActionType = Field(
        description="Operational action being proposed."
    )

    target_id: str = Field(
        description=(
            "Settlement, payment, merchant, or ticket affected "
            "by the proposed action."
        )
    )

    reason: str = Field(
        description="Evidence-based justification for the action."
    )

    status: ActionStatus = Field(
        description="Current lifecycle status of the action."
    )

    requested_by: str = Field(
        description="Agent or user that proposed the action."
    )

    created_at: datetime = Field(
        description="Timestamp at which the action was proposed."
    )

    approved_by: str | None = Field(
        default=None,
        description="Human reviewer who approved the action.",
    )

    approval_note: str | None = Field(
        default=None,
        description="Reviewer explanation for approval or rejection.",
    )

    decided_at: datetime | None = Field(
        default=None,
        description="Timestamp of the human decision.",
    )

    executed_at: datetime | None = Field(
        default=None,
        description="Timestamp at which the action was executed.",
    )

    execution_result: str | None = Field(
        default=None,
        description="Result returned by the execution layer.",
    )


class ApprovalDecision(BaseModel):
    action_id: str
    approved: bool
    reviewer: str
    note: str | None = None


class ActionExecutionOutcome(BaseModel):
    action_id: str
    status: ActionStatus
    execution_result: str
    executed_at: datetime