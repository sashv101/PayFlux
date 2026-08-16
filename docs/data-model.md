---
noteId: "ea639690994e11f19c10b500b719a191"
tags: []

---

# PayFlux Data Model

PayFlux uses completely synthetic data representing a fictional payment platform.

## 1. Merchants

Represents businesses using PayFlux.

| Field | Purpose |
|---|---|
| merchant_id | Unique merchant identifier |
| business_name | Fictional business name |
| business_type | Retail, SaaS, education, etc. |
| city | Merchant location |
| kyc_status | verified, pending or on_hold |
| settlement_cycle_days | Number of days before settlement |
| created_at | Merchant registration timestamp |

## 2. Payments

Represents customer payments accepted by merchants.

| Field | Purpose |
|---|---|
| payment_id | Unique payment identifier |
| merchant_id | Merchant receiving the payment |
| amount_paise | Payment amount stored in paise |
| payment_method | UPI, card or net banking |
| status | captured, failed or pending |
| failure_code | Reason when payment fails |
| created_at | Payment timestamp |

## 3. Settlements

Represents money transferred from PayFlux to a merchant's bank account.

| Field | Purpose |
|---|---|
| settlement_id | Unique settlement identifier |
| merchant_id | Merchant receiving the settlement |
| amount_paise | Settlement amount in paise |
| status | scheduled, processed, delayed or on_hold |
| scheduled_at | Expected processing timestamp |
| settled_at | Actual processing timestamp |
| hold_reason | Reason for a settlement hold |

## 4. Support Tickets

Represents merchant complaints requiring investigation.

| Field | Purpose |
|---|---|
| ticket_id | Unique ticket identifier |
| merchant_id | Merchant who raised the ticket |
| payment_id | Related payment, when applicable |
| settlement_id | Related settlement, when applicable |
| subject | Short issue summary |
| description | Merchant's support message |
| category | Expected issue category |
| priority | low, medium or high |
| status | open, investigating or resolved |
| expected_resolution | Labelled correct resolution |
| created_at | Ticket creation timestamp |

## Relationships

- One merchant can have multiple payments.
- One merchant can have multiple settlements.
- One merchant can create multiple support tickets.
- A support ticket may reference a specific payment.
- A support ticket may reference a specific settlement.