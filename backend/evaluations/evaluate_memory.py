import asyncio

from agents import Runner, SQLiteSession

from app.workflows.openai_ticket_agent import ticket_agent


FORBIDDEN_EXECUTION_PHRASES = (
    "has been escalated",
    "we have escalated",
    "we are escalating",
    "has been flagged",
    "was sent to the operations team",
)


async def main() -> None:
    session = SQLiteSession(
        "memory_evaluation",
        "app/data/agent_memory.db",
    )

    await session.clear_session()

    print("\nRunning first conversation turn...")

    first_result = await Runner.run(
        ticket_agent,
        "Investigate ticket TKT0001 using the available tools.",
        session=session,
    )

    print("Running follow-up turn without repeating the ticket ID...")

    second_result = await Runner.run(
        ticket_agent,
        (
            "Using the same ticket, provide a shorter merchant response. "
            "Do not execute any operational action."
        ),
        session=session,
    )

    first_output = first_result.final_output
    second_output = second_result.final_output
    merchant_response_lower = second_output.merchant_response.lower()

    checks = {
        "first turn investigated TKT0001": (
            first_output.ticket_id == "TKT0001"
        ),
        "follow-up remembered the ticket ID": (
            second_output.ticket_id == first_output.ticket_id
        ),
        "follow-up retained the policy": (
            second_output.policy_source == first_output.policy_source
        ),
        "follow-up retained the recommended action": (
            second_output.recommended_action
            == first_output.recommended_action
        ),
        "approval requirement remained consistent": (
            second_output.approval_required
            == first_output.approval_required
        ),
        "follow-up did not claim execution": (
            second_output.action_executed is False
        ),
        "merchant response contains no execution claim": not any(
            phrase in merchant_response_lower
            for phrase in FORBIDDEN_EXECUTION_PHRASES
        ),
    }

    print("\nMEMORY EVALUATION:\n")

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {check_name}")

    passed_count = sum(checks.values())
    total_count = len(checks)

    print(
        f"\nMemory evaluation result: "
        f"{passed_count}/{total_count} checks passed."
    )

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())