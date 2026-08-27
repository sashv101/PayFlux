import pytest
from fastapi.testclient import TestClient

from app.data.seed_data import seed_small_dataset
from app.main import app
from app.workflows.action_models import ActionType
from app.workflows.action_store import create_proposed_action


client = TestClient(app)


@pytest.fixture(autouse=True)
def prepare_test_data():
    seed_small_dataset()
    yield


def create_test_action():
    return create_proposed_action(
        ticket_id="TKT0001",
        action_type=ActionType.ESCALATE_SETTLEMENT,
        target_id="STL0001",
        reason="Delayed settlement requires review.",
        requested_by="api_test",
    )


def test_action_list_starts_empty():
    response = client.get("/agent/actions")

    assert response.status_code == 200
    assert response.json() == []


def test_unknown_action_returns_404():
    response = client.get(
        "/agent/actions/ACT-DOES-NOT-EXIST"
    )

    assert response.status_code == 404


def test_action_list_supports_status_filter():
    action = create_test_action()

    response = client.get(
        "/agent/actions",
        params={"action_status": "pending_approval"},
    )

    assert response.status_code == 200

    actions = response.json()

    assert len(actions) == 1
    assert actions[0]["action_id"] == action.action_id
    assert actions[0]["status"] == "pending_approval"


def test_pending_action_cannot_execute():
    action = create_test_action()

    response = client.post(
        f"/agent/actions/{action.action_id}/execute"
    )

    assert response.status_code == 409
    assert "requires human approval" in (
        response.json()["detail"].lower()
    )


def test_approved_action_can_execute_once():
    action = create_test_action()

    decision_response = client.post(
        f"/agent/actions/{action.action_id}/decision",
        json={
            "approved": True,
            "reviewer": "api_test_reviewer",
            "note": "Approved by API test.",
        },
    )

    assert decision_response.status_code == 200
    assert decision_response.json()["status"] == "approved"

    second_decision_response = client.post(
        f"/agent/actions/{action.action_id}/decision",
        json={
            "approved": False,
            "reviewer": "second_reviewer",
            "note": "This decision must be blocked.",
        },
    )

    assert second_decision_response.status_code == 409

    execution_response = client.post(
        f"/agent/actions/{action.action_id}/execute"
    )

    assert execution_response.status_code == 200
    assert execution_response.json()["status"] == "executed"

    repeated_execution_response = client.post(
        f"/agent/actions/{action.action_id}/execute"
    )

    assert repeated_execution_response.status_code == 409

    stored_response = client.get(
        f"/agent/actions/{action.action_id}"
    )

    assert stored_response.status_code == 200
    assert stored_response.json()["status"] == "executed"
    assert stored_response.json()["executed_at"] is not None
    assert stored_response.json()["execution_result"] is not None


def test_rejected_action_cannot_execute():
    action = create_test_action()

    decision_response = client.post(
        f"/agent/actions/{action.action_id}/decision",
        json={
            "approved": False,
            "reviewer": "api_test_reviewer",
            "note": "Rejected by API test.",
        },
    )

    assert decision_response.status_code == 200
    assert decision_response.json()["status"] == "rejected"

    execution_response = client.post(
        f"/agent/actions/{action.action_id}/execute"
    )

    assert execution_response.status_code == 409

    stored_response = client.get(
        f"/agent/actions/{action.action_id}"
    )

    stored_action = stored_response.json()

    assert stored_action["status"] == "rejected"
    assert stored_action["executed_at"] is None
    assert stored_action["execution_result"] is None

def test_cors_allows_local_frontend():
    response = client.options(
        "/agent/actions",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert response.status_code == 200
    assert (
        response.headers["access-control-allow-origin"]
        == "http://localhost:5173"
    )