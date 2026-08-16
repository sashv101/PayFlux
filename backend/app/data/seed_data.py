from app.data.database import create_database, get_connection


MERCHANTS = [
    (
        "M0001",
        "BlueCart Electronics",
        "retail",
        "Pune",
        "verified",
        2,
        "2026-07-01T09:00:00Z",
    ),
    (
        "M0002",
        "LearnSphere Academy",
        "education",
        "Bengaluru",
        "verified",
        1,
        "2026-07-05T10:30:00Z",
    ),
    (
        "M0003",
        "FreshRoute Foods",
        "food_delivery",
        "Mumbai",
        "on_hold",
        2,
        "2026-07-10T11:00:00Z",
    ),
    (
        "M0004",
        "CloudDesk Software",
        "saas",
        "Hyderabad",
        "verified",
        3,
        "2026-07-15T12:15:00Z",
    ),
    (
        "M0005",
        "UrbanThread Fashion",
        "fashion",
        "Delhi",
        "pending",
        2,
        "2026-07-20T14:00:00Z",
    ),
]

PAYMENTS = [
    (
        "PAY0001",
        "M0001",
        125050,
        "upi",
        "captured",
        None,
        "2026-08-13T10:15:00Z",
    ),
    (
        "PAY0002",
        "M0001",
        750000,
        "card",
        "captured",
        None,
        "2026-08-13T14:30:00Z",
    ),
    (
        "PAY0003",
        "M0002",
        499900,
        "card",
        "failed",
        "bank_declined",
        "2026-08-14T09:20:00Z",
    ),
    (
        "PAY0004",
        "M0002",
        250000,
        "upi",
        "captured",
        None,
        "2026-08-14T11:45:00Z",
    ),
    (
        "PAY0005",
        "M0003",
        185000,
        "netbanking",
        "captured",
        None,
        "2026-08-14T16:10:00Z",
    ),
    (
        "PAY0006",
        "M0004",
        999900,
        "card",
        "captured",
        None,
        "2026-08-15T08:30:00Z",
    ),
    (
        "PAY0007",
        "M0005",
        349900,
        "upi",
        "pending",
        None,
        "2026-08-15T12:00:00Z",
    ),
]

SETTLEMENTS = [
    (
        "STL0001",
        "M0001",
        875050,
        "delayed",
        "2026-08-15T10:00:00Z",
        None,
        None,
    ),
    (
        "STL0002",
        "M0002",
        250000,
        "processed",
        "2026-08-15T10:00:00Z",
        "2026-08-15T10:30:00Z",
        None,
    ),
    (
        "STL0003",
        "M0003",
        185000,
        "on_hold",
        "2026-08-16T10:00:00Z",
        None,
        "kyc_review",
    ),
    (
        "STL0004",
        "M0004",
        999900,
        "scheduled",
        "2026-08-18T10:00:00Z",
        None,
        None,
    ),
    (
        "STL0005",
        "M0005",
        349900,
        "scheduled",
        "2026-08-18T10:00:00Z",
        None,
        None,
    ),
]

TICKETS = [
    (
        "TKT0001",
        "M0001",
        None,
        "STL0001",
        "Settlement has not reached our bank",
        (
            "Settlement STL0001 was expected yesterday, but the amount "
            "has still not reached our bank account."
        ),
        "settlement_delayed",
        "high",
        "open",
        (
            "Confirm that STL0001 is delayed and escalate it to the "
            "settlement operations team for investigation."
        ),
        "2026-08-16T08:30:00Z",
    ),
    (
        "TKT0002",
        "M0002",
        "PAY0003",
        None,
        "Customer payment failed",
        (
            "The customer attempted a card payment but the payment "
            "failed. Please explain what happened."
        ),
        "payment_failed",
        "medium",
        "open",
        (
            "Explain that PAY0003 was declined by the customer's bank "
            "and recommend retrying with another payment method."
        ),
        "2026-08-16T08:45:00Z",
    ),
    (
        "TKT0003",
        "M0003",
        None,
        "STL0003",
        "Settlement blocked despite successful payment",
        (
            "Our customer payment was successful, but our settlement "
            "is currently blocked."
        ),
        "kyc_review",
        "high",
        "open",
        (
            "Explain that the settlement is on hold because the merchant "
            "account requires KYC review. Do not bypass the compliance hold."
        ),
        "2026-08-16T09:00:00Z",
    ),
    (
        "TKT0004",
        "M0004",
        None,
        None,
        "Production API returning errors",
        (
            "Our checkout integration is receiving intermittent server "
            "errors in production."
        ),
        "api_integration",
        "high",
        "open",
        (
            "Request safe diagnostic details such as request ID, timestamp "
            "and HTTP status. Never request API secrets or card information."
        ),
        "2026-08-16T09:15:00Z",
    ),
    (
        "TKT0005",
        "M0005",
        None,
        "STL0005",
        "Settlement not received yet",
        (
            "We have not received today's settlement. Please process it "
            "as soon as possible."
        ),
        "settlement_delayed",
        "low",
        "open",
        (
            "Explain that STL0005 is scheduled for 2026-08-18 and is not "
            "currently delayed. No escalation is required."
        ),
        "2026-08-16T09:30:00Z",
    ),
]

