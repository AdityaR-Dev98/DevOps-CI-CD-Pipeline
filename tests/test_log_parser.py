import json
from pathlib import Path

def parse_logs(input_path: Path):
    """Parse raw logs and generate structured JSON output."""
    lines = input_path.read_text().splitlines()
    entries = []

    for line in lines:
        if "ERROR" in line:
            entries.append({"type": "error", "message": line})
        elif "AUTO-FIX" in line or "FIX" in line:
            entries.append({"type": "fix", "message": line})

    structured = {"entries": entries}
    output_path = input_path.parent / "structured_logs.json"
    output_path.write_text(json.dumps(structured, indent=4))
    return output_path
