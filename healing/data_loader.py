import json
import traceback
from pathlib import Path
from healing.code_suggester import suggest_code_fix
from datetime import datetime
import time
import pandas as pd


LOG_FILE = Path("logs/structured_logs.json")


def log_event(event_type, message):
    """Appends a new structured log entry."""
    if not LOG_FILE.exists():
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "w") as f:
            json.dump({"entries": []}, f, indent=4)

    with open(LOG_FILE, "r") as f:
        data = json.load(f)

    entry = {
        "timestamp": str(datetime.now()),
        "type": event_type,
        "message": message,
    }
    data["entries"].append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_logs(log_path="logs/structured_logs.json"):
    """Load logs from JSON into a DataFrame."""
    path = Path(log_path)
    if not path.exists():
        return pd.DataFrame()
    with open(path, "r") as f:
        data = json.load(f)
    df = pd.DataFrame(data.get("entries", []))
    
    # Convert timestamp column to datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


def run_self_healing_tests():
    print("Running AI Self-Healing Tests...")
    test_files = list(Path("tests").glob("test_*.py"))

    for test_file in test_files:
        try:
            print(f"Running test: {test_file.name}")
            exec(open(test_file).read())  # Simulate pytest run
            log_event("test_run", f"{test_file.name} ran successfully")

        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"Test failed: {test_file.name}\n{error_trace}")
            log_event("error", error_trace)

            print("Invoking AI code correction module...")
            suggestion = suggest_code_fix(test_file, str(e))
            if suggestion:
                log_event("ai_fix", f"Fix suggested for {test_file.name}: {suggestion[:200]}")
            else:
                log_event("ai_fix_failed", f"No fix found for {test_file.name}")

    print("\nUpdating live error analytics...")
    df = load_logs(str(LOG_FILE))
    print(df.tail(5))  # Show latest entries


if __name__ == "__main__":
    while True:
        run_self_healing_tests()
        print("Waiting 30 seconds before next test cycle...\n")
        time.sleep(30)
