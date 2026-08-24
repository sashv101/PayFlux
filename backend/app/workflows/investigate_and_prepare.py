import asyncio
import sys

from pydantic import BaseModel

from app.workflows.action_preparation import (
    ActionPreparationResult,
    prepare_action_from_investigation,
)
from app.workflows.planned_ticket_workflow import (
    PlannedInvestigationRun,
    run_planned_investigation,
)


class InvestigateAndPrepareResult(BaseModel):
    planned_investigation: PlannedInvestigationRun
    action_preparation: ActionPreparationResult


async def investigate_and_prepare_action(
    ticket_id: str,
) -> InvestigateAndPrepareResult:
    planned_investigation = (
        await run_planned_investigation(ticket_id)
    )

    if not planned_investigation.plan_followed:
        raise RuntimeError(
            "Investigation did not follow the approved evidence plan."
        )

    action_preparation = prepare_action_from_investigation(
        planned_investigation.investigation_result
    )

    return InvestigateAndPrepareResult(
        planned_investigation=planned_investigation,
        action_preparation=action_preparation,
    )


def print_result(
    result: InvestigateAndPrepareResult,
) -> None:
    investigation = (
        result.planned_investigation.investigation_result
    )

    print("\nPLAN ADHERENCE:")
    print(
        "PASS"
        if result.planned_investigation.plan_followed
        else "FAIL"
    )

    print("\nINVESTIGATION RESULT:\n")
    print(investigation.model_dump_json(indent=2))

    print("\nACTION PREPARATION:")

    print(
        result.action_preparation.preparation_message
    )

    if result.action_preparation.proposed_action is None:
        print("No action record was created.")
    else:
        print(
            result.action_preparation.proposed_action.model_dump_json(
                indent=2
            )
        )


async def main() -> None:
    ticket_id = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "TKT0001"
    )

    print(
        f"\nInvestigating and preparing action for "
        f"{ticket_id}..."
    )

    result = await investigate_and_prepare_action(ticket_id)
    print_result(result)


if __name__ == "__main__":
    asyncio.run(main())