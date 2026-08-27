import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, test, vi } from "vitest";

import App from "./App";
import {
  decideAction,
  executeAction,
  getActions,
} from "./api";


vi.mock("./api", () => ({
  decideAction: vi.fn(),
  executeAction: vi.fn(),
  getActions: vi.fn(),
  investigateTicket: vi.fn(),
}));


const executedAction = {
  action_id: "ACT-TEST123",
  ticket_id: "TKT0001",
  action_type: "escalate_settlement",
  target_id: "STL0001",
  status: "executed",
  reason: "Settlement delay confirmed.",
  execution_result: "Settlement escalation created.",
};

const pendingAction = {
  ...executedAction,
  action_id: "ACT-PENDING123",
  status: "pending_approval",
  execution_result: null,
};

const approvedAction = {
  ...executedAction,
  action_id: "ACT-APPROVED123",
  status: "approved",
  execution_result: null,
};


describe("PayFlux dashboard", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    getActions.mockImplementation((status = "") => {
      if (status === "pending_approval") {
        return Promise.resolve([]);
      }

      return Promise.resolve([executedAction]);
    });
  });


  test("loads and displays stored agent actions", async () => {
    render(<App />);

    expect(
      await screen.findByText(/ACT-TEST123/),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Settlement delay confirmed."),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Settlement escalation created.", {
        exact: false,
      }),
    ).toBeInTheDocument();
  });


  test("filters actions by selected status", async () => {
    const user = userEvent.setup();

    render(<App />);

    await screen.findByText(/ACT-TEST123/);

    await user.selectOptions(
      screen.getByLabelText("Status"),
      "pending_approval",
    );

    await waitFor(() => {
      expect(getActions).toHaveBeenLastCalledWith(
        "pending_approval",
      );
    });

    expect(
      await screen.findByText(
        "No pending approval actions found.",
      ),
    ).toBeInTheDocument();
  });

  test("submits a human approval decision", async () => {
    const user = userEvent.setup();

    getActions.mockResolvedValue([pendingAction]);
    decideAction.mockResolvedValue({
        ...pendingAction,
        status: "approved",
    });

    const confirmSpy = vi
        .spyOn(window, "confirm")
        .mockReturnValue(true);

    render(<App />);

    await user.click(
        await screen.findByRole("button", {
        name: "Approve",
        }),
    );

    await waitFor(() => {
        expect(decideAction).toHaveBeenCalledWith(
        "ACT-PENDING123",
        expect.objectContaining({
            approved: true,
            reviewer: "payflux_dashboard_reviewer",
        }),
        );
    });

    confirmSpy.mockRestore();
    });


    test("executes an approved action after confirmation", async () => {
    const user = userEvent.setup();

    getActions.mockResolvedValue([approvedAction]);
    executeAction.mockResolvedValue({
        ...approvedAction,
        status: "executed",
    });

    const confirmSpy = vi
        .spyOn(window, "confirm")
        .mockReturnValue(true);

    render(<App />);

    await user.click(
        await screen.findByRole("button", {
        name: "Execute action",
        }),
    );

    await waitFor(() => {
        expect(executeAction).toHaveBeenCalledWith(
        "ACT-APPROVED123",
        );
    });

    confirmSpy.mockRestore();
    });
});