import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from .fixture import submit_batch
from .models import Plan, Review
from .providers import generate, independent_review
from .review import review_plan

ROOT = Path(__file__).resolve().parents[1]


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def run_path(run_id, root=None):
    if not re.fullmatch(r"[a-f0-9]{12}", run_id):
        raise ValueError("Invalid run id")
    return (root or ROOT / "runs") / run_id


def run(
    mode="offline",
    model="qwen3:4b",
    base_url="http://127.0.0.1:11434",
    seeded_bug=False,
    root=None,
):
    requirement = (ROOT / "requirements/change-request.md").read_text()
    run_id = uuid4().hex[:12]
    folder = run_path(run_id, root)
    folder.mkdir(parents=True)
    save(
        folder / "metadata.json",
        {
            "run_id": run_id,
            "mode": mode,
            "model": model if mode == "ollama" else None,
            "started_at": datetime.now(timezone.utc).isoformat(),
            "seeded_bug": seeded_bug,
            "requirement_sha256": hashlib.sha256(requirement.encode()).hexdigest(),
        },
    )
    (folder / "requirement.md").write_text(requirement)
    try:
        if mode == "offline":
            plan = Plan.model_validate_json(
                (ROOT / "examples/offline-plan.json").read_text()
            )
            advice = Review(
                concerns=[
                    "Offline fixture deliberately contains an incorrect expected result for zero."
                ],
                summary="Hand-authored simulated model output. No AI model was called.",
            )
        elif mode == "ollama":
            plan = generate(requirement, model, base_url)
            save(folder / "plan.json", plan.model_dump())
            advice = independent_review(requirement, plan, model, base_url)
        else:
            raise ValueError("Unknown mode")
        save(folder / "plan.json", plan.model_dump())
        save(folder / "model-review.json", advice.model_dump())
        accepted, gate = review_plan(plan)
        save(folder / "review.json", gate)
        if not gate["executable"]:
            raise ValueError(
                "Missing mandatory coverage: " + ", ".join(gate["missing_coverage"])
            )
        results = []
        for case in accepted:
            actual = submit_batch(
                [p.model_dump() for p in case.payments], seeded_bug=seeded_bug
            )
            wanted = {
                "status": case.expected_status,
                "imported": case.expected_imported,
            }
            results.append(
                {
                    "id": case.id,
                    "requirement": case.requirement,
                    "expected": wanted,
                    "actual": actual,
                    "passed": actual == wanted,
                }
            )
        save(folder / "results.json", results)
        lines = [
            "# Draft QA report",
            f"Run: {run_id}",
            f"Mode: {mode}",
            f"Seeded defect enabled: {seeded_bug}",
            "Status: awaiting human review; no external publishing is implemented.",
            f"Passed: {sum(r['passed'] for r in results)}/{len(results)}",
            "",
            "## Model review",
            advice.summary,
            *["- " + c for c in advice.concerns],
            "",
            "## Open questions",
            *["- " + q for q in plan.questions],
            "",
            "## Test results",
            *[
                "- "
                + r["id"]
                + ": "
                + ("PASS" if r["passed"] else "FAIL")
                + " expected "
                + json.dumps(r["expected"])
                + " actual "
                + json.dumps(r["actual"])
                for r in results
            ],
            "",
            "## Rejected suggestions",
            *[f"- {r['id']}: {r['reason']}" for r in gate["rejected"]],
        ]
        (folder / "draft-report.md").write_text("\n\n".join(lines) + "\n")
        return {
            "run_id": run_id,
            "mode": mode,
            "passed": sum(r["passed"] for r in results),
            "total": len(results),
            "rejected": len(gate["rejected"]),
            "draft": str(folder / "draft-report.md"),
        }
    except Exception as exc:
        save(folder / "error.json", {"error": str(exc), "type": type(exc).__name__})
        raise


def evidence_digest(folder):
    digest = hashlib.sha256()
    for name in [
        "metadata.json",
        "requirement.md",
        "plan.json",
        "model-review.json",
        "review.json",
        "results.json",
        "draft-report.md",
    ]:
        digest.update(name.encode())
        digest.update((folder / name).read_bytes())
    return digest.hexdigest()


def approve(run_id, reviewer, root=None):
    folder = run_path(run_id, root)
    if not reviewer.strip():
        raise ValueError("Reviewer name required")
    digest = evidence_digest(folder)
    save(
        folder / "approval.json",
        {
            "reviewer": reviewer,
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "sha256": digest,
        },
    )
    return digest


def export_approved(run_id, root=None):
    folder = run_path(run_id, root)
    approval = json.loads((folder / "approval.json").read_text())
    if approval["sha256"] != evidence_digest(folder):
        raise ValueError("Evidence changed since approval; review again")
    # Local-only export: no GitHub, Slack or issue-tracker write API exists.
    destination = folder / "approved-report.md"
    destination.write_text(
        "Reviewed by "
        + approval["reviewer"]
        + "\n\n"
        + (folder / "draft-report.md").read_text()
    )
    return str(destination)
