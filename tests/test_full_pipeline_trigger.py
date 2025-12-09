import sys
import json
import traceback
import subprocess
import difflib
from pathlib import Path
from datetime import datetime
from healing import code_suggester

# === Directories ===
BUGGY_CODE_DIR = Path("buggy_examples")
FIXED_CODE_DIR = Path("fixed_examples")
LOG_DIR = Path("logs/self_healing")

# Ensure directories exist
BUGGY_CODE_DIR.mkdir(exist_ok=True)
FIXED_CODE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# === Utility: Run a Python file ===
def run_python_file(path: Path):
    """Run a Python file and return (success, output_or_error)."""
    try:
        result = subprocess.run(
            [sys.executable, str(path)],
            capture_output=True,
            text=True,
            timeout=15
        )
        if result.returncode != 0:
            raise Exception(result.stderr or result.stdout)
        return True, result.stdout.strip()
    except Exception as e:
        err_msg = str(e) or traceback.format_exc()
        return False, err_msg


# === Utility: Show code diff ===
def show_diff(original: str, suggestion: str):
    """Display a clean unified diff between original and suggested code."""
    diff = difflib.unified_diff(
        original.splitlines(),
        suggestion.splitlines(),
        fromfile="original",
        tofile="suggested",
        lineterm=""
    )
    diff_text = "\n".join(diff)
    if diff_text.strip():
        print("\n=== DIFF PREVIEW (original → suggested) ===")
        print(diff_text)
        print("=============================================\n")


# === Core: Test & Auto-heal one file ===
def run_and_heal_code(file_path: Path):
    """Test and auto-heal a single Python file (non-interactive)."""
    print(f"\n--- Testing: {file_path.name} ---")
    original_code = file_path.read_text(encoding="utf-8")

    success, output = run_python_file(file_path)
    if success:
        print(f"✓ {file_path.name} passed successfully.\n")
        return {"file": file_path.name, "status": "passed_initially"}

    print(f"Error detected in {file_path.name}. Invoking AI fixer...\n")
    suggestion, explanation = code_suggester.suggest_code_fix(output, original_code)

    show_diff(original_code, suggestion)
    print(f"AI Explanation: {explanation}\n")

    fixed_file = FIXED_CODE_DIR / file_path.name
    fixed_file.write_text(suggestion, encoding="utf-8")
    print(f"AI fix saved to: {fixed_file}")

    # Test fixed file
    fixed_success, fixed_output = run_python_file(fixed_file)
    final_status = "passed_after_fix" if fixed_success else "failed_after_fix"

    return {
        "file": file_path.name,
        "initial_error": output[:300],
        "ai_explanation": explanation,
        "final_status": final_status,
        "final_output": (fixed_output or "")[:300]
    }


# === Main: Run healing pipeline ===
def run_self_healing():
    """Run self-healing tests on all buggy code files."""
    results = []
    for py_file in BUGGY_CODE_DIR.glob("*.py"):
        result = run_and_heal_code(py_file)
        results.append(result)

    log_path = LOG_DIR / f"self_healing_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

    print(f"\nSelf-healing run complete. Results saved to {log_path}")


# === Entry Point ===
if __name__ == "__main__":
    run_self_healing()
