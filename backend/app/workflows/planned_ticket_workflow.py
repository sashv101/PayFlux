import asyncio
import sys

from agents import Runner
from pydantic import BaseModel

from app.workflows.investigation_plan import InvestigationPlan
from app.workflows.investigation_result import InvestigationResult
from app.workflows.openai_investigation_planner import (
    generate_investigation_plan,
)
from app.workflows.openai_ticket_agent import ticket_agent


class PlannedInvestigationRun(BaseModel):
    plan: InvestigationPlan
    planned_tools: list[str]
    actual_tools: list[str]
    plan_followed: bool
    investigation_result: InvestigationResult


def extract_tool_names(run_items: list) -> list[str]:
    tool_names = []

    for item in run_items:
        if getattr(item, "type", None) != "tool_call_item":
            continue

        raw_item = getattr(item, "raw_item", None)
        tool_name = getattr(raw_item, "name", None)

        if tool_name:
            tool_names.append(tool_name)

    return tool_names


async def run_planned_investigation(
    ticket_id: str,
) -> PlannedInvestigationRun:
    plan = await generate_investigation_plan(ticket_id)

    planned_tools = [
        step.tool.value
        for step in plan.steps
        if step.tool is not None
    ]

    execution_prompt = f"""
Investigate ticket {ticket_id}.

Follow this evidence-gathering plan:

{plan.model_dump_json(indent=2)}

Use the appropriate tools to verify every required fact.
The plan authorizes evidence retrieval only.
It does not authorize any operational action.
Return the final structured InvestigationResult.
"""

    result = await Runner.run(
        ticket_agent,
        execution_prompt,
    )

    actual_tools = extract_tool_names(result.new_items)

    return PlannedInvestigationRun(
        plan=plan,
        planned_tools=planned_tools,
        actual_tools=actual_tools,
        plan_followed=(actual_tools == planned_tools),
        investigation_result=result.final_output,
    )


def print_workflow_result(
    workflow_result: PlannedInvestigationRun,
) -> None:
    print("\nINVESTIGATION PLAN:\n")
    print(workflow_result.plan.model_dump_json(indent=2))

    print("\nPLANNED TOOL PATH:")

    for index, tool_name in enumerate(
        workflow_result.planned_tools,
        start=1,
    ):
        print(f"{index}. {tool_name}")

    print("\nACTUAL TOOL PATH:")

    for index, tool_name in enumerate(
        workflow_result.actual_tools,
        start=1,
    ):
        print(f"{index}. {tool_name}")

    print("\nPLAN ADHERENCE:")
    print("PASS" if workflow_result.plan_followed else "FAIL")

    print("\nFINAL INVESTIGATION RESULT:\n")
    print(
        workflow_result.investigation_result.model_dump_json(
            indent=2
        )
    )


async def main() -> None:
    ticket_id = sys.argv[1] if len(sys.argv) > 1 else "TKT0001"

    print(f"\nRunning planned investigation for {ticket_id}...")

    workflow_result = await run_planned_investigation(ticket_id)
    print_workflow_result(workflow_result)


if __name__ == "__main__":
    asyncio.run(main())