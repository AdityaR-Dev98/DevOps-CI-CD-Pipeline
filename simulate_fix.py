import json
from pathlib import Path
from datetime import datetime

file = Path("logs/structured_logs.json")
if not file.exists():
    raise FileNotFoundError("Run log_parser.py first to generate structured_logs.json")

with open(file, "r") as f:
    data = json.load(f)

# Add a fake fix entry
data["entries"].append({
    "timestamp": str(datetime.now()),
    "type": "fix",
    "message": "Dummy fix applied: rollback dependency"
})

# Save back
with open(file, "w") as f:
    json.dump(data, f, indent=4)

print("[INFO] Added dummy fix entry to structured_logs.json")
