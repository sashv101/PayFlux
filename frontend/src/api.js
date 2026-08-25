const API_BASE_URL = "http://127.0.0.1:8000";


async function apiRequest(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => null);

    throw new Error(
      errorBody?.detail ||
        `Request failed with status ${response.status}`,
    );
  }

  return response.json();
}


export function getActions(status = "") {
  const query = status
    ? `?action_status=${encodeURIComponent(status)}`
    : "";

  return apiRequest(`/agent/actions${query}`);
}


export function investigateTicket(ticketId) {
  return apiRequest(`/agent/investigate/${ticketId}`, {
    method: "POST",
  });
}


export function decideAction(actionId, decision) {
  return apiRequest(`/agent/actions/${actionId}/decision`, {
    method: "POST",
    body: JSON.stringify(decision),
  });
}


export function executeAction(actionId) {
  return apiRequest(`/agent/actions/${actionId}/execute`, {
    method: "POST",
  });
}