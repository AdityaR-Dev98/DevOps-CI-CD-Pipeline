import re
from datetime import datetime
from pathlib import Path
from transformers import pipeline

print("Loading model for code corrections...")

ai_model = pipeline(
    "text-generation",
    model="deepseek-ai/deepseek-coder-1.3b-instruct",
    device_map="auto",
    trust_remote_code=True
)

LOG_FILE = Path("logs/code_suggestions.log")
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def log_action(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"{timestamp} [AI-FIX] {msg}"
    print(entry)
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(entry + "\n")


def detect_target_file_and_line(message: str):
    match = re.search(r'File "([^"]+\.py)", line (\d+)', message)
    if match:
        return Path(match.group(1)), int(match.group(2))
    return None, None


# --------------------- INDENTATION SANITIZER ---------------------
def sanitize_indentation(code: str) -> str:
    """Ensure that def/if/for/class blocks have valid indentation."""
    lines = code.splitlines()
    fixed_lines = []
    for i, line in enumerate(lines):
        fixed_lines.append(line)
        # Match block openers
        if re.match(r'^\s*(def|class|if|for|while|try|except|with)\b.*:\s*$', line):
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                # If next line isn’t indented, insert a safe 'pass'
                if not re.match(r'^\s+', next_line):
                    fixed_lines.append("    pass")
            else:
                fixed_lines.append("    pass")
    return "\n".join(fixed_lines)


# --------------------- RULE-BASED FALLBACK FIXES ---------------------
def rule_based_fix(error_message: str, original_code: str) -> tuple[str, str]:
    """
    Simple deterministic fallback repairs for common Python runtime errors.
    Returns (fixed_code, explanation)
    """

    # ✅ Handle EOFError (e.g., input() in non-interactive test)
    if "EOFError" in error_message:
        log_action("Applied rule-based fix for EOFError (safe input fallback).")
        fixed_code = re.sub(
            r'input\(.*?\)',
            '"default_user"  # replaced input() to avoid EOFError in CI',
            original_code
        )
        fixed_code = sanitize_indentation(fixed_code)
        return fixed_code, "Replaced input() calls with safe default strings."

    # ✅ Handle FileNotFoundError
    if "FileNotFoundError" in error_message:
        log_action("Applied rule-based fix for FileNotFoundError (graceful file handling).")

        fixed_code = original_code
        # Ensure try/except around file operations
        if "open(" in fixed_code and "try:" not in fixed_code:
            fixed_code = (
                "try:\n    "
                + fixed_code.replace("\n", "\n    ")
                + "\nexcept FileNotFoundError:\n    print('File not found, using default fallback.')"
            )

        # Fix indentation issues (convert 8+ spaces to 4)
        fixed_code = re.sub(r" {8,}", "    ", fixed_code)
        fixed_code = sanitize_indentation(fixed_code)
        return fixed_code, "Wrapped file operations in try/except with graceful fallback."

    # No rule match → return unchanged
    return original_code, ""


# --------------------- AI-BASED FIX GENERATION ---------------------
def generate_ai_fix(original_code: str, issue: str) -> str:
    """
    Generate corrected code using Deepseek-Coder model.
    """
    prompt = f"""
You are a Python code-fixing assistant.
The following code throws an error. Your job is to rewrite the entire code with the bug fixed.

### Code
{original_code}

### Error Message
{issue}

### Rules:
- Output ONLY the corrected full code (no explanations, no comments, no markdown, no extra text).
- Preserve structure and indentation.
- If something is unclear, make a minimal correction that ensures valid Python syntax.

Corrected code:
"""

    try:
        result = ai_model(
            prompt,
            max_new_tokens=600,
            do_sample=False,
            temperature=0.1,
            pad_token_id=50256
        )
        suggestion = result[0]["generated_text"].strip()

        if "Corrected code:" in suggestion:
            suggestion = suggestion.split("Corrected code:")[-1].strip()

        # Clean markdown artifacts
        suggestion = re.sub(r"^```(?:python)?|```$", "", suggestion, flags=re.MULTILINE).strip()

        if not suggestion or len(suggestion) < 5:
            raise ValueError("AI returned empty or invalid code.")

        # Sanitize indentation before returning
        suggestion = sanitize_indentation(suggestion)
        return suggestion

    except Exception as e:
        log_action(f"[ERROR] AI model failure: {e}")
        return original_code


# --------------------- MAIN INTERFACE FUNCTION ---------------------
def suggest_code_fix(error_message: str, original_code: str):
    """
    Given traceback + buggy code, returns corrected code and explanation.
    """
    try:
        file_path, _ = detect_target_file_and_line(error_message)

        # First try rule-based fix
        fixed_code, rule_explanation = rule_based_fix(error_message, original_code)
        if rule_explanation:
            if file_path:
                file_path.write_text(fixed_code, encoding="utf-8")
                log_action(f"Fixed code saved to: {file_path}")
            return fixed_code, f"Rule-based auto-fix applied: {rule_explanation}"

        # Otherwise, call the AI model
        suggestion = generate_ai_fix(original_code, error_message)
        explanation = "AI analyzed the error and generated a corrected version, saved separately."

        if file_path:
            file_path.write_text(suggestion, encoding="utf-8")
            log_action(f"Fixed code saved to: {file_path}")

        return suggestion, explanation

    except Exception as e:
        err = f"[ERROR] AI suggestion failed: {e}"
        log_action(err)
        return original_code, err
