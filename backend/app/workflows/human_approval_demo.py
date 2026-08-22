import asyncio

from agents import Agent, Runner
from dotenv import load_dotenv

from app.integrations.execution_tools import (
    execute_settlement_escalation,
)
from app.workflows.action_models import (
    ActionType,
    ApprovalDecision,
)
from app.workflows.action_store import (
    create_proposed_action,
    decide_action,
    get_action,
)


load_dotenv()


EXECUTOR_INSTRUCTIONS = """
You are the PayFlux controlled action executor.

Call execute_settlement_escalation exactly once using the supplied
action ID.

Never claim that an action was executed until the execution tool
returns a successful result.

If the tool call is rejected by the human reviewer, acknowledge the
rejection and do not attempt to call the tool again.
"""


execution_agent = Agent(
    name="PayFlux Controlled Action Executor",
    instructions=EXECUTOR_INSTRUCTIONS,
    tools=[execute_settlement_escalation],
)


async def main() -> None:
    action = create_proposed_action(
        ticket_id="TKT0001",
        action_type=ActionType.ESCALATE_SETTLEMENT,
        target_id="STL0001",
        reason=(
            "Settlement STL0001 is delayed, remains unsettled, "
            "and requires settlement-operations review."
        ),
    )

    print("\nPROPOSED ACTION:\n")
    print(action.model_dump_json(indent=2))

    result = await Runner.run(
        execution_agent,
        (
            "Execute the proposed settlement escalation using "
            f"action ID {action.action_id}."
        ),
    )

    print("\nSDK APPROVAL INTERRUPTIONS:")
    print(len(result.interruptions))

    if not result.interruptions:
        raise RuntimeError(
            "Expected the execution tool to pause for approval."
        )

    stored_before_decision = get_action(action.action_id)

    print("\nSTATUS BEFORE HUMAN DECISION:")
    print(stored_before_decision.status.value)

    while True:
        reviewer_input = input(
            "\nApprove this dummy escalation? Type y or n: "
        ).strip().lower()

        if reviewer_input in {"y", "n"}:
            break

        print("Please enter only y or n.")

    approved = reviewer_input == "y"

    decided_action = decide_action(
        ApprovalDecision(
            action_id=action.action_id,
            approved=approved,
            reviewer="local_demo_reviewer",
            note=(
                "Approved during local human-in-the-loop demo."
                if approved
                else "Rejected during local human-in-the-loop demo."
            ),
        )
    )

    state = result.to_state()

    for interruption in result.interruptions:
        if approved:
            state.approve(interruption)
        else:
            state.reject(interruption)

    resumed_result = await Runner.run(
        execution_agent,
        state,
    )

    final_action = get_action(action.action_id)

    print("\nAGENT RESPONSE AFTER HUMAN DECISION:\n")
    print(resumed_result.final_output)

    print("\nFINAL STORED ACTION:\n")
    print(final_action.model_dump_json(indent=2))

    if approved:
        expected_status = "executed"
    else:
        expected_status = "rejected"

    print("\nEXPECTED FINAL STATUS:")
    print(expected_status)


if __name__ == "__main__":
    asyncio.run(main())