# PAY 104 Synthetic payment batch validation

R1 Accept a nonempty batch of at most 100 payments.
R2 A reference must contain 1–40 ASCII letters, digits, underscores or hyphens and be unique within the batch.
R3 Amounts are strings containing digits, a decimal point and exactly two decimal places. Allow 0.01 through 1000000.00 inclusive. Reject zero, negatives, excessive precision and non-finite numbers.
R4 Accept only the exact currency code GBP.
R5 Accept a wholly valid batch with status 201 and imported equal to batch size. For any invalid payment return 422 and imported 0. No partial acceptance.

Unresolved: the product owner says "process quickly" but has not specified a latency threshold. Ask for a measurable target; do not invent a performance pass criterion.

This is a synthetic fixture. It contains no employer or customer information.
