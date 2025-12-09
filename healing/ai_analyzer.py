import json
import os
from pathlib import Path
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
import re

# Load .env file if present
load_dotenv()

# Candidate models
MODEL_CANDIDATES = [
    ("mistralai/Mistral-7B-Instruct-v0.2", "chat"),
    ("tiiuae/falcon-rw-1b", "text"),
]

def get_hf_token() -> str:
    token = os.getenv("HUGGINGFACEHUB_API_TOKEN")
    if not token:
        raise RuntimeError("HUGGINGFACEHUB_API_TOKEN not set in environment variables.")
    print("[DEBUG] Hugging Face token loaded")
    return token

def get_inference_client(token: str):
    """
    Try each candidate model until one responds.
    Returns (client, model_name, mode) where mode is 'chat' or 'text'.
    """
    for model_name, mode in MODEL_CANDIDATES:
        try:
            print(f"[DEBUG] Trying model: {model_name} (mode={mode})")
            client = InferenceClient(model=model_name, token=token)

            # Quick sanity check
            if mode == "chat":
                _ = client.chat_completion(messages=[{"role": "user", "content": "Hello"}], max_tokens=5)
            else:
                _ = client.text_generation("Hello", max_new_tokens=5)

            return client, model_name, mode
        except Exception as e:
            print(f"[WARN] Failed with {model_name}: {e}")
            continue
    raise RuntimeError("No available Hugging Face model found.")

def analyze_logs(structured_log_file: str = "logs/structured_logs.json") -> dict:
    Path("logs").mkdir(exist_ok=True)

    if not Path(structured_log_file).exists():
        print(f"[ERROR] Structured log file {structured_log_file} not found.")
        empty_report = {"issues_found": []}
        with open("logs/ai_analysis.json", "w") as f:
            json.dump(empty_report, f, indent=4)
        return empty_report

    with open(structured_log_file, "r") as f:
        data = json.load(f)

    hf_token = get_hf_token()

    try:
        client, model_name, mode = get_inference_client(hf_token)
    except RuntimeError as e:
        print(f"[ERROR] {e}")
        print("[ERROR] No HF model available, switching to mock analysis mode ⚠️")
        client, model_name, mode = None, "mock", "mock"

    logs = [e for e in (data.get("errors", []) or data.get("entries", [])) if e.get("type") == "error"]
    if not logs:
        print("[WARN] No error logs found, writing empty report.")
        report = {"issues_found": []}
        with open("logs/ai_analysis.json", "w") as f:
            json.dump(report, f, indent=4)
        return report

    issues = []
    for err in logs:
        msg = err.get("message", str(err))

        prompt = f"""
You are an AI DevOps assistant.
Analyze this CI/CD error log and provide:
1. Short summary of the issue
2. Suggested fix (one line)
3. Severity (low/medium/high)

Error log: {msg}
"""

        print(f"[DEBUG] Sending prompt to model: {model_name}")
        try:
            if client:
                if mode == "chat":
                    response = client.chat_completion(
                        messages=[{"role": "user", "content": prompt}],
                        max_tokens=200
                    )
                    text = response.choices[0].message["content"]
                else:  # text mode
                    response = client.text_generation(prompt, max_new_tokens=150)
                    text = str(response)
            else:
                raise RuntimeError("Mock mode")

            match = re.search(r"(low|medium|high)", text.lower())
            severity = match.group(1) if match else "medium"

            issues.append({
                "error": msg,
                "suggestion": text.strip(),
                "severity": severity
            })
        except Exception as e:
            print(f"[WARN] Model failed mid-run: {e}")
            issues.append({
                "error": msg,
                "suggestion": "Investigate the error and check system logs.",
                "severity": "medium"
            })

    report = {"issues_found": issues}
    with open("logs/ai_analysis.json", "w") as f:
        json.dump(report, f, indent=4)

    print(f"[INFO] AI analysis report generated: logs/ai_analysis.json with {len(issues)} issues")
    return report

def run_analysis():
    """Wrapper used by test cases to execute the analyzer."""
    return analyze_logs("logs/structured_logs.json")

if __name__ == "__main__":
    analyze_logs()
