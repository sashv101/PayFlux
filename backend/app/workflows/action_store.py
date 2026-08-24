import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.workflows.action_models import (
    ActionExecutionOutcome,
    ActionStatus,
    ActionType,
    ApprovalDecision,
    ProposedAction,
)


DATABASE_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "payflux.db"
)


CREATE_ACTIONS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS agent_actions (
    action_id TEXT PRIMARY KEY,
    ticket_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL CHECK (
        status IN (
            'pending_approval',
            'approved',
            'rejected',
            'executed',
            'failed'
        )
    ),
    requested_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    approved_by TEXT,
    approval_note TEXT,
    decided_at TEXT,
    executed_at TEXT,
    execution_result TEXT,
    FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
);
"""


CREATE_STATUS_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_agent_actions_status
ON agent_actions(status);
"""


CREATE_TICKET_INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_agent_actions_ticket
ON agent_actions(ticket_id);
"""


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_action_store() -> None:
    with get_connection() as connection:
        connection.execute(CREATE_ACTIONS_TABLE_SQL)
        connection.execute(CREATE_STATUS_INDEX_SQL)
        connection.execute(CREATE_TICKET_INDEX_SQL)
        connection.commit()


def row_to_action(row: sqlite3.Row) -> ProposedAction:
    return ProposedAction.model_validate(dict(row))


def create_proposed_action(
    ticket_id: str,
    action_type: ActionType,
    target_id: str,
    reason: str,
    requested_by: str = "payflux_agent",
) -> ProposedAction:
    initialize_action_store()

    action = ProposedAction(
        action_id=f"ACT-{uuid4().hex[:12].upper()}",
        ticket_id=ticket_id,
        action_type=action_type,
        target_id=target_id,
        reason=reason,
        status=ActionStatus.PENDING_APPROVAL,
        requested_by=requested_by,
        created_at=utc_now(),
    )

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO agent_actions (
                action_id,
                ticket_id,
                action_type,
                target_id,
                reason,
                status,
                requested_by,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                action.action_id,
                action.ticket_id,
                action.action_type.value,
                action.target_id,
                action.reason,
                action.status.value,
                action.requested_by,
                action.created_at.isoformat(),
            ),
        )
        connection.commit()

    return action


def get_action(action_id: str) -> ProposedAction | None:
    initialize_action_store()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM agent_actions
            WHERE action_id = ?
            """,
            (action_id,),
        ).fetchone()

    return row_to_action(row) if row is not None else None


def list_actions(
    status: ActionStatus | None = None,
) -> list[ProposedAction]:
    initialize_action_store()

    with get_connection() as connection:
        if status is None:
            rows = connection.execute(
                """
                SELECT *
                FROM agent_actions
                ORDER BY created_at DESC
                """
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT *
                FROM agent_actions
                WHERE status = ?
                ORDER BY created_at DESC
                """,
                (status.value,),
            ).fetchall()

    return [row_to_action(row) for row in rows]

def find_reusable_action(
    ticket_id: str,
    action_type: ActionType,
    target_id: str,
) -> ProposedAction | None:
    """
    Find an existing non-failed action for the same ticket,
    action type and target.

    Rejected and failed actions may be proposed again.
    Pending, approved or executed actions are reused.
    """

    initialize_action_store()

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM agent_actions
            WHERE ticket_id = ?
              AND action_type = ?
              AND target_id = ?
              AND status IN (
                  'pending_approval',
                  'approved',
                  'executed'
              )
            ORDER BY created_at DESC
            LIMIT 1
            """,
            (
                ticket_id,
                action_type.value,
                target_id,
            ),
        ).fetchone()

    return row_to_action(row) if row is not None else None

def decide_action(
    decision: ApprovalDecision,
) -> ProposedAction:
    initialize_action_store()

    new_status = (
        ActionStatus.APPROVED
        if decision.approved
        else ActionStatus.REJECTED
    )

    decided_at = utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE agent_actions
            SET
                status = ?,
                approved_by = ?,
                approval_note = ?,
                decided_at = ?
            WHERE action_id = ?
              AND status = 'pending_approval'
            """,
            (
                new_status.value,
                decision.reviewer,
                decision.note,
                decided_at.isoformat(),
                decision.action_id,
            ),
        )
        connection.commit()

    if cursor.rowcount != 1:
        raise ValueError(
            "Action does not exist or is no longer pending approval."
        )

    updated_action = get_action(decision.action_id)

    if updated_action is None:
        raise RuntimeError("Updated action could not be retrieved.")

    return updated_action


def record_execution(
    action_id: str,
    execution_result: str,
    succeeded: bool,
) -> ActionExecutionOutcome:
    initialize_action_store()

    final_status = (
        ActionStatus.EXECUTED
        if succeeded
        else ActionStatus.FAILED
    )

    executed_at = utc_now()

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE agent_actions
            SET
                status = ?,
                executed_at = ?,
                execution_result = ?
            WHERE action_id = ?
              AND status = 'approved'
            """,
            (
                final_status.value,
                executed_at.isoformat(),
                execution_result,
                action_id,
            ),
        )
        connection.commit()

    if cursor.rowcount != 1:
        raise ValueError(
            "Only an approved action can be recorded as executed."
        )

    return ActionExecutionOutcome(
        action_id=action_id,
        status=final_status,
        execution_result=execution_result,
        executed_at=executed_at,
    )


def main() -> None:
    initialize_action_store()

    print("Action store and lifecycle operations are ready")
    print(f"Database: {DATABASE_PATH}")


if __name__ == "__main__":
    main()