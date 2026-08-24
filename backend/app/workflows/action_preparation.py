from pydantic import BaseModel

from app.workflows.action_models import (
    ActionType,
    ProposedAction,
)
from app.workflows.action_store import (
    create_proposed_action,
    find_reusable_action,
    get_connection,
)
from app.workflows.investigation_result import (
    InvestigationResult,
    RecommendedAction,
)


class ActionPreparationResult(BaseModel):
    investigation_result: InvestigationResult
    proposed_action: ProposedAction | None
    action_created: bool
    preparation_message: str


def get_ticket_targets(ticket_id: str) -> dict:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT
                merchant_id,
                payment_id,
                settlement_id
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

    if row is None:
        raise ValueError(
            f"Ticket {ticket_id} does not exist."
        )

    return dict(row)


def prepare_action_from_investigation(
    investigation: InvestigationResult,
) -> ActionPreparationResult:
    if investigation.action_executed:
        raise ValueError(
            "Investigation cannot arrive with action_executed=True."
        )

    if not investigation.approval_required:
        return ActionPreparationResult(
            investigation_result=investigation,
            proposed_action=None,
            action_created=False,
            preparation_message=(
                "No approval-controlled operational action is required."
            ),
        )

    ticket_targets = get_ticket_targets(
        investigation.ticket_id
    )

    if (
        investigation.recommended_action
        == RecommendedAction.ESCALATE_SETTLEMENT
    ):
        action_type = ActionType.ESCALATE_SETTLEMENT
        target_id = ticket_targets["settlement_id"]

    elif (
        investigation.recommended_action
        == RecommendedAction.ROUTE_COMPLIANCE_REVIEW
    ):
        action_type = ActionType.ROUTE_COMPLIANCE_REVIEW
        target_id = ticket_targets["merchant_id"]

    else:
        raise ValueError(
            "Approval was requested for an unsupported "
            f"action: {investigation.recommended_action.value}"
        )

    if not target_id:
        raise ValueError(
            "The recommended action has no valid target record."
        )

    existing_action = find_reusable_action(
        ticket_id=investigation.ticket_id,
        action_type=action_type,
        target_id=target_id,
    )

    if existing_action is not None:
        return ActionPreparationResult(
            investigation_result=investigation,
            proposed_action=existing_action,
            action_created=False,
            preparation_message=(
                "An existing action was reused to prevent duplication."
            ),
        )

    proposed_action = create_proposed_action(
        ticket_id=investigation.ticket_id,
        action_type=action_type,
        target_id=target_id,
        reason=investigation.assessment,
        requested_by="payflux_investigation_agent",
    )

    return ActionPreparationResult(
        investigation_result=investigation,
        proposed_action=proposed_action,
        action_created=True,
        preparation_message=(
            "A new action was created and is pending human approval."
        ),
    )