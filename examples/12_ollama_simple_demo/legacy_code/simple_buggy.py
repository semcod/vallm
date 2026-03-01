"""
Simple buggy code for demonstration.
Contains obvious issues for Ollama to fix.
"""

import os
import json

# Global variable - bad practice
data_cache = {}

def process_user_input(user_input):
    """Process user input with security issues."""
    # Security vulnerability: eval usage
    if user_input.startswith('calc:'):
        calculation = user_input[5:]
        result = eval(calculation)  # DANGEROUS!
        return result
    
    # SQL injection vulnerability
    if user_input.startswith('search:'):
        query = user_input[7:]
        sql = f"SELECT * FROM users WHERE name = '{query}'"
        print(f"Executing: {sql}")
        return sql
    
    return "processed"

def load_config():
    """Load configuration with eval."""
    config_str = os.environ.get('CONFIG', '{}')
    return eval(config_str)  # DANGEROUS!

def save_data(data, filename):
    """Save data without validation."""
    # No error handling
    with open(filename, 'w') as f:
        json.dump(data, f)
    
    # Command injection vulnerability
    command = f"chmod 644 {filename}"
    os.system(command)

def calculate_total(items):
    """Calculate total with no error handling."""
    total = 0
    for item in items:
        # No type checking
        total += item['price'] * item['quantity']
    return total

def duplicate_function():
    """This is a duplicate function."""
    return "duplicate"

def duplicate_function():
    """Another duplicate function."""
    return "duplicate again"

def unused_function():
    """This function is never used."""
    pass

class BadClass:
    """Class with multiple issues."""
    
    def __init__(self):
        self.data = []
        self.more_data = []
        self.even_more_data = []
        self.unused_var = "never used"
    
    def process_data(self, data):
        """Method with no error handling."""
        # Deep nesting
        if data:
            if isinstance(data, list):
                for item in data:
                    if 'type' in item:
                        if item['type'] == 'user':
                            if 'name' in item:
                                if item['name']:
                                    self.data.append(item)
        return self.data
    
    def another_method(self):
        """Another method with issues."""
        pass

def main():
    """Main function with problems."""
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
