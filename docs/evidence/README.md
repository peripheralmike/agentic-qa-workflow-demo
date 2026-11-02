# Execution evidence

Recorded locally on macOS ARM64, Python 3.12, 2026-11-02. These are snapshots, not promises about future model output.

| Check | Actual outcome |
| --- | --- |
| Workflow unit and integration tests | 17 passed |
| Offline reviewed scenario execution | 11 passed; one deliberately wrong expectation rejected |
| Offline seeded-defect run | 9 passed, 2 failed as intended: zero and atomicity |
| MCP protocol smoke test | Initialized session, discovered 3 tools, read requirement, executed suite, retrieved results |
| Live Ollama qwen3:4b run | 14 scenarios generated; 3 rejected by the specification gate; 11 executed and passed |

## Inspect the evidence

- [Offline draft](offline/draft-report.md): hand-authored simulated model output, no live model call.
- [Seeded defect draft](seeded-defect/draft-report.md): expected failures demonstrate sensitivity to the defect.
- [MCP client result](mcp-smoke.json): actual stdio protocol round trip. The recorded draft path is normalized to a repository-relative path.
- [Live plan](live/plan.json), [live gate](live/review.json), [model review](live/model-review.json), [live results](live/results.json) and [draft report](live/draft-report.md): actual local model output, not a curated replacement.
- [Initial live error](initial-live-failure/error.json): the first attempt stopped before executing scenarios because the review schema's large string bound was rejected by the local grammar engine. The generation adapter now removes string length bounds from the model-facing grammar while retaining full Pydantic response validation. A test protects this boundary.

## What the live result teaches

The analyst incorrectly expected three otherwise valid GBP 0.01 batches to fail. The executable specification rejected those expectations. It also generated redundant questions about facts already supplied in the requirement. Those questions remain visible; they are not all useful clarification requests.

The separate model reviewer was also fallible. It suggested testing other valid currency codes even though the contract permits only GBP. It criticized imported=1 in valid cases even though those cases each contained one payment. Its comments about the missing 101-payment case and broader reference boundaries identify real gaps. Its review is advisory and is neither a release decision nor human sign-off.

The gate's coverage checklist is deliberately small. Eleven passing examples do not establish complete coverage, and the reviewer output should not be copied uncritically into a defect tracker. All recorded reports remain unapproved drafts. No human approval was fabricated and no external report was posted.

## Reproduce

```bash
pytest -q --junitxml=reports/junit.xml
qa-demo run --mode offline
qa-demo run --mode offline --seeded-bug  # intentionally exits 1
python scripts/mcp_smoke.py
qa-demo run --mode ollama --model qwen3:4b
```
