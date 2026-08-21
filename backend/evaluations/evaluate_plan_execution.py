import asyncio

from app.workflows.planned_ticket_workflow import (
    run_planned_investigation,
)


EVALUATION_CASES = [
    {
        "ticket_id": "TKT0001",
        "expected_tools": [
            "lookup_ticket_tool",
            "lookup_merchant_tool",
            "lookup_settlement_tool",
            "retrieve_policy_tool",
        ],
        "expected_action": "escalate_settlement",
        "expected_approval_required": True,
    },
    {
        "ticket_id": "TKT0002",
        "expected_tools": [
            "lookup_ticket_tool",
            "lookup_merchant_tool",
            "lookup_payment_tool",
            "retrieve_policy_tool",
        ],
        "expected_action": "explain_payment_failure",
        "expected_approval_required": False,
    },
]


async def evaluate_case(case: dict) -> bool:
    ticket_id = case["ticket_id"]

    print(f"\nEvaluating planned execution for {ticket_id}...")

    workflow_result = await run_planned_investigation(ticket_id)
    investigation = workflow_result.investigation_result

    checks = {
        "planned tools match expected path": (
            workflow_result.planned_tools
            == case["expected_tools"]
        ),
        "actual tools match expected path": (
            workflow_result.actual_tools
            == case["expected_tools"]
        ),
        "execution followed the plan": (
            workflow_result.plan_followed is True
        ),
        "result belongs to the correct ticket": (
            investigation.ticket_id == ticket_id
        ),
        "recommended action is correct": (
            investigation.recommended_action.value
            == case["expected_action"]
        ),
        "approval requirement is correct": (
            investigation.approval_required
            is case["expected_approval_required"]
        ),
        "no operational action was executed": (
            investigation.action_executed is False
        ),
    }

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {check_name}")

    print(
        "Planned path: "
        + " -> ".join(workflow_result.planned_tools)
    )

    print(
        "Actual path:  "
        + " -> ".join(workflow_result.actual_tools)
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
        f"\nPlan-execution evaluation result: "
        f"{passed_count}/{total_count} cases passed."
    )

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())