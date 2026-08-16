import pytest

from app.data.database import get_connection

from app.data.seed_data import seed_small_dataset
from app.tools.support_tools import (
    lookup_merchant,
    lookup_payment,
    lookup_settlement,
    lookup_ticket,
    retrieve_policy,
)


@pytest.fixture(scope="module", autouse=True)
def prepare_test_data() -> None:
    seed_small_dataset()


def test_lookup_ticket_returns_references() -> None:
    ticket = lookup_ticket("TKT0001")

    assert ticket is not None
    assert ticket["merchant_id"] == "M0001"
    assert ticket["settlement_id"] == "STL0001"
    assert ticket["payment_id"] is None


def test_lookup_ticket_hides_expected_resolution() -> None:
    ticket = lookup_ticket("TKT0001")

    assert ticket is not None
    assert "expected_resolution" not in ticket


def test_lookup_merchant_returns_kyc_evidence() -> None:
    merchant = lookup_merchant("M0003")

    assert merchant is not None
    assert merchant["kyc_status"] == "on_hold"
    assert merchant["settlement_cycle_days"] == 2


def test_lookup_payment_returns_failure_evidence() -> None:
    payment = lookup_payment("PAY0003")

    assert payment is not None
    assert payment["status"] == "failed"
    assert payment["failure_code"] == "bank_declined"
    assert payment["amount_rupees"] == 4999.0


def test_lookup_settlement_distinguishes_delayed_case() -> None:
    settlement = lookup_settlement("STL0001")

    assert settlement is not None
    assert settlement["status"] == "delayed"
    assert settlement["settled_at"] is None


def test_lookup_settlement_distinguishes_scheduled_case() -> None:
    settlement = lookup_settlement("STL0005")

    assert settlement is not None
    assert settlement["status"] == "scheduled"
    assert settlement["scheduled_at"] == "2026-08-18T10:00:00Z"


@pytest.mark.parametrize(
    ("lookup_function", "missing_identifier"),
    [
        (lookup_ticket, "TKT9999"),
        (lookup_merchant, "M9999"),
        (lookup_payment, "PAY9999"),
        (lookup_settlement, "STL9999"),
    ],
)
def test_lookup_tools_return_none_for_missing_records(
    lookup_function,
    missing_identifier: str,
) -> None:
    assert lookup_function(missing_identifier) is None


def test_retrieve_policy_returns_approved_document() -> None:
    policy = retrieve_policy("settlement_delayed")

    assert policy is not None
    assert policy["category"] == "settlement_delayed"
    assert policy["source"] == "settlement_policy.md"
    assert "status is `delayed`" in policy["content"]


def test_retrieve_policy_rejects_unknown_category() -> None:
    policy = retrieve_policy("delete_database")

    assert policy is None


def test_all_ticket_categories_have_policies() -> None:
    with get_connection() as connection:
        categories = connection.execute(
            """
            SELECT DISTINCT category
            FROM tickets
            ORDER BY category
            """
        ).fetchall()

    for row in categories:
        policy = retrieve_policy(row["category"])
        assert policy is not None