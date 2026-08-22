from app.workflows.action_models import (
    ActionStatus,
    ActionType,
    ApprovalDecision,
)
from app.workflows.action_store import (
    create_proposed_action,
    decide_action,
    get_action,
    get_connection,
    record_execution,
)


def main() -> None:
    created_action_ids: list[str] = []

    try:
        rejected_action = create_proposed_action(
            ticket_id="TKT0001",
            action_type=ActionType.ESCALATE_SETTLEMENT,
            target_id="STL0001",
            reason="Settlement is delayed and remains unsettled.",
        )
        created_action_ids.append(rejected_action.action_id)

        initial_rejected_action_status = rejected_action.status

        pending_execution_blocked = False

        try:
            record_execution(
                action_id=rejected_action.action_id,
                execution_result="This must not be recorded.",
                succeeded=True,
            )
        except ValueError:
            pending_execution_blocked = True

        rejected_action = decide_action(
            ApprovalDecision(
                action_id=rejected_action.action_id,
                approved=False,
                reviewer="test_reviewer",
                note="Rejecting this action for lifecycle evaluation.",
            )
        )

        rejected_execution_blocked = False

        try:
            record_execution(
                action_id=rejected_action.action_id,
                execution_result="This must not be recorded.",
                succeeded=True,
            )
        except ValueError:
            rejected_execution_blocked = True

        approved_action = create_proposed_action(
            ticket_id="TKT0001",
            action_type=ActionType.ESCALATE_SETTLEMENT,
            target_id="STL0001",
            reason="Settlement is delayed and requires escalation.",
        )
        created_action_ids.append(approved_action.action_id)

        approved_action = decide_action(
            ApprovalDecision(
                action_id=approved_action.action_id,
                approved=True,
                reviewer="test_reviewer",
                note="Approved for lifecycle evaluation.",
            )
        )

        second_decision_blocked = False

        try:
            decide_action(
                ApprovalDecision(
                    action_id=approved_action.action_id,
                    approved=False,
                    reviewer="second_reviewer",
                    note="This second decision must be rejected.",
                )
            )
        except ValueError:
            second_decision_blocked = True

        outcome = record_execution(
            action_id=approved_action.action_id,
            execution_result=(
                "Dummy settlement escalation created successfully."
            ),
            succeeded=True,
        )

        persisted_action = get_action(approved_action.action_id)

        checks = {
            "new action starts pending approval": (
                initial_rejected_action_status
                == ActionStatus.PENDING_APPROVAL
            ),
            "pending action cannot execute": (
                pending_execution_blocked
            ),
            "human rejection is persisted": (
                rejected_action.status
                == ActionStatus.REJECTED
            ),
            "rejected action cannot execute": (
                rejected_execution_blocked
            ),
            "human approval is persisted": (
                approved_action.status
                == ActionStatus.APPROVED
            ),
            "second approval decision is blocked": (
                second_decision_blocked
            ),
            "approved action can execute": (
                outcome.status == ActionStatus.EXECUTED
            ),
            "executed status is persisted": (
                persisted_action is not None
                and persisted_action.status
                == ActionStatus.EXECUTED
            ),
        }

        print("\nACTION LIFECYCLE EVALUATION:\n")

        for check_name, passed in checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"{status}: {check_name}")

        passed_count = sum(checks.values())
        total_count = len(checks)

        print(
            f"\nAction lifecycle result: "
            f"{passed_count}/{total_count} checks passed."
        )

        if passed_count != total_count:
            raise SystemExit(1)

    finally:
        if created_action_ids:
            placeholders = ", ".join(
                "?" for _ in created_action_ids
            )

            with get_connection() as connection:
                connection.execute(
                    f"""
                    DELETE FROM agent_actions
                    WHERE action_id IN ({placeholders})
                    """,
                    created_action_ids,
                )
                connection.commit()


if __name__ == "__main__":
    main()