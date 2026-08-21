import asyncio
from collections import Counter

from agents.items import ToolCallItem

from app.workflows.openai_ticket_agent import investigate_ticket


EVALUATION_CASES = [
    {
        "ticket_id": "TKT0001",
        "expected_action": "escalate_settlement",
        "expected_approval_required": True,

        "expected_tools": {
            "lookup_ticket_tool",
            "lookup_merchant_tool",
            "lookup_settlement_tool",
            "retrieve_policy_tool",
        },
        "forbidden_tools": {
            "lookup_payment_tool",
        },
        "expected_output_terms": {
            "STL0001",
            "delayed",
            "settlement_policy.md",
        },
        "forbidden_output_terms": {
            "successfully escalated",
            "escalation completed",
            "action was executed",
        },


    },
    {
        "ticket_id": "TKT0002",

        "expected_action": "explain_payment_failure",
        "expected_approval_required": False,
        
        "expected_tools": {
            "lookup_ticket_tool",
            "lookup_merchant_tool",
            "lookup_payment_tool",
            "retrieve_policy_tool",
        },
        "forbidden_tools": {
            "lookup_settlement_tool",
        },
        "expected_output_terms": {
            "PAY0003",
            "bank_declined",
            "payment_failure_policy.md",
        },
        "forbidden_output_terms": {
            "successfully escalated",
            "escalation completed",
            "action was executed",
        },
    },
]


def extract_tool_names(result) -> list[str]:
    """
    Extract model-selected tool names from an agent run.
    """

    return [
        item.tool_name
        for item in result.new_items
        if isinstance(item, ToolCallItem)
        and item.tool_name is not None
    ]


async def evaluate_case(case: dict) -> bool:
    """
    Evaluate tool selection and final-output behaviour for one ticket.
    """

    ticket_id = case["ticket_id"]

    print(f"\nEvaluating {ticket_id}...")

    result = await investigate_ticket(ticket_id)

    tool_names = extract_tool_names(result)
    tool_counts = Counter(tool_names)

    expected_tools = case["expected_tools"]
    forbidden_tools = case["forbidden_tools"]
    expected_output_terms = case["expected_output_terms"]
    forbidden_output_terms = case["forbidden_output_terms"]

    structured_output = result.final_output
    final_output = structured_output.model_dump_json()
    final_output_lower = final_output.lower()

    missing_output_terms = {
        term
        for term in expected_output_terms
        if term.lower() not in final_output_lower
    }

    detected_forbidden_terms = {
        term
        for term in forbidden_output_terms
        if term.lower() in final_output_lower
    }

    checks = {

        "ticket ID matches": (
            structured_output.ticket_id == case["ticket_id"]
        ),
        "issue was verified": (
            structured_output.issue_verified is True
        ),
        "recommended action is correct": (
            structured_output.recommended_action.value
            == case["expected_action"]
        ),
        "approval requirement is correct": (
            structured_output.approval_required
            is case["expected_approval_required"]
        ),
        "action was not falsely executed": (
            structured_output.action_executed is False
        ),

        "ticket lookup was first": (
            len(tool_names) > 0
            and tool_names[0] == "lookup_ticket_tool"
        ),
        "all required tools were called": (
            expected_tools.issubset(set(tool_names))
        ),
        "no forbidden tools were called": (
            forbidden_tools.isdisjoint(set(tool_names))
        ),
        "each required tool was called once": all(
            tool_counts[tool_name] == 1
            for tool_name in expected_tools
        ),
        "expected evidence appears in output": (
            len(missing_output_terms) == 0
        ),
        "no unsupported execution was claimed": (
            len(detected_forbidden_terms) == 0
        ),
    }

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {status}: {check_name}")

    print(f"  Tool path: {' -> '.join(tool_names)}")

    if missing_output_terms:
        print(
            "  Missing output terms: "
            + ", ".join(sorted(missing_output_terms))
        )

    if detected_forbidden_terms:
        print(
            "  Forbidden output terms detected: "
            + ", ".join(sorted(detected_forbidden_terms))
        )

    return all(checks.values())


async def main() -> None:
    """
    Run all live PayFlux agent-path evaluation cases.
    """

    results = []

    for case in EVALUATION_CASES:
        passed = await evaluate_case(case)
        results.append(passed)

    passed_count = sum(results)
    total_count = len(results)

    print(
        f"\nEvaluation result: "
        f"{passed_count}/{total_count} cases passed."
    )

    if not all(results):
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())