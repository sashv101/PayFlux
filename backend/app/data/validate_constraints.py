import sqlite3

from app.data.database import get_connection


def validate_constraints() -> None:
    with get_connection() as connection:
        # SQLite requires foreign-key enforcement on every new connection.
        # connection.execute("PRAGMA foreign_keys = ON")

        # Ensure repeated executions of this script remain safe.
        connection.execute(
            "DELETE FROM payments WHERE payment_id IN (?, ?)",
            ("PAY_TEST_001", "PAY_TEST_INVALID"),
        )
        connection.execute(
            "DELETE FROM merchants WHERE merchant_id = ?",
            ("M_TEST_001",),
        )

        connection.execute(
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
            (
                "M_TEST_001",
                "Demo Electronics",
                "retail",
                "Pune",
                "verified",
                2,
                "2026-08-16T10:00:00Z",
            ),
        )

        connection.execute(
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
            (
                "PAY_TEST_001",
                "M_TEST_001",
                125050,
                "upi",
                "captured",
                None,
                "2026-08-16T10:30:00Z",
            ),
        )

        print("PASS: Valid merchant and payment were accepted.")

        try:
            connection.execute(
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
                (
                    "PAY_TEST_INVALID",
                    "M_DOES_NOT_EXIST",
                    50000,
                    "card",
                    "captured",
                    None,
                    "2026-08-16T11:00:00Z",
                ),
            )
        except sqlite3.IntegrityError as error:
            print("PASS: Invalid payment was rejected.")
            print(f"Reason: {error}")
        else:
            raise AssertionError(
                "Foreign-key validation failed: invalid payment was accepted."
            )


if __name__ == "__main__":
    validate_constraints()