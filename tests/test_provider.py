import json
import httpx
import pytest
from pydantic import ValidationError
from qa_workflow import providers, workflow
from qa_workflow.models import Review


def test_generation_schema_preserves_validation_contract():
    original = Review.model_json_schema()
    simplified = providers.generation_schema(original)
    assert "maxLength" not in json.dumps(simplified)
    assert "maxLength" in json.dumps(original)
    assert simplified["additionalProperties"] is False
    with pytest.raises(ValidationError):
        Review.model_validate({"concerns": [], "summary": "x" * 2001})


def test_truncated_model_response_rejected(monkeypatch):
    monkeypatch.setattr(
        providers.httpx,
        "post",
        lambda *a, **kw: httpx.Response(
            200,
            request=httpx.Request("POST", "http://localhost/api/chat"),
            json={"done": True, "done_reason": "length", "message": {"content": "{}"}},
        ),
    )
    with pytest.raises(ValueError, match="incomplete"):
        providers.chat("test", "system", "user", {})


def test_provider_failure_does_not_execute_tests(monkeypatch, tmp_path):
    def unavailable(*args, **kwargs):
        raise httpx.ConnectError("Test provider unavailable")

    monkeypatch.setattr(workflow, "generate", unavailable)
    monkeypatch.setattr(
        workflow,
        "submit_batch",
        lambda *a, **k: pytest.fail("Fixture must not execute"),
    )
    with pytest.raises(httpx.ConnectError):
        workflow.run(mode="ollama", root=tmp_path)
    folders = list(tmp_path.iterdir())
    assert len(folders) == 1
    assert (folders[0] / "error.json").exists()
    assert not (folders[0] / "results.json").exists()


def test_incomplete_plan_does_not_execute(monkeypatch, tmp_path):
    from qa_workflow.models import Plan

    plan = Plan.model_validate_json(
        (workflow.ROOT / "examples/offline-plan.json").read_text()
    )
    plan.scenarios = [s for s in plan.scenarios if s.id != "maximum"]
    monkeypatch.setattr(workflow, "generate", lambda *a: plan)
    monkeypatch.setattr(
        workflow,
        "independent_review",
        lambda *a: Review(concerns=[], summary="Simulated reviewer"),
    )
    monkeypatch.setattr(
        workflow,
        "submit_batch",
        lambda *a, **k: pytest.fail("Fixture must not execute"),
    )
    with pytest.raises(ValueError, match="coverage"):
        workflow.run(mode="ollama", root=tmp_path)
    assert not list(tmp_path.glob("*/results.json"))
