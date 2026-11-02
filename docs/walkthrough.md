# Five minute walkthrough

1. Open the requirement. Point out the unresolved latency target.
2. Show `examples/offline-plan.json` and its intentionally wrong zero-value expectation. Be explicit: this is simulated AI output.
3. Run offline mode. Show `review.json`: the incorrect suggestion is rejected. Show `results.json` and the draft.
4. Run with `--seeded-bug`. Show zero and atomicity failures. Explain how testing an intentionally defective implementation checks whether assertions actually detect a problem.
5. Run live Ollama mode. Compare the generated plan and the separate model review with the rule-based gate. If generation fails, explain why execution stopped and show `error.json`.
6. Run the MCP smoke script. This is real protocol integration, not a function named MCP.
7. Explain human approval and demonstrate that changing evidence invalidates an approved export. Do not describe this local guard as strong identity verification.

## Interview discussion

Why declarative scenarios instead of model-written code? How independent is a reviewer using the same model? Which oracle errors could both implementation and tests share? How would you isolate test execution in a production service? How would you measure flakiness or model regressions? Why is a model's own approval insufficient?

## Future extensions

A persistent run dashboard, stronger reviewer identity, a separately authenticated issue publishing integration, sandboxed code generation and broader mutation testing are possible follow-ups. None is part of the current implementation.
