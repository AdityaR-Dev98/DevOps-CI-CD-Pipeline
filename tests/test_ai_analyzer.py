import json
import builtins
from pathlib import Path
import healing.auto_fix as autofix

def test_pipeline_ai_integration(monkeypatch, tmp_path):
    """Simulate full CI/CD pipeline triggering an AI suggestion."""

    structured = tmp_path / "structured_logs.json"
    structured.write_text(json.dumps({
        "entries": [{"message": "Unhandled pipeline failure in step XYZ"}]
    }))

    rules = tmp_path / "recovery_rules.json"
    rules.write_text(json.dumps({}))

    monkeypatch.setattr(autofix, "load_rules", lambda: json.loads(rules.read_text()))
    autofix.LOG_FILE = tmp_path / "auto_fix.log"

    class DummyModel:
        def __call__(self, prompt, **kwargs):
            return [{"generated_text": "Add try-except block around the failure step"}]

    from healing import code_suggester
    monkeypatch.setattr(code_suggester, "ai_model", DummyModel())

    monkeypatch.setattr(builtins, "input", lambda _: "y")
    autofix.run_auto_fix()

    log_text = autofix.LOG_FILE.read_text()
    assert "AI Suggestion" in log_text
    assert "AI Explanation" in log_text
    assert "User accepted AI suggestion" in log_text
