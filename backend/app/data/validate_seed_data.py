from app.data.database import get_connection


EXPECTED_COUNTS = {
    "merchants": 5,
    "payments": 7,
    "settlements": 5,
    "tickets": 5,
}


def validate_record_counts() -> None:
    with get_connection() as connection:
        for table_name, expected_count in EXPECTED_COUNTS.items():
            actual_count = connection.execute(
                f"SELECT COUNT(*) AS count FROM {table_name}"
            ).fetchone()["count"]

            assert actual_count == expected_count, (
                f"{table_name}: expected {expected_count}, "
                f"found {actual_count}"
            )

            print(
                f"PASS: {table_name} contains "
                f"{actual_count} records."
            )


def validate_ticket_relationships() -> None:
    with get_connection() as connection:
        broken_merchant_links = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM tickets AS ticket
            LEFT JOIN merchants AS merchant
                ON ticket.merchant_id = merchant.merchant_id
            WHERE merchant.merchant_id IS NULL
            """
        ).fetchone()["count"]

        broken_payment_links = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM tickets AS ticket
            LEFT JOIN payments AS payment
                ON ticket.payment_id = payment.payment_id
            WHERE ticket.payment_id IS NOT NULL
              AND payment.payment_id IS NULL
            """
        ).fetchone()["count"]

        broken_settlement_links = connection.execute(
            """
            SELECT COUNT(*) AS count
            FROM tickets AS ticket
            LEFT JOIN settlements AS settlement
                ON ticket.settlement_id = settlement.settlement_id
            WHERE ticket.settlement_id IS NOT NULL
              AND settlement.settlement_id IS NULL
            """
        ).fetchone()["count"]

    assert broken_merchant_links == 0
    assert broken_payment_links == 0
    assert broken_settlement_links == 0

    print("PASS: All ticket relationships are valid.")


def validate_key_scenarios() -> None:
    with get_connection() as connection:
        delayed_case = connection.execute(
            """
            SELECT settlement.status
            FROM tickets AS ticket
            JOIN settlements AS settlement
                ON ticket.settlement_id = settlement.settlement_id
            WHERE ticket.ticket_id = 'TKT0001'
            """
        ).fetchone()

        not_delayed_case = connection.execute(
            """
            SELECT settlement.status
            FROM tickets AS ticket
            JOIN settlements AS settlement
                ON ticket.settlement_id = settlement.settlement_id
            WHERE ticket.ticket_id = 'TKT0005'
            """
        ).fetchone()

        failed_payment_case = connection.execute(
            """
            SELECT payment.status, payment.failure_code
            FROM tickets AS ticket
            JOIN payments AS payment
                ON ticket.payment_id = payment.payment_id
            WHERE ticket.ticket_id = 'TKT0002'
            """
        ).fetchone()

    assert delayed_case["status"] == "delayed"
    assert not_delayed_case["status"] == "scheduled"
    assert failed_payment_case["status"] == "failed"
    assert failed_payment_case["failure_code"] == "bank_declined"

    print("PASS: TKT0001 represents a genuinely delayed settlement.")
    print("PASS: TKT0005 represents a settlement that is not delayed.")
    print("PASS: TKT0002 references a bank-declined payment.")


def run_validations() -> None:
    validate_record_counts()
    validate_ticket_relationships()
    validate_key_scenarios()

    print("\nAll PayFlux synthetic-data validations passed.")


if __name__ == "__main__":
    run_validations()