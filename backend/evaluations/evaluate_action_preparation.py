import asyncio

from app.workflows.action_models import (
    ActionStatus,
    ActionType,
)
from app.workflows.action_preparation import (
    prepare_action_from_investigation,
)
from app.workflows.investigate_and_prepare import (
    investigate_and_prepare_action,
)


async def main() -> None:
    settlement_case = await investigate_and_prepare_action(
        "TKT0001"
    )

    settlement_investigation = (
        settlement_case
        .planned_investigation
        .investigation_result
    )

    settlement_preparation = (
        settlement_case.action_preparation
    )

    settlement_action = (
        settlement_preparation.proposed_action
    )

    repeated_preparation = prepare_action_from_investigation(
        settlement_investigation
    )

    payment_case = await investigate_and_prepare_action(
        "TKT0002"
    )

    payment_investigation = (
        payment_case
        .planned_investigation
        .investigation_result
    )

    payment_preparation = (
        payment_case.action_preparation
    )

    active_statuses = {
        ActionStatus.PENDING_APPROVAL,
        ActionStatus.APPROVED,
        ActionStatus.EXECUTED,
    }

    checks = {
        "settlement plan was followed": (
            settlement_case
            .planned_investigation
            .plan_followed
            is True
        ),
        "settlement requires approval": (
            settlement_investigation
            .approval_required
            is True
        ),
        "settlement action was prepared": (
            settlement_action is not None
        ),
        "action type is settlement escalation": (
            settlement_action is not None
            and settlement_action.action_type
            == ActionType.ESCALATE_SETTLEMENT
        ),
        "action targets STL0001": (
            settlement_action is not None
            and settlement_action.target_id
            == "STL0001"
        ),
        "prepared action has a reusable status": (
            settlement_action is not None
            and settlement_action.status
            in active_statuses
        ),
        "repeated preparation reuses action": (
            repeated_preparation.action_created
            is False
        ),
        "repeated preparation keeps same action ID": (
            settlement_action is not None
            and repeated_preparation.proposed_action
            is not None
            and repeated_preparation
            .proposed_action
            .action_id
            == settlement_action.action_id
        ),
        "payment plan was followed": (
            payment_case
            .planned_investigation
            .plan_followed
            is True
        ),
        "payment explanation needs no approval": (
            payment_investigation
            .approval_required
            is False
        ),
        "payment case creates no action": (
            payment_preparation.proposed_action
            is None
            and payment_preparation.action_created
            is False
        ),
    }

    print("\nACTION PREPARATION EVALUATION:\n")

    for check_name, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        print(f"{status}: {check_name}")

    passed_count = sum(checks.values())
    total_count = len(checks)

    print(
        f"\nAction preparation result: "
        f"{passed_count}/{total_count} checks passed."
    )

    if passed_count != total_count:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())