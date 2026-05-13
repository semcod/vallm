from typing import Dict, Any

MOCK_LLM_RESPONSES = {
    "good_code": {
        "verdict": "pass",
        "score": 0.9,
        "reasoning": "Code is well-structured and follows best practices.",
    },
    "bad_code": {
        "verdict": "review",
        "score": 0.3,
        "reasoning": "Code has potential issues and could be improved.",
    },
    "syntax_error": {"verdict": "fail", "score": 0.1, "reasoning": "Code contains syntax errors."},
}


class MockLLMProvider:
    def __init__(self, responses: Dict[str, Any] = None):
        self.responses = responses or MOCK_LLM_RESPONSES
        self.call_count = 0

    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        self.call_count += 1
        if "def invalid_syntax" in code:
            return self.responses["syntax_error"]
        elif "print(" in code and "input(" in code:
            return self.responses["bad_code"]
        else:
            return self.responses["good_code"]

    def is_available(self) -> bool:
        return True
