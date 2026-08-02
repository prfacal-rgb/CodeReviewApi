from features.code_review.models import SuggestionItem

SYSTEM_PROMPT = """
You are a senior developer explaining a code issue to a junior developer.
Given a code suggestion, respond with a JSON object (no markdown) with this exact
structure:

{
  "why_it_matters": "Why this issue is important in production",
  "detailed_explanation": "Step by step explanation of the problem",
  "example_fix": "Corrected code snippet showing the fix",
  "references": ["relevant concept or doc link 1", "relevant concept 2"]
}
"""


def build_prompt(suggestion: SuggestionItem, code: str, language: str) -> str:
    return f"""Language: {language}

                Original code:
                {code}

                Suggestion to explain:
                - Severity: {suggestion.severity}
                - Category: {suggestion.category}
                - Issue: {suggestion.description}

                Explain this suggestion in detail."""
