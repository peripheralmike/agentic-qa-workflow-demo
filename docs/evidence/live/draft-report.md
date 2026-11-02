# Draft QA report

Run: dcc06629df8d

Mode: ollama

Seeded defect enabled: False

Status: awaiting human review; no external publishing is implemented.

Passed: 11/11



## Model review

The proposed plan has several gaps in coverage for the requirements, particularly for R1 (batch size), R2 (reference field), and R5 (imported value). The scenarios do not fully test the edge cases for R3 (amount validation) and R2 (reference field). The 'imported' value for valid batches is incorrectly set to 1 in all valid scenarios, which should be the batch size. The latency question remains unresolved.

- The proposed plan does not cover the case where the batch size exceeds 100 payments (R1).

- The reference field validation (R2) is not fully covered in the scenarios. The scenarios only test for duplicates and a single invalid reference, but not the full range of 1-40 characters with allowed characters.

- The amount validation (R3) is covered with some examples, but the scenarios do not test for all edge cases like '0.00' (zero), negative numbers, and excessive precision, though they do include some examples.

- The currency validation (R4) is covered in the scenarios with a USD example, but the scenarios do not test for other valid currency codes beyond GBP.

- The requirement R5 states that for a valid batch, 'imported' should equal the batch size. However, the scenarios for valid batches (valid_batch_001, valid_batch_002, valid_batch_003) all have 'expected_imported':1, which is incorrect for batches with more than one payment.

- The 'empty_batch' scenario tests for an empty batch, which is covered by R1 (nonempty batch), but the expected status is 422, which is correct as per R1.

- The 'duplicate_reference' scenario tests for duplicate references, which is part of R2, but the scenarios do not cover the case where the reference has invalid characters (e.g., spaces, special characters not in the allowed set).

- The 'mixed_valid_invalid' scenario tests for a mix of valid and invalid payments, which is covered by R5, but the expected status is 422 and imported 0, which is correct as per R5.

- The latency question is mentioned as unresolved but not addressed in the scenarios.



## Open questions

- What is the purpose of the synthetic payment batch validation?

- What are the specific requirements for the reference field?

- What is the allowed range for payment amounts?

- What currency is accepted?

- What happens if a payment batch is invalid?

- What is the expected status code for a valid batch?

- What is the expected value of 'imported' for a valid batch?

- What is the expected status code for an invalid batch?

- What is the expected value of 'imported' for an invalid batch?

- What is the unresolved latency question?



## Test results

- valid_batch_001: PASS expected {"status": 201, "imported": 1} actual {"status": 201, "imported": 1}

- valid_batch_002: PASS expected {"status": 201, "imported": 1} actual {"status": 201, "imported": 1}

- valid_batch_003: PASS expected {"status": 201, "imported": 1} actual {"status": 201, "imported": 1}

- invalid_batch_003: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- invalid_batch_004: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- invalid_batch_005: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- invalid_batch_006: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- invalid_batch_007: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- empty_batch: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- duplicate_reference: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}

- mixed_valid_invalid: PASS expected {"status": 422, "imported": 0} actual {"status": 422, "imported": 0}



## Rejected suggestions

- invalid_batch_001: Expected result contradicts the executable specification

- invalid_batch_002: Expected result contradicts the executable specification

- invalid_batch_008: Expected result contradicts the executable specification
