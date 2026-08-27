import { useEffect, useState } from "react";

import {
  decideAction,
  executeAction,
  getActions,
  investigateTicket,
} from "./api";

import "./App.css";


function App() {
  const [actions, setActions] = useState([]);
  const [ticketId, setTicketId] = useState("TKT0001");
  const [investigation, setInvestigation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [investigating, setInvestigating] = useState(false);
  const [processingActionId, setProcessingActionId] = useState("");
  const [error, setError] = useState("");


  async function loadActions() {
    try {
      setLoading(true);
      setError("");

      const data = await getActions();
      setActions(data);
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setLoading(false);
    }
  }


  async function handleInvestigation(event) {
    event.preventDefault();

    const normalizedTicketId = ticketId.trim().toUpperCase();

    if (!normalizedTicketId) {
      setError("Enter a ticket ID.");
      return;
    }

    try {
      setInvestigating(true);
      setError("");
      setInvestigation(null);

      const result = await investigateTicket(normalizedTicketId);

      setInvestigation(result);
      await loadActions();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setInvestigating(false);
    }
  }


  async function handleDecision(actionId, approved) {
    const decisionName = approved ? "approve" : "reject";

    const confirmed = window.confirm(
      `Are you sure you want to ${decisionName} this action?`,
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingActionId(actionId);
      setError("");

      await decideAction(actionId, {
        approved,
        reviewer: "payflux_dashboard_reviewer",
        note: approved
          ? "Approved through the PayFlux dashboard."
          : "Rejected through the PayFlux dashboard.",
      });

      await loadActions();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setProcessingActionId("");
    }
  }


  async function handleExecution(actionId) {
    const confirmed = window.confirm(
      "Execute this approved operational action?",
    );

    if (!confirmed) {
      return;
    }

    try {
      setProcessingActionId(actionId);
      setError("");

      await executeAction(actionId);
      await loadActions();
    } catch (requestError) {
      setError(requestError.message);
    } finally {
      setProcessingActionId("");
    }
  }


  useEffect(() => {
    let cancelled = false;

    getActions()
      .then((data) => {
        if (!cancelled) {
          setActions(data);
        }
      })
      .catch((requestError) => {
        if (!cancelled) {
          setError(requestError.message);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);


  return (
    <main>
      <header>
        <p>PAYFLUX</p>

        <h1>Merchant Support Agent</h1>

        <p>
          Investigate support tickets, review proposed actions,
          and control execution.
        </p>
      </header>

      <section>
        <h2>Investigate a ticket</h2>

        <form onSubmit={handleInvestigation}>
          <label htmlFor="ticket-id">
            Ticket ID
          </label>

          <input
            id="ticket-id"
            value={ticketId}
            onChange={(event) => setTicketId(event.target.value)}
            placeholder="For example, TKT0001"
          />

          <button type="submit" disabled={investigating}>
            {investigating
              ? "Agent is investigating..."
              : "Investigate"}
          </button>
        </form>

        {investigation && (
  <article>
    <h3>Investigation completed</h3>

    <p
  className={
    investigation.planned_investigation.plan_followed
      ? "status-badge status-passed"
      : "status-badge status-failed"
  }
>
  Plan adherence:{" "}
  {investigation.planned_investigation.plan_followed
    ? "Passed"
    : "Failed"}
</p>

    <p>
      {investigation.action_preparation.preparation_message}
    </p>

    {investigation.action_preparation.proposed_action && (
      <p>
        Proposed action:{" "}
        {
          investigation.action_preparation.proposed_action
            .action_id
        }{" "}
        (
        {
          investigation.action_preparation.proposed_action
            .status
        }
        )
      </p>
    )}
  </article>
)}
      </section>

      <section>
        <div>
          <h2>Agent actions</h2>

          <button
            type="button"
            onClick={loadActions}
            disabled={loading}
          >
            {loading ? "Loading..." : "Refresh actions"}
          </button>
        </div>

        {error && (
          <p role="alert">
            Error: {error}
          </p>
        )}

        {!loading && !error && actions.length === 0 && (
          <p>No agent actions are currently stored.</p>
        )}

        {actions.map((action) => (
          <article key={action.action_id}>
            <h3>{action.action_type}</h3>

            <p>Action ID: {action.action_id}</p>
            <p>Ticket: {action.ticket_id}</p>
            <p>Target: {action.target_id}</p>
            <p className={`status-badge status-${action.status}`}>
  {action.status.replaceAll("_", " ")}
</p>
            <p>{action.reason}</p>

            {action.status === "pending_approval" && (
              <div>
                <button
                  type="button"
                  onClick={() =>
                    handleDecision(action.action_id, true)
                  }
                  disabled={
                    processingActionId === action.action_id
                  }
                >
                  {processingActionId === action.action_id
                    ? "Processing..."
                    : "Approve"}
                </button>

                <button
                  type="button"
                  onClick={() =>
                    handleDecision(action.action_id, false)
                  }
                  disabled={
                    processingActionId === action.action_id
                  }
                >
                  Reject
                </button>
              </div>
            )}

            {action.status === "approved" && (
              <button
                type="button"
                onClick={() =>
                  handleExecution(action.action_id)
                }
                disabled={
                  processingActionId === action.action_id
                }
              >
                {processingActionId === action.action_id
                  ? "Executing..."
                  : "Execute action"}
              </button>
            )}

            {action.status === "executed" &&
              action.execution_result && (
                <p>
                  Execution result: {action.execution_result}
                </p>
              )}
          </article>
        ))}
      </section>
    </main>
  );
}


export default App;