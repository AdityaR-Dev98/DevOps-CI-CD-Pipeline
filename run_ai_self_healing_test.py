import sys
import json
import traceback
import subprocess
import difflib
from pathlib import Path
from datetime import datetime
from healing import code_suggester
import os

# === Directories ===
BUGGY_CODE_DIR = Path("buggy_examples")
FIXED_CODE_DIR = Path("fixed_examples")
LOG_DIR = Path("logs/self_healing")

LOG_DIR.mkdir(parents=True, exist_ok=True)
BUGGY_CODE_DIR.mkdir(exist_ok=True)
FIXED_CODE_DIR.mkdir(exist_ok=True)


def run_python_file(path: Path, input_data: str = None):
    """
    Runs a Python file and returns (success: bool, output_or_error: str).
    Handles cases where input() or missing files cause crashes.
    """
    try:
        # Create dummy files if needed (prevents FileNotFoundError)
        content = path.read_text(encoding="utf-8")
        if "nonexistent_file.txt" in content and not Path("nonexistent_file.txt").exists():
            Path("nonexistent_file.txt").write_text("dummy data", encoding="utf-8")
        if "config.json" in content and not Path("config.json").exists():
            Path("config.json").write_text("{}", encoding="utf-8")

        # Handle scripts requiring input()
        result = subprocess.run(
            [sys.executable, str(path)],
            input=input_data or "TestUser\n",
            capture_output=True,
            text=True,
            timeout=15
        )

        if result.returncode != 0:
            raise Exception(result.stderr or result.stdout)
        return True, result.stdout.strip()

    except subprocess.TimeoutExpired:
        return False, f"Timeout: {path.name} took too long to execute."
    except Exception as e:
        tb = traceback.format_exc()
        return False, str(e) if str(e) else tb


def show_diff(original: str, suggestion: str):
    """Displays a clean unified diff of changes."""
    diff = difflib.unified_diff(
        original.splitlines(),
        suggestion.splitlines(),
        fromfile="original",
        tofile="AI_suggested_fix",
        lineterm=""
    )
    diff_text = "\n".join(diff)
    if diff_text.strip():
        print("\n=== DIFF PREVIEW (original → suggested) ===")
        print(diff_text)
        print("=============================================\n")


def run_and_heal_code(file_path: Path):
    """
    Tests and attempts to heal a single buggy Python file.
    Returns structured result for dashboard/logging.
    """
    print(f"\n--- Testing: {file_path.name} ---")

    original_code = file_path.read_text(encoding="utf-8")
    success, output = run_python_file(file_path)

    if success:
        print(f"✓ {file_path.name} passed successfully.\n")
        return {
            "file": file_path.name,
            "status": "passed_initially",
            "ai_explanation": "",
            "final_output": output[:300]
        }

    print(f"Error detected in {file_path.name}:\n{output[:200]}\nInvoking AI fixer...\n")

    suggestion, explanation = code_suggester.suggest_code_fix(output, original_code)

    if not suggestion:
        print(f"AI did not generate a valid fix for {file_path.name}")
        return {
            "file": file_path.name,
            "status": "no_fix_generated",
            "initial_error": output[:300],
            "ai_explanation": "",
        }

    show_diff(original_code, suggestion)

    fixed_file = FIXED_CODE_DIR / file_path.name
    fixed_file.write_text(suggestion, encoding="utf-8")

    print(f"AI fix saved to: {fixed_file}")
    fixed_success, fixed_output = run_python_file(fixed_file)

    final_status = "passed_after_fix" if fixed_success else "failed_after_fix"

    print(f"{file_path.name} final status: {final_status}\n")

    return {
        "file": file_path.name,
        "initial_error": output[:300],
        "ai_explanation": explanation,
        "final_status": final_status,
        "final_output": (fixed_output or "")[:300],
    }


def run_self_healing():
    """Runs AI self-healing tests on all buggy files."""
    results = []
    print("\n=== Starting AI Self-Healing Run ===\n")

    for py_file in sorted(BUGGY_CODE_DIR.glob("*.py")):
        result = run_and_heal_code(py_file)
        results.append(result)

    log_path = LOG_DIR / f"self_healing_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"\nSelf-healing run complete. Results saved to: {log_path}")
    return log_path


if __name__ == "__main__":
    run_self_healing()
