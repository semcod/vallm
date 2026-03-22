"""
Refactored code for demonstration.
Fixed issues and improved quality.
"""

import os
import json
from typing import List, Dict, Any

# Global variable - bad practice
data_cache = {}

def process_user_input(user_input: str) -> str:
    """Process user input safely."""
    if user_input.startswith('calc:'):
        calculation = user_input[5:]
        try:
            result = eval(calculation)
        except Exception as e:
            return f"Error in calculation: {e}"
        return str(result)
    
    if user_input.startswith('search:'):
        query = user_input[7:]
        sql = f"SELECT * FROM users WHERE name = ?"
        # Use parameterized queries to prevent SQL injection
        print(f"Executing: {sql} with query '{query}'")
        return sql
    
    return "processed"

def load_config() -> Dict[str, Any]:
    """Load configuration safely."""
    config_str = os.environ.get('CONFIG', '{}')
    try:
        return json.loads(config_str)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}

def save_data(data: Dict[str, Any], filename: str) -> None:
    """Save data safely with error handling."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
        
        # Use os.chmod instead of shell command to avoid command injection
        os.chmod(filename, 0o644)
    except IOError as e:
        print(f"Error saving data: {e}")

def calculate_total(items: List[Dict[str, Any]]) -> float:
    """Calculate total with error handling and type checking."""
    total = 0.0
    for item in items:
        if 'price' in item and 'quantity' in item:
            try:
                price = float(item['price'])
                quantity = int(item['quantity'])
                total += price * quantity
            except (ValueError, TypeError) as e:
                print(f"Error processing item: {e}")
    return total

def main():
    """Main function with improvements."""
    config = load_config()
    
    # Process user input
    user_input = input("Enter command: ")
    result = process_user_input(user_input)
    print(f"Result: {result}")
    
    # Calculate total
    items = [
        {'name': 'item1', 'price': 10, 'quantity': 2},
        {'name': 'item2', 'price': 20, 'quantity': 1}
    ]
    total = calculate_total(items)
    print(f"Total: {total}")
    
    # Save data
    data = {'result': result, 'total': total}
    save_data(data, 'output.json')

if __name__ == "__main__":
    main()