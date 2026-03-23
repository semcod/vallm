"""
Refactored code for demonstration.
Fixed issues and improved quality.
"""

import os
import json
from typing import List, Dict, Any

# Global variable - bad practice
data_cache = {}

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
    from .utils import run_demo_main
    run_demo_main()

if __name__ == "__main__":
    main()