import json
import pytest
from pydantic import ValidationError
from qa_workflow.models import Plan
from qa_workflow.review import review_plan
from qa_workflow.workflow import ROOT, run, run_path, approve, export_approved


def plan():
    return Plan.model_validate_json((ROOT / "examples/offline-plan.json").read_text())


def test_wrong_model_assumption_rejected():
    accepted, review = review_plan(plan())
    assert review["executable"]
    assert review["rejected"] == [
        {
            "id": "wrong-ai-assumption",
            "reason": "Expected result contradicts the executable specification",
        }
    ]
    assert len(accepted) == 11


def test_missing_coverage_blocks_execution():
    p = plan()
    p.scenarios = [s for s in p.scenarios if s.id != "maximum"]
    assert review_plan(p)[1]["missing_coverage"] == ["maximum"]


def test_code_injection_not_part_of_schema():
    data = plan().model_dump()
    data["python"] = 'import os; os.system("echo unsafe")'
    with pytest.raises(ValidationError):
        Plan.model_validate(data)


def test_duplicate_ids_rejected():
    p = plan()
    p.scenarios.append(p.scenarios[0])
    assert review_plan(p)[1]["rejected"][-1]["reason"] == "Duplicate scenario id"


def test_normal_run(tmp_path):
    result = run(root=tmp_path)
    assert result["passed"] == result["total"] == 11
    assert result["rejected"] == 1
    assert not (run_path(result["run_id"], tmp_path) / "approval.json").exists()


def test_seeded_bug_detected(tmp_path):
    result = run(root=tmp_path, seeded_bug=True)
    results = json.loads(
        (run_path(result["run_id"], tmp_path) / "results.json").read_text()
    )
    assert {r["id"] for r in results if not r["passed"]} == {"zero", "atomicity"}


def test_export_requires_approval(tmp_path):
    result = run(root=tmp_path)
    with pytest.raises(FileNotFoundError):
        export_approved(result["run_id"], tmp_path)


def test_approval_bound_to_all_evidence(tmp_path):
    result = run(root=tmp_path)
    rid = result["run_id"]
    approve(rid, "Test reviewer", tmp_path)
    assert "Reviewed by Test reviewer" in open(export_approved(rid, tmp_path)).read()
    (run_path(rid, tmp_path) / "results.json").write_text("[]")
    with pytest.raises(ValueError, match="changed"):
        export_approved(rid, tmp_path)


@pytest.mark.parametrize("rid", ["../secrets", "/etc/passwd", "a" * 13, ""])
def test_run_id_traversal_rejected(rid):
    with pytest.raises(ValueError):
        run_path(rid)


def test_schema_wrong_types():
    data = plan().model_dump()
    data["scenarios"][0]["expected_imported"] = "1"
    with pytest.raises(ValidationError):
        Plan.model_validate(data)
