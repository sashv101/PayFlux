import pytest
from fastapi.testclient import TestClient

from app.data.seed_data import seed_small_dataset
from app.main import app


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def prepare_test_data() -> None:
    """
    Rebuild the deterministic dataset before this test module runs.
    """

    seed_small_dataset()


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "payflux-api",
    }


def test_ticket_list_returns_five_records() -> None:
    response = client.get("/api/tickets")

    assert response.status_code == 200

    tickets = response.json()

    assert len(tickets) == 5
    assert tickets[0]["ticket_id"] == "TKT0005"


def test_ticket_list_does_not_expose_answer_key() -> None:
    response = client.get("/api/tickets")

    tickets = response.json()

    for ticket in tickets:
        assert "expected_resolution" not in ticket


def test_delayed_settlement_ticket_contains_evidence() -> None:
    response = client.get("/api/tickets/TKT0001")

    assert response.status_code == 200

    ticket = response.json()

    assert ticket["merchant"]["merchant_id"] == "M0001"
    assert ticket["settlement"]["settlement_id"] == "STL0001"
    assert ticket["settlement"]["status"] == "delayed"
    assert ticket["payment"] is None
    assert "expected_resolution" not in ticket


def test_failed_payment_ticket_contains_evidence() -> None:
    response = client.get("/api/tickets/TKT0002")

    assert response.status_code == 200

    ticket = response.json()

    assert ticket["payment"]["payment_id"] == "PAY0003"
    assert ticket["payment"]["status"] == "failed"
    assert ticket["payment"]["failure_code"] == "bank_declined"
    assert ticket["settlement"] is None


def test_unknown_ticket_returns_404() -> None:
    response = client.get("/api/tickets/TKT9999")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Ticket not found",
    }