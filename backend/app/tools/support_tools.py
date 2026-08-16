from app.data.database import get_connection
from pathlib import Path

BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIRECTORY = BACKEND_DIRECTORY / "knowledge"

POLICY_FILES = {
    "settlement_delayed": "settlement_policy.md",
    "payment_failed": "payment_failure_policy.md",
    "kyc_review": "kyc_policy.md",
    "api_integration": "api_integration_policy.md",
}

def lookup_ticket(ticket_id: str) -> dict | None:
    """
    Retrieve one support ticket.

    This deliberately excludes expected_resolution because that field
    is reserved for evaluation and must not be visible to the agent.
    """

    with get_connection() as connection:
        ticket = connection.execute(
            """
            SELECT
                ticket_id,
                merchant_id,
                payment_id,
                settlement_id,
                subject,
                description,
                category,
                priority,
                status,
                created_at
            FROM tickets
            WHERE ticket_id = ?
            """,
            (ticket_id,),
        ).fetchone()

    if ticket is None:
        return None

    return dict(ticket)


def lookup_merchant(merchant_id: str) -> dict | None:
    """
    Retrieve the operational profile of one merchant.
    """

    with get_connection() as connection:
        merchant = connection.execute(
            """
            SELECT
                merchant_id,
                business_name,
                business_type,
                city,
                kyc_status,
                settlement_cycle_days,
                created_at
            FROM merchants
            WHERE merchant_id = ?
            """,
            (merchant_id,),
        ).fetchone()

    if merchant is None:
        return None

    return dict(merchant)


def lookup_payment(payment_id: str) -> dict | None:
    """
    Retrieve the current status and failure evidence for one payment.

    Use this tool when a support ticket references a payment ID or when
    the merchant asks about a failed, pending or captured payment.
    """

    with get_connection() as connection:
        payment = connection.execute(
            """
            SELECT
                payment_id,
                merchant_id,
                amount_paise,
                payment_method,
                status,
                failure_code,
                created_at
            FROM payments
            WHERE payment_id = ?
            """,
            (payment_id,),
        ).fetchone()

    if payment is None:
        return None

    payment_data = dict(payment)
    payment_data["amount_rupees"] = (
        payment_data["amount_paise"] / 100
    )

    return payment_data


def lookup_settlement(settlement_id: str) -> dict | None:
    """
    Retrieve the current status, schedule and hold information for
    one settlement.

    Use this tool when a ticket references a settlement ID or when a
    merchant reports that settlement funds have not reached its bank.
    """

    with get_connection() as connection:
        settlement = connection.execute(
            """
            SELECT
                settlement_id,
                merchant_id,
                amount_paise,
                status,
                scheduled_at,
                settled_at,
                hold_reason
            FROM settlements
            WHERE settlement_id = ?
            """,
            (settlement_id,),
        ).fetchone()

    if settlement is None:
        return None

    settlement_data = dict(settlement)
    settlement_data["amount_rupees"] = (
        settlement_data["amount_paise"] / 100
    )

    return settlement_data


def retrieve_policy(category: str) -> dict | None:
    """
    Retrieve the approved PayFlux policy for a support category.

    Use this tool after identifying the ticket category and gathering
    operational evidence. The policy determines which response or
    escalation is permitted.
    """

    file_name = POLICY_FILES.get(category)

    if file_name is None:
        return None

    policy_path = KNOWLEDGE_DIRECTORY / file_name

    if not policy_path.exists():
        return None

    content = policy_path.read_text(encoding="utf-8")

    return {
        "category": category,
        "source": file_name,
        "content": content,
    }