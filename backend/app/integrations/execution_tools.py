from agents import function_tool

from app.workflows.action_models import (
    ActionExecutionOutcome,
    ActionStatus,
    ActionType,
)
from app.workflows.action_store import (
    get_action,
    record_execution,
)


def execute_settlement_escalation_action(
    action_id: str,
) -> ActionExecutionOutcome:
    """
    Execute a database-approved settlement escalation.

    This trusted application function is shared by the FastAPI
    layer and the Agents SDK tool wrapper.
    """

    action = get_action(action_id)

    if action is None:
        raise ValueError(
            f"Action {action_id} does not exist."
        )

    if action.action_type != ActionType.ESCALATE_SETTLEMENT:
        raise ValueError(
            "This executor only supports settlement escalations."
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

    return record_execution(
        action_id=action.action_id,
        execution_result=execution_message,
        succeeded=True,
    )


@function_tool(needs_approval=True)
def execute_settlement_escalation(
    action_id: str,
) -> str:
    """
    Execute an approved settlement escalation.

    The Agents SDK pauses this tool call for human review before
    invoking the trusted application execution function.
    """

    outcome = execute_settlement_escalation_action(
        action_id
    )

    return outcome.model_dump_json(indent=2)