"""Shared utility for extracting code from LLM responses."""

from __future__ import annotations

import re


def extract_code_from_response(response: str) -> str:
    """Extract Python code from LLM response.
    
    Args:
        response: Raw response string from LLM
        
    Returns:
        Extracted code block or original response if no code found
    """
    # Look for python code blocks
    pattern = r'```python\s*(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # Try generic code blocks
    pattern = r'```\s*(.*?)```'
    matches = re.findall(pattern, response, re.DOTALL)
    
    if matches:
        return matches[0].strip()
    
    # Return whole response if no code blocks found
    return response.strip()
