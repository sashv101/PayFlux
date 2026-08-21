import asyncio

from app.workflows.openai_investigation_planner import (
    generate_investigation_plan,
)


EVALUATION_CASES = [
    {
        "ticket_id": "TKT0001",
        "expected_tools": [
            "lookup_ticket_tool",
            "lookup_merchant_tool",
            "lookup_settlement_tool",
            "retrieve_policy_tool",
            None,
        ],
    },
    {
        "ticket_id": "TKT0002",
        "expected_tools": [
            "lookup_ticket_tool",
            "lookup_merchant_tool",
            "lookup_payment_tool",
            "retrieve_policy_tool",
            None,
        ],
    },
]


async def evaluate_case(case: dict) -> bool:
    ticket_id = case["ticket_id"]

    print(f"\nEvaluating plan for {ticket_id}...")

    plan = await generate_investigation_plan(ticket_id)

    actual_tools = [
        step.tool.value if step.tool is not None else None
        for step in plan.steps
    ]

    actual_step_numbers = [
        step.step_number for step in plan.steps
    ]

    expected_step_numbers = list(
        range(1, len(plan.steps) + 1)
    )

    checks = {
        "ticket ID matches": (
            plan.ticket_id == ticket_id
        ),
        "tool plan matches expected path": (
            actual_tools == case["expected_tools"]
        ),
        "steps are numbered sequentially": (
            actual_step_numbers == expected_step_numbers
        ),
        "final step is an assessment": (
            plan.steps[-1].tool is None
        ),
        "all plan conditions are explicit": all(
            bool(step.condition.strip())
            for step in plan.steps
        ),
        "success criteria are present": (
            len(plan.success_criteria) > 0
        ),
    }

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {check_name}")

    print(
        "Planned path: "
        + " -> ".join(
            tool_name if tool_name is not None else "assessment"
            for tool_name in actual_tools
        )
    )

    return all(checks.values())


async def main() -> None:
    results = []

    for case in EVALUATION_CASES:
        passed = await evaluate_case(case)
        results.append(passed)

    passed_count = sum(results)
    total_count = len(results)

    print(
        f"\nPlanner evaluation result: "
        f"{passed_count}/{total_count} cases passed."
    )

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())