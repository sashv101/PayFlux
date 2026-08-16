---
noteId: "2c5988e0999811f19c10b500b719a191"
tags: []

---

# PayFlux Settlement Handling Policy

Policy ID: POL-SET-001  
Version: 1.0  
Category: settlement_delayed

## Scheduled settlements

A settlement is not considered delayed when its scheduled processing timestamp
is still in the future.

Support must explain the scheduled date and must not create an escalation.

## Delayed settlements

When the settlement status is `delayed`, support must confirm the delay and
create an escalation for the settlement operations team.

The response must include the settlement ID and scheduled timestamp.

## Processed settlements

When the status is `processed`, support should provide the processing timestamp.

If a merchant reports that a processed settlement has not reached its bank,
the case requires bank-credit investigation.

## Settlements on hold

A settlement with status `on_hold` must not be manually released by support.

Support must inspect the hold reason and follow the applicable compliance
or risk policy.