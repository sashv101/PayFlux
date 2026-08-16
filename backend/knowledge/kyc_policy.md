---
noteId: "5be180e0999811f19c10b500b719a191"
tags: []

---

# PayFlux KYC and Compliance Hold Policy

Policy ID: POL-KYC-001  
Version: 1.0  
Category: kyc_review

## Pending KYC

When KYC status is `pending`, support should explain that verification is still
under review.

## KYC hold

When KYC status is `on_hold`, settlements may remain blocked until compliance
review is complete.

Support must not bypass, remove or promise the removal of a compliance hold.

The case may be routed to the compliance-review queue when the merchant disputes
the hold or has already submitted the requested documents.

## Verified merchants

A verified merchant should not be told that a settlement is blocked by KYC
unless settlement evidence explicitly contains a KYC-related hold.