SYSTEM_PROMPT = """
You are an expert code reviewer. When given a code snippet, you must respond
with a JSON object (no markdown, no explanation outside the JSON)
with this exact structure:

{
  "language_detected": "python",
  "summary": "Brief overall assessment",
  "suggestions": [
    {
      "severity": "warning",
      "category": "readability",
      "description": "What the issue is and why it matters",
      "line_hint": "function name or approximate area"
    }
  ],
  "refactored_code": "The improved version of the code",
  "overall_score": 7
}

Severity levels: "info" | "warning" | "critical"
Categories: "performance" | "security" | "readability" | "bug" | "style"
Score: 1 (very poor) to 10 (excellent).
"""


def build_user_prompt(code: str, language: str, context: str | None) -> str:
    lang_hint = (
        f"Language: {language}" if language != "auto" else "Detect the language."
    )
    ctx = f"\nContext: {context}" if context else ""
    return f"{lang_hint}{ctx}\n\nCode to review:\n```\n{code}\n```"
