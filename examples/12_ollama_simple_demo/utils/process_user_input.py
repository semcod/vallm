"""Shared process_user_input function for ollama demo examples."""

from __future__ import annotations


def process_user_input(user_input: str) -> str:
    """Process user input with standard logic.

    Args:
        user_input: Raw user input string

    Returns:
        Processed result string
    """
    if not user_input:
        return "No input provided"

    # Handle calculation commands
    if user_input.startswith("calc:"):
        calculation = user_input[5:]
        try:
            result = eval(calculation)
        except Exception as e:
            return f"Error in calculation: {e}"
        return str(result)

    # Handle search commands
    if user_input.startswith("search:"):
        query = user_input[7:]
        sql = "SELECT * FROM users WHERE name = ?"
        # Use parameterized queries to prevent SQL injection
        print(f"Executing: {sql} with query '{query}'")
        return sql

    # Basic processing logic for other commands
    if user_input.lower() == "help":
        return "Available commands: status, list, exit, calc:<expression>, search:<query>"
    elif user_input.lower() == "status":
        return "System is running"
    elif user_input.lower() == "list":
        return "Items: item1, item2, item3"
    elif user_input.lower() == "exit":
        return "Goodbye!"
    else:
        return f"Unknown command: {user_input}"
