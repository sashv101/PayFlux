---
noteId: "434a0840999811f19c10b500b719a191"
tags: []

---

# PayFlux Payment Failure Policy

Policy ID: POL-PAY-001  
Version: 1.0  
Category: payment_failed

## Failed payments

Support must inspect the payment status and failure code before responding.

When the failure code is `bank_declined`, explain that the issuing bank declined
the transaction. Recommend that the customer contact the bank or retry using a
different payment method.

## Pending payments

A pending payment must not be described as successful or failed until its final
status is available.

Support should ask the merchant to wait for status reconciliation.

## Captured payments

A captured payment was successfully processed by PayFlux.

Support must not describe a captured payment as failed merely because the
merchant's ticket uses the word "failed".

## Sensitive information

Support must never request a complete card number, CVV, PIN, password, OTP or
API secret.