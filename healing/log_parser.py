import re
import json
from pathlib import Path
from datetime import datetime

def parse_pipeline_logs(log_file: str) -> list:
    """Parse pipeline logs for errors"""
    errors = []
    log_path = Path(log_file)

    if not log_path.exists():
        print(f"[WARN] Pipeline log file {log_file} not found.")
        return errors

    with open(log_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        # Skip auto-fix chatter inside pipeline logs
        if "[AUTO-FIX]" in line:
            continue

        if "ERROR" in line or "Exception" in line or "failed" in line.lower():
            errors.append({
                "timestamp": str(datetime.now()),
                "type": "error",
                "message": line.strip()
            })
    return errors


def parse_auto_fix_logs(log_file: str) -> list:
    """Parse auto_fix.log for applied fixes (tagged as type=fix)"""
    fixes = []
    log_path = Path(log_file)

    if not log_path.exists():
        print(f"[WARN] Auto-fix log file {log_file} not found.")
        return fixes

    with open(log_path, "r") as f:
        lines = f.readlines()

    for line in lines:
        parts = line.strip().split(" ", 2)
        if len(parts) >= 2:
            timestamp = parts[0] + " " + parts[1]
        else:
            timestamp = str(datetime.now())

        fixes.append({
            "timestamp": timestamp,
            "type": "fix",
            "message": line.strip()
        })
    return fixes


def parse_logs(pipeline_log_dir="logs/pipeline_logs", output_file="logs/structured_logs.json"):
    structured_data = {"entries": []}

    # Parse raw pipeline logs
    pipeline_dir = Path(pipeline_log_dir)
    if pipeline_dir.exists() and pipeline_dir.is_dir():
        for file in pipeline_dir.glob("*.log"):
            structured_data["entries"].extend(parse_pipeline_logs(file))
    else:
        print(f"[WARN] No pipeline logs found in {pipeline_log_dir}")

    # Parse auto_fix.log (kept separately as type=fix)
    auto_fix_log = pipeline_dir / "auto_fix.log"
    structured_data["entries"].extend(parse_auto_fix_logs(auto_fix_log))

    # Save structured data
    Path("logs").mkdir(exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(structured_data, f, indent=4)

    print(f"[INFO] Structured logs written to {output_file}")
    return structured_data


if __name__ == "__main__":
    parse_logs()
