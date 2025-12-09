import subprocess
from pathlib import Path
from datetime import datetime
from healing.code_suggester import suggest_code_fix
import shutil
import os
import pytest
import webbrowser

LOG_DIR = Path("logs")
TEMP_FIX_DIR = Path("temp_fixes")
LOG_FILE = LOG_DIR / "auto_fix_test.log"

LOG_DIR.mkdir(parents=True, exist_ok=True)
TEMP_FIX_DIR.mkdir(exist_ok=True)

def log(message: str):
    """Write log message with timestamp."""
    entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [TEST] {message}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    print(entry.strip())

def run_script(script_path: str):
    """Run a Python script and capture its output."""
    return subprocess.run(
        ["python", script_path],
        capture_output=True,
        text=True
    )

def auto_fix(script_path: str):
    """Attempt to fix a buggy Python script using AI suggestions."""
    result = run_script(script_path)
    if result.returncode == 0:
        log(f"{script_path} ran successfully — no fix needed.")
        return True

    error_msg = result.stderr or result.stdout
    log(f"Error detected in {script_path}:\n{error_msg}")

    original_code = Path(script_path).read_text(encoding="utf-8")
    fixed_code, explanation = suggest_code_fix(error_msg, original_code)

    if not fixed_code:
        log("AI did not return a valid fix. Skipping.")
        return False

    fixed_path = TEMP_FIX_DIR / f"fixed_{Path(script_path).name}"
    with open(fixed_path, "w", encoding="utf-8") as f:
        f.write(fixed_code)

    log(f"AI fix written to temporary file: {fixed_path}")
    log(f"Explanation: {explanation}")

    test_result = run_script(fixed_path)
    if test_result.returncode == 0:
        log(f"Fix validated successfully for {script_path}")
        return True
    else:
        log(f"Fix test failed for {script_path}:\n{test_result.stderr or test_result.stdout}")
        return False


# ----------------------------
# Pytest Test Function
# ----------------------------

buggy_files = [
    "buggy_examples/buggy1_syntax_error.py",
    "buggy_examples/buggy2_zero_division.py",
    "buggy_examples/buggy3_name_error.py",
    "buggy_examples/buggy4_import_error.py",
    "buggy_examples/buggy5_file_handling.py",
    "buggy_examples/buggy6_logic_error.py",
    "buggy_examples/buggy7_type_error.py",
    "buggy_examples/buggy8_api_call.py",
    "buggy_examples/buggy9_class_inheritance.py",
]

@pytest.mark.parametrize("file_path", buggy_files)
def test_auto_fix(file_path):
    """Pytest-compatible wrapper for auto-fixing buggy scripts."""
    path = Path(file_path)
    if not path.exists():
        pytest.skip(f"File not found: {file_path}")
    log(f"\n=== Testing {file_path} ===")
    assert auto_fix(file_path)


# ----------------------------
# Hook: After All Tests
# ----------------------------

def pytest_sessionfinish(session, exitstatus):
    """Hook to open dashboard after all pytest tests finish."""
    log("All auto-fix tests completed.")
    dashboard_path = Path("dashboard/index.html").resolve()
    if dashboard_path.exists():
        log("Opening AI Auto-Fix Dashboard in browser...")
        webbrowser.open(f"file://{dashboard_path}")
    else:
        log("Dashboard not found. Skipping browser launch.")
