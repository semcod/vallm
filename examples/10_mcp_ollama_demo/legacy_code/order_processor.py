"""
Legacy order processing system with multiple code smells.
This code intentionally contains issues for demonstration purposes.
"""

import json
import os
from datetime import datetime

# Global variable - bad practice
cache = {}

def process_order(data):
    """Process order data - has multiple issues."""
    # Deep nesting - complexity issue
    if data:
        if 'items' in data:
            items = data['items']
            if len(items) > 0:
                for item in items:
                    if 'price' in item:
                        if item['price'] > 0:
                            if 'quantity' in item:
                                if item['quantity'] > 0:
                                    # Calculate total
                                    total = item['price'] * item['quantity']
                                    if total > 100:
                                        # Apply discount
                                        discount = total * 0.1
                                        final = total - discount
                                        return final
    return 0

def load_config():
    """Load config - security issue with eval."""
    # Security vulnerability: eval() usage
    config_str = os.environ.get('CONFIG', '{}')
    return eval(config_str)  # DANGEROUS!

def save_data(data, filename):
    """Save data - uses pickle without validation."""
    import pickle
    # Security issue: unrestricted pickle
    with open(filename, 'wb') as f:
        pickle.dump(data, f)

def calculate(x, y, z, a, b, c):
    """Too many parameters - maintainability issue."""
    # Long function with many parameters
    result = x + y + z + a + b + c
    if x > 0:
        if y > 0:
            if z > 0:
                if a > 0:
                    if b > 0:
                        if c > 0:
                            return result * 2
    return result

class OrderManager:
    """Class with mixed responsibilities - SOLID violation."""
    
    def __init__(self):
        self.orders = []
        self.cache = {}
        self.logger = None
    
    def add_order(self, order):
        """Add order - no validation."""
        self.orders.append(order)
        # Direct SQL injection vulnerability
        query = f"INSERT INTO orders VALUES ({order['id']}, '{order['name']}')"
        self.execute_query(query)
    
    def execute_query(self, query):
        """Execute SQL query - no sanitization."""
        print(f"Executing: {query}")
        return True
    
    def process_payment(self, amount, card_number):
        """Process payment - security issues."""
        # Hardcoded credentials
        api_key = "sk-live-1234567890abcdef"
        # No encryption
        print(f"Charging {amount} to card {card_number}")
        return True
    
    def send_email(self, to, subject, body):
        """Send email - command injection risk."""
        import os
        cmd = f"echo '{body}' | mail -s '{subject}' {to}"
        os.system(cmd)  # Command injection vulnerability
    
    def get_stats(self):
        """Calculate stats - inefficient implementation."""
        total = 0
        for order in self.orders:
            total += 1
        return {'total_orders': total}

# Duplicate code
def validate_email_1(email):
    """Email validation - duplicated logic."""
    if '@' in email:
        if '.' in email:
            return True
    return False

def validate_email_2(email):
    """Email validation - same logic, different function."""
    if '@' in email:
        if '.' in email:
            return True
    return False

# Magic numbers
def calculate_shipping(weight):
    """Calculate shipping with magic numbers."""
    if weight < 10:
        return 5.99  # Magic number
    elif weight < 50:
        return 10.99  # Magic number
    else:
        return 25.99  # Magic number

# Unused imports and variables
UNUSED_VAR = "this is never used"

def dead_code():
    """Function that's never called."""
    pass
