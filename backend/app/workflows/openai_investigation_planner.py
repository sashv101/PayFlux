import asyncio
import sys

from agents import Agent, Runner
from dotenv import load_dotenv

from app.integrations.openai_tools import lookup_ticket_tool
from app.workflows.investigation_plan import InvestigationPlan


PLANNER_INSTRUCTIONS = """
You are the PayFlux investigation planning agent.

Your job is to create an evidence-gathering plan for a support ticket.
You plan the investigation but do not perform the full investigation.

RULES:

1. Always call lookup_ticket_tool exactly once before creating the plan.
2. Even though you call lookup_ticket_tool while creating the plan,
   include lookup_ticket_tool as Step 1 in the returned plan.
   The returned plan must be standalone for a separate executor.
3. Use the returned ticket record to determine which evidence is relevant.
4. Include lookup_merchant_tool in every plan.
5. Include lookup_payment_tool only when the ticket contains a payment_id.
6. Include lookup_settlement_tool only when the ticket contains a settlement_id.
7. Include retrieve_policy_tool in every plan.
8. End with an assessment step whose tool is null.
9. Do not invent payment IDs, settlement IDs, merchants, policies, or evidence.
10. Do not claim that any operational action has been executed.
11. Number plan steps sequentially, starting from 1.
11. For every valid ticket, the first returned PlanStep must have:
- step_number: 1
- tool: lookup_ticket_tool
- condition: always

The plan should normally follow this order:

- Retrieve the ticket.
- Retrieve the associated merchant.
- Retrieve the linked payment or settlement when present.
- Retrieve the relevant policy.
- Assess the evidence and recommend the next action.
"""

load_dotenv()


planner_agent = Agent(
    name="PayFlux Investigation Planner",
    instructions=PLANNER_INSTRUCTIONS,
    tools=[lookup_ticket_tool],
    output_type=InvestigationPlan,
)


async def generate_investigation_plan(
    ticket_id: str,
) -> InvestigationPlan:
    result = await Runner.run(
        planner_agent,
        (
            f"Create an investigation plan for ticket {ticket_id}. "
            "First retrieve the ticket record."
        ),
    )

    return result.final_output


async def main() -> None:
    ticket_id = sys.argv[1] if len(sys.argv) > 1 else "TKT0001"

    plan = await generate_investigation_plan(ticket_id)

    print("\nINVESTIGATION PLAN:\n")
    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())