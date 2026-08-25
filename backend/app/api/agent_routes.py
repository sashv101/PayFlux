from fastapi import APIRouter, HTTPException, status

from app.api.agent_schemas import ActionDecisionRequest
from app.integrations.execution_tools import (
    execute_settlement_escalation_action,
)
from app.workflows.action_models import (
    ActionExecutionOutcome,
    ActionStatus,
    ActionType,
    ApprovalDecision,
    ProposedAction,
)
from app.workflows.action_store import (
    decide_action,
    get_action,
    list_actions,
)
from app.workflows.investigate_and_prepare import (
    InvestigateAndPrepareResult,
    investigate_and_prepare_action,
)


router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


@router.post(
    "/investigate/{ticket_id}",
    response_model=InvestigateAndPrepareResult,
)
async def investigate_ticket(
    ticket_id: str,
) -> InvestigateAndPrepareResult:
    try:
        return await investigate_and_prepare_action(ticket_id)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        ) from error


@router.get(
    "/actions",
    response_model=list[ProposedAction],
)
def get_actions(
    action_status: ActionStatus | None = None,
) -> list[ProposedAction]:
    return list_actions(status=action_status)


@router.get(
    "/actions/{action_id}",
    response_model=ProposedAction,
)
def get_action_by_id(
    action_id: str,
) -> ProposedAction:
    action = get_action(action_id)

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} does not exist.",
        )

    return action


@router.post(
    "/actions/{action_id}/decision",
    response_model=ProposedAction,
)
def submit_action_decision(
    action_id: str,
    request: ActionDecisionRequest,
) -> ProposedAction:
    try:
        return decide_action(
            ApprovalDecision(
                action_id=action_id,
                approved=request.approved,
                reviewer=request.reviewer,
                note=request.note,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error


@router.post(
    "/actions/{action_id}/execute",
    response_model=ActionExecutionOutcome,
)
def execute_action(
    action_id: str,
) -> ActionExecutionOutcome:
    action = get_action(action_id)

    if action is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Action {action_id} does not exist.",
        )

    if action.action_type != ActionType.ESCALATE_SETTLEMENT:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=(
                "Execution is not implemented for action type "
                f"{action.action_type.value}."
            ),
        )

    try:
        return execute_settlement_escalation_action(
            action_id
        )

    except PermissionError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        ) from error

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error