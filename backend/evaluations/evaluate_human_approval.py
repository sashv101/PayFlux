import asyncio

from agents import Runner

from app.workflows.action_models import (
    ActionStatus,
    ActionType,
    ApprovalDecision,
)
from app.workflows.action_store import (
    create_proposed_action,
    decide_action,
    get_action,
    get_connection,
)
from app.workflows.human_approval_demo import execution_agent


async def run_decision_case(
    approved: bool,
    created_action_ids: list[str],
):
    action = create_proposed_action(
        ticket_id="TKT0001",
        action_type=ActionType.ESCALATE_SETTLEMENT,
        target_id="STL0001",
        reason=(
            "Settlement STL0001 is delayed and requires "
            "human-reviewed escalation."
        ),
        requested_by="approval_evaluation",
    )
    created_action_ids.append(action.action_id)

    initial_result = await Runner.run(
        execution_agent,
        (
            "Execute the settlement escalation using "
            f"action ID {action.action_id}."
        ),
    )

    stored_before_decision = get_action(action.action_id)

    if not initial_result.interruptions:
        raise RuntimeError(
            "Execution did not pause for human approval."
        )

    decided_action = decide_action(
        ApprovalDecision(
            action_id=action.action_id,
            approved=approved,
            reviewer="evaluation_reviewer",
            note=(
                "Approved by automated approval-flow evaluation."
                if approved
                else "Rejected by automated approval-flow evaluation."
            ),
        )
    )

    state = initial_result.to_state()

    for interruption in initial_result.interruptions:
        if approved:
            state.approve(interruption)
        else:
            state.reject(interruption)

    resumed_result = await Runner.run(
        execution_agent,
        state,
    )

    final_action = get_action(action.action_id)

    return {
        "initial_result": initial_result,
        "stored_before_decision": stored_before_decision,
        "decided_action": decided_action,
        "resumed_result": resumed_result,
        "final_action": final_action,
    }


async def main() -> None:
    created_action_ids: list[str] = []

    try:
        approved_case = await run_decision_case(
            approved=True,
            created_action_ids=created_action_ids,
        )

        rejected_case = await run_decision_case(
            approved=False,
            created_action_ids=created_action_ids,
        )

        approved_final = approved_case["final_action"]
        rejected_final = rejected_case["final_action"]

        checks = {
            "approved case paused before execution": (
                len(
                    approved_case[
                        "initial_result"
                    ].interruptions
                )
                == 1
            ),
            "approved case was initially pending": (
                approved_case[
                    "stored_before_decision"
                ].status
                == ActionStatus.PENDING_APPROVAL
            ),
            "approved action executed": (
                approved_final.status
                == ActionStatus.EXECUTED
            ),
            "approved action records reviewer": (
                approved_final.approved_by
                == "evaluation_reviewer"
            ),
            "approved action records execution result": (
                approved_final.execution_result is not None
            ),
            "rejected case paused before execution": (
                len(
                    rejected_case[
                        "initial_result"
                    ].interruptions
                )
                == 1
            ),
            "rejected action remains rejected": (
                rejected_final.status
                == ActionStatus.REJECTED
            ),
            "rejected action has no execution time": (
                rejected_final.executed_at is None
            ),
            "rejected action has no execution result": (
                rejected_final.execution_result is None
            ),
            "rejected call was not requested again": (
                len(
                    rejected_case[
                        "resumed_result"
                    ].interruptions
                )
                == 0
            ),
        }

        print("\nHUMAN APPROVAL EVALUATION:\n")

        for check_name, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"{status}: {check_name}")

        passed_count = sum(checks.values())
        total_count = len(checks)

        print(
            f"\nHuman approval result: "
            f"{passed_count}/{total_count} checks passed."
        )

        if passed_count != total_count:
            raise SystemExit(1)

    finally:
        if created_action_ids:
            placeholders = ", ".join(
                "?" for _ in created_action_ids
            )

            with get_connection() as connection:
                connection.execute(
                    f"""
                    DELETE FROM agent_actions
                    WHERE action_id IN ({placeholders})
                    """,
                    created_action_ids,
                )
                connection.commit()


if __name__ == "__main__":
    asyncio.run(main())