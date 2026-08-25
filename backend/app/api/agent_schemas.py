from pydantic import BaseModel, ConfigDict, Field


class ActionDecisionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "approved": True,
                "reviewer": "operations_reviewer",
                "note": (
                    "Verified the evidence and approved "
                    "the proposed action."
                ),
            }
        }
    )

    approved: bool = Field(
        description=(
            "True to approve the action or false to reject it."
        )
    )

    reviewer: str = Field(
        min_length=1,
        description="Identity of the human reviewer.",
    )

    note: str | None = Field(
        default=None,
        description="Optional explanation for the decision.",
    )