"""Code extraction utilities for LLM responses."""

import re
from typing import Optional


def extract_code_from_response(response: str, language: str = "python") -> str:
    """Extract code from LLM response.
    
    Handles various response formats:
    - Markdown code blocks (```python ... ```)
    - Plain text with code
    - Multiple code blocks (returns first one)
    
    Args:
        response: LLM response text
        language: Expected programming language
        
    Returns:
        Extracted code string or empty string if no code found
    """
    if not response:
        return ""
    
    # Try to find code blocks with language marker
    pattern = rf"```{language}\s*\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return matches[0].strip()
    
    # Try generic code block
    pattern = r"```\s*\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        return matches[0].strip()
    
    # If no code blocks, return the whole response (stripped)
    return response.strip()


def extract_json_from_response(response: str) -> Optional[dict]:
    """Extract JSON object from LLM response.
    
    Args:
        response: LLM response text
        
    Returns:
        Parsed JSON dict or None if extraction fails
    """
    import json
    
    if not response:
        return None
    
    # Try to find JSON in code blocks
    pattern = r"```json\s*\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0].strip())
        except json.JSONDecodeError:
            pass
    
    # Try to find JSON in generic code blocks
    pattern = r"```\s*\n(.*?)```"
    matches = re.findall(pattern, response, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match.strip())
        except json.JSONDecodeError:
            continue
    
    # Try to parse the entire response as JSON
    try:
        return json.loads(response.strip())
    except json.JSONDecodeError:
        pass
    
    return None
