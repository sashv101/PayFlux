import json

from agents import function_tool

from app.tools.support_tools import (
    lookup_merchant,
    lookup_payment,
    lookup_settlement,
    lookup_ticket,
    retrieve_policy,
)


@function_tool
def lookup_ticket_tool(ticket_id: str) -> str:
    """
    Retrieve one PayFlux support ticket and its related record identifiers.

    Use this as the first tool when investigating a ticket. It returns the
    merchant ID and, when applicable, a payment ID or settlement ID. It does
    not return operational evidence or the expected resolution.

    Args:
        ticket_id: PayFlux ticket identifier, such as TKT0001.
    """

    ticket = lookup_ticket(ticket_id)

    if ticket is None:
        return json.dumps(
            {
                "error": "ticket_not_found",
                "ticket_id": ticket_id,
            }
        )

    return json.dumps(ticket, ensure_ascii=False)

@function_tool
def lookup_merchant_tool(merchant_id: str) -> str:
    """
    Retrieve the operational profile of one PayFlux merchant.

    Use this after a ticket identifies a merchant. It provides the merchant's
    KYC status and settlement cycle, which may affect support decisions.

    Args:
        merchant_id: PayFlux merchant identifier, such as M0001.
    """

    merchant = lookup_merchant(merchant_id)

    if merchant is None:
        return json.dumps(
            {
                "error": "merchant_not_found",
                "merchant_id": merchant_id,
            }
        )

    return json.dumps(merchant, ensure_ascii=False)

@function_tool
def lookup_payment_tool(payment_id: str) -> str:
    """
    Retrieve verified status and failure evidence for one PayFlux payment.

    Use this when a ticket references a payment ID. Do not infer payment
    status from the merchant's description when this tool is available.

    Args:
        payment_id: PayFlux payment identifier, such as PAY0003.
    """

    payment = lookup_payment(payment_id)

    if payment is None:
        return json.dumps(
            {
                "error": "payment_not_found",
                "payment_id": payment_id,
            }
        )

    return json.dumps(payment, ensure_ascii=False)

@function_tool
def lookup_settlement_tool(settlement_id: str) -> str:
    """
    Retrieve verified status, schedule and hold evidence for one settlement.

    Use this when a ticket references a settlement ID. This tool determines
    whether the settlement is delayed, scheduled, processed or on hold.

    Args:
        settlement_id: PayFlux settlement identifier, such as STL0001.
    """

    settlement = lookup_settlement(settlement_id)

    if settlement is None:
        return json.dumps(
            {
                "error": "settlement_not_found",
                "settlement_id": settlement_id,
            }
        )

    return json.dumps(settlement, ensure_ascii=False)

@function_tool
def retrieve_policy_tool(category: str) -> str:
    """
    Retrieve the approved synthetic PayFlux policy for a support category.

    Use this after gathering operational evidence and before recommending
    an action. The policy defines what support may communicate or escalate.

    Args:
        category: Supported ticket category, such as settlement_delayed.
    """

    policy = retrieve_policy(category)

    if policy is None:
        return json.dumps(
            {
                "error": "policy_not_found",
                "category": category,
            }
        )

    return json.dumps(policy, ensure_ascii=False)