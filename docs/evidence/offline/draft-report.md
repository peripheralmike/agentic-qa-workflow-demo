# Draft QA report

Run: d1a3e67e01ec

Mode: offline

Seeded defect enabled: False

Status: awaiting human review; no external publishing is implemented.

Passed: 11/11



## Model review

Hand-authored simulated model output. No AI model was called.

- Offline fixture deliberately contains an incorrect expected result for zero.



## Open questions

- What measurable latency threshold replaces process quickly?



## Test results

- minimum: PASS expected {"status": 201, "imported": 1} actual {"status": 201, "imported": 1}

- maximum: PASS expected {"status": 201, "imported": 1} actual {"status": 201, "imported": 1}

- zero: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- precision: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- currency: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- duplicate: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- empty: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- atomicity: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- negative: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- overflow: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- nonfinite: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}



## Rejected suggestions

- wrong-ai-assumption: Expected result contradicts the executable specification
