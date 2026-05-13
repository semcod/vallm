"""Shared main function for ollama simple demo examples."""

from __future__ import annotations


def run_demo_main() -> None:
    """Run the standard demo main function pattern."""
    from .load_config import load_config
    from .process_user_input import process_user_input
    from .calculate_total import calculate_total
    from .save_data import save_data

    config = load_config()

    # Process user input
    user_input = input("Enter command: ")
    result = process_user_input(user_input)
    print(f"Result: {result}")

    # Calculate total
    items = [
        {"name": "item1", "price": 10, "quantity": 2},
        {"name": "item2", "price": 20, "quantity": 1},
    ]
    total = calculate_total(items)
    print(f"Total: {total}")

    # Save data
    data = {"result": result, "total": total}
    save_data(data, "output.json")
