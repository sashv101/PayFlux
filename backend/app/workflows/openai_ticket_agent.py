import sys
import asyncio
import os

from agents import Agent, Runner
from agents.items import ToolCallItem, ToolCallOutputItem
from dotenv import load_dotenv
from app.workflows.investigation_result import InvestigationResult

from app.integrations.openai_tools import (
    lookup_merchant_tool,
    lookup_payment_tool,
    lookup_settlement_tool,
    lookup_ticket_tool,
    retrieve_policy_tool,
)


load_dotenv()


MODEL_NAME = os.getenv(
    "OPENAI_MODEL",
    "gpt-5.4-mini",
)


ticket_agent = Agent(
    name="PayFlux Ticket Investigator",
    model=MODEL_NAME,
    instructions="""
You investigate synthetic PayFlux merchant-support tickets.

Investigation process:
1. Always begin by calling lookup_ticket_tool with the supplied ticket ID.
2. Use the returned merchant ID to call lookup_merchant_tool.
3. If the ticket contains a payment ID, call lookup_payment_tool.
4. If the ticket contains a settlement ID, call lookup_settlement_tool.
5. Call retrieve_policy_tool using the ticket category.
6. Use only evidence returned by these tools.

Tool discipline:
- Do not call a payment tool when no payment ID is present.
- Do not call a settlement tool when no settlement ID is present.
- Do not invent missing identifiers, statuses, dates or policies.
- Do not treat the merchant's description as verified operational evidence.
- Do not expose or reference an expected resolution or answer key.
- Do not claim to have executed an escalation or changed any record.

Final-response format:
## Verified facts
List the relevant facts returned by the tools.

## Applicable policy
Summarize the retrieved policy and name its source file.

## Assessment
Explain whether the merchant's complaint is supported by operational evidence.

## Recommended action
State the next permitted support action.

## Approval or execution status
Clearly state that the recommendation has not yet been executed.

APPROVAL AND EXECUTION RULES:

- Set approval_required to true when recommended_action is
  escalate_settlement or route_compliance_review.
- Set approval_required to false for all other recommended actions.
- Set action_executed to false because this agent currently has no
  tools that can execute or approve an operational action.
- Never claim that an escalation, compliance review, refund, retry,
  or other operational action has already been completed.
- The merchant_response may say that escalation is recommended or
  pending approval, but must not say that it has already been executed.
""",
    tools=[
        lookup_ticket_tool,
        lookup_merchant_tool,
        lookup_payment_tool,
        lookup_settlement_tool,
        retrieve_policy_tool,
    ],
     output_type=InvestigationResult,
)

def get_raw_field(raw_item, field_name: str):
    """
    Safely read a field from either an SDK object or dictionary.
    """

    if isinstance(raw_item, dict):
        return raw_item.get(field_name)

    return getattr(raw_item, field_name, None)


def display_tool_trace(result) -> None:
    """
    Print model-selected tool calls and their returned outputs.
    """

    print("\nTOOL EXECUTION TRACE:\n")

    step_number = 1

    for item in result.new_items:
        if isinstance(item, ToolCallItem):
            arguments = get_raw_field(
                item.raw_item,
                "arguments",
            )

            print(
                f"{step_number}. CALL "
                f"{item.tool_name} "
                f"with {arguments}"
            )

            step_number += 1

        elif isinstance(item, ToolCallOutputItem):
            compact_output = str(item.output).replace(
                "\n",
                " ",
            )

            if len(compact_output) > 180:
                compact_output = (
                    compact_output[:180] + "..."
                )

            print(
                f"   OUTPUT: {compact_output}"
            )

async def investigate_ticket(ticket_id: str):
    """
    Run a complete PayFlux investigation for one ticket.
    """

    return await Runner.run(
        ticket_agent,
        (
            f"Investigate support ticket {ticket_id}. "
            "Use the available tools to verify the issue and recommend "
            "the correct next action."
        ),
    )


async def main() -> None:
    ticket_id = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "TKT0001"
    )

    result = await investigate_ticket(ticket_id)

    display_tool_trace(result)

    print("\nFINAL AGENT OUTPUT:\n")

    structured_output = result.final_output
    final_output = structured_output.model_dump_json()
    print(final_output.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())