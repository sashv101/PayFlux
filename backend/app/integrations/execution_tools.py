from agents import function_tool

from app.workflows.action_models import (
    ActionStatus,
    ActionType,
)
from app.workflows.action_store import (
    get_action,
    record_execution,
)


@function_tool(needs_approval=True)
def execute_settlement_escalation(
    action_id: str,
) -> str:
    """
    Execute an approved settlement escalation.

    The action must already exist in the PayFlux action store,
    must represent a settlement escalation, and must have received
    explicit human approval.
    """

    action = get_action(action_id)

    if action is None:
        raise ValueError(
            f"Action {action_id} does not exist."
        )

    if action.action_type != ActionType.ESCALATE_SETTLEMENT:
        raise ValueError(
            "This tool only executes settlement escalations."
        )

    if action.status != ActionStatus.APPROVED:
        raise PermissionError(
            "Settlement escalation requires human approval."
        )

    execution_message = (
        "Dummy settlement escalation created successfully for "
        f"settlement {action.target_id} from ticket "
        f"{action.ticket_id}."
    )

    outcome = record_execution(
        action_id=action.action_id,
        execution_result=execution_message,
        succeeded=True,
    )

    return outcome.model_dump_json(indent=2)