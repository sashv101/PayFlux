from enum import Enum

from pydantic import BaseModel, Field


class PlannedTool(str, Enum):
    LOOKUP_TICKET = "lookup_ticket_tool"
    LOOKUP_MERCHANT = "lookup_merchant_tool"
    LOOKUP_PAYMENT = "lookup_payment_tool"
    LOOKUP_SETTLEMENT = "lookup_settlement_tool"
    RETRIEVE_POLICY = "retrieve_policy_tool"


class PlanStep(BaseModel):
    step_number: int = Field(
        description="Execution order of this step, starting from 1."
    )

    objective: str = Field(
        description="What this step is intended to establish."
    )

    tool: PlannedTool | None = Field(
        description=(
            "Tool required for this step, or null when the step only "
            "assesses already retrieved evidence."
        )
    )

    condition: str = Field(
        description=(
            "Condition under which this step should run. "
            "Use 'always' when it is unconditional."
        )
    )


class InvestigationPlan(BaseModel):
    ticket_id: str = Field(
        description="Ticket that will be investigated."
    )

    investigation_goal: str = Field(
        description="The overall objective of the investigation."
    )

    steps: list[PlanStep] = Field(
        description="Ordered and evidence-focused investigation steps."
    )

    success_criteria: list[str] = Field(
        description=(
            "Conditions that must be satisfied before producing "
            "a final recommendation."
        )
    )