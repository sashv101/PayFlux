from app.data.database import get_connection
from app.models.ticket import (
    MerchantEvidence,
    PaymentEvidence,
    SettlementEvidence,
    TicketDetail,
    TicketSummary,
)


def list_tickets() -> list[TicketSummary]:
    
    """
    Retrieve all support tickets in newest-first order.
    """

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                ticket_id,
                merchant_id,
                payment_id,
                settlement_id,
                subject,
                category,
                priority,
                status,
                created_at
            FROM tickets
            ORDER BY created_at DESC
            """
        ).fetchall()

    return [
        TicketSummary(**dict(row))
        for row in rows
    ]


def get_ticket_detail(ticket_id: str) -> TicketDetail | None:
    """
    Retrieve a ticket together with its connected evidence.
    """

    with get_connection() as connection:
        ticket_row = connection.execute(
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

        if ticket_row is None:
            return None

        merchant_row = connection.execute(
            """
            SELECT
                merchant_id,
                business_name,
                business_type,
                city,
                kyc_status,
                settlement_cycle_days
            FROM merchants
            WHERE merchant_id = ?
            """,
            (ticket_row["merchant_id"],),
        ).fetchone()

        payment_row = None

        if ticket_row["payment_id"] is not None:
            payment_row = connection.execute(
                """
                SELECT
                    payment_id,
                    amount_paise,
                    payment_method,
                    status,
                    failure_code,
                    created_at
                FROM payments
                WHERE payment_id = ?
                """,
                (ticket_row["payment_id"],),
            ).fetchone()

        settlement_row = None

        if ticket_row["settlement_id"] is not None:
            settlement_row = connection.execute(
                """
                SELECT
                    settlement_id,
                    amount_paise,
                    status,
                    scheduled_at,
                    settled_at,
                    hold_reason
                FROM settlements
                WHERE settlement_id = ?
                """,
                (ticket_row["settlement_id"],),
            ).fetchone()

    return TicketDetail(
        ticket_id=ticket_row["ticket_id"],
        subject=ticket_row["subject"],
        description=ticket_row["description"],
        category=ticket_row["category"],
        priority=ticket_row["priority"],
        status=ticket_row["status"],
        created_at=ticket_row["created_at"],
        merchant=MerchantEvidence(**dict(merchant_row)),
        payment=(
            PaymentEvidence(**dict(payment_row))
            if payment_row is not None
            else None
        ),
        settlement=(
            SettlementEvidence(**dict(settlement_row))
            if settlement_row is not None
            else None
        ),
    )