def clear_existing_data() -> None:
    """
    Delete child records before parent records to preserve
    foreign-key integrity.
    """

    with get_connection() as connection:
        connection.execute("DELETE FROM tickets")
        connection.execute("DELETE FROM settlements")
        connection.execute("DELETE FROM payments")
        connection.execute("DELETE FROM merchants")


def insert_merchants() -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO merchants (
                merchant_id,
                business_name,
                business_type,
                city,
                kyc_status,
                settlement_cycle_days,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            MERCHANTS,
        )

def insert_payments() -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO payments (
                payment_id,
                merchant_id,
                amount_paise,
                payment_method,
                status,
                failure_code,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            PAYMENTS,
        )

def insert_settlements() -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO settlements (
                settlement_id,
                merchant_id,
                amount_paise,
                status,
                scheduled_at,
                settled_at,
                hold_reason
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            SETTLEMENTS,
        )

def insert_tickets() -> None:
    with get_connection() as connection:
        connection.executemany(
            """
            INSERT INTO tickets (
                ticket_id,
                merchant_id,
                payment_id,
                settlement_id,
                subject,
                description,
                category,
                priority,
                status,
                expected_resolution,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            TICKETS,
        )

def display_merchants() -> None:
    with get_connection() as connection:
        merchants = connection.execute(
            """
            SELECT
                merchant_id,
                business_name,
                city,
                kyc_status,
                settlement_cycle_days
            FROM merchants
            ORDER BY merchant_id
            """
        ).fetchall()

    print(f"\nCreated {len(merchants)} synthetic merchants:\n")

    for merchant in merchants:
        print(dict(merchant))

def display_payments() -> None:
    with get_connection() as connection:
        payments = connection.execute(
            """
            SELECT
                payment_id,
                merchant_id,
                amount_paise,
                payment_method,
                status,
                failure_code
            FROM payments
            ORDER BY payment_id
            """
        ).fetchall()

    print(f"\nCreated {len(payments)} synthetic payments:\n")

    for payment in payments:
        payment_data = dict(payment)
        payment_data["amount_rupees"] = (
            payment_data.pop("amount_paise") / 100
        )
        print(payment_data)

def display_settlements() -> None:
    with get_connection() as connection:
        settlements = connection.execute(
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
            ORDER BY settlement_id
            """
        ).fetchall()

    print(f"\nCreated {len(settlements)} synthetic settlements:\n")

    for settlement in settlements:
        settlement_data = dict(settlement)
        settlement_data["amount_rupees"] = (
            settlement_data.pop("amount_paise") / 100
        )
        print(settlement_data)

def display_tickets() -> None:
    with get_connection() as connection:
        tickets = connection.execute(
            """
            SELECT
                ticket_id,
                merchant_id,
                payment_id,
                settlement_id,
                subject,
                category,
                priority,
                expected_resolution
            FROM tickets
            ORDER BY ticket_id
            """
        ).fetchall()

    print(f"\nCreated {len(tickets)} synthetic tickets:\n")

    for ticket in tickets:
        print(dict(ticket))

def seed_small_dataset() -> None:
    create_database()
    clear_existing_data()

    insert_merchants()
    insert_payments()
    insert_settlements()
    insert_tickets()

    display_merchants()
    display_payments()
    display_settlements()
    display_tickets()


if __name__ == "__main__":
    seed_small_dataset()