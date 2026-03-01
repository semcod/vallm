"""
Legacy data processing system with multiple architectural issues.
This code intentionally contains various problems for autonomous refactoring demonstration.
"""

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime
from typing import List, Dict, Any, Optional

# Global variables - bad practice
cache = {}
connection = None
config = {}

def load_config():
    """Load configuration - security issue with eval."""
    config_str = os.environ.get('CONFIG', '{}')
    return eval(config_str)  # DANGEROUS!

def init_database():
    """Initialize database connection."""
    global connection
    connection = sqlite3.connect(':memory:')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY,
            name TEXT,
            email TEXT,
            password TEXT,
            created_at TIMESTAMP
        )
    ''')
    connection.commit()

class DataProcessor:
    """Data processor with multiple responsibilities - violates SRP."""
    
    def __init__(self):
        self.data = []
        self.processed_data = []
        self.errors = []
        self.stats = {}
        self.cache = {}
        self.config = load_config()
        
    def process_user_data(self, user_data):
        """Process user data with deep nesting and security issues."""
        if user_data:
            if isinstance(user_data, list):
                for user in user_data:
                    if 'name' in user:
                        if 'email' in user:
                            if 'password' in user:
                                if '@' in user['email']:
                                    if len(user['password']) > 6:
                                        # SQL injection vulnerability
                                        query = f"INSERT INTO users (name, email, password, created_at) VALUES ('{user['name']}', '{user['email']}', '{user['password']}', '{datetime.now()}')"
                                        cursor = connection.cursor()
                                        cursor.execute(query)
                                        connection.commit()
                                        
                                        # Process the user
                                        processed_user = {
                                            'name': user['name'],
                                            'email': user['email'],
                                            'processed_at': datetime.now().isoformat()
                                        }
                                        self.processed_data.append(processed_user)
                                        
                                        # Update stats
                                        if 'users_processed' not in self.stats:
                                            self.stats['users_processed'] = 0
                                        self.stats['users_processed'] += 1
        return self.processed_data
    
    def calculate_metrics(self, data):
        """Calculate metrics with performance issues."""
        metrics = {}
        
        # Inefficient calculation
        for i in range(len(data)):
            for j in range(len(data)):
                if i != j:
                    if data[i].get('name') == data[j].get('name'):
                        if 'duplicates' not in metrics:
                            metrics['duplicates'] = []
                        metrics['duplicates'].append(data[i])
        
        # More inefficient operations
        total_items = 0
        for item in data:
            total_items += 1
            for key, value in item.items():
                if isinstance(value, str):
                    total_items += len(value)
                elif isinstance(value, (list, dict)):
                    total_items += len(value)
        
        metrics['total_items'] = total_items
        return metrics
    
    def export_data(self, filename, data):
        """Export data with security issues."""
        # Command injection vulnerability
        command = f"echo '{json.dumps(data)}' > {filename}"
        subprocess.run(command, shell=True)
        
        # Pickle security issue
        import pickle
        with open(f"{filename}.pickle", 'wb') as f:
            pickle.dump(data, f)
    
    def validate_email(self, email):
        """Email validation - duplicate function."""
        if '@' in email and '.' in email:
            return True
        return False
    
    def validate_email_again(self, email):
        """Duplicate email validation function."""
        if '@' in email and '.' in email:
            return True
        return False
    
    def process_with_external_api(self, data):
        """Process data with external API - no error handling."""
        import requests
        
        # Hardcoded API key
        api_key = "sk-1234567890abcdef"
        
        for item in data:
            url = f"https://api.example.com/process?data={item['name']}&key={api_key}"
            response = requests.get(url)
            result = response.json()
            item['api_result'] = result
    
    def complex_calculation(self, a, b, c, d, e, f, g, h, i, j):
        """Too many parameters - maintainability issue."""
        result = a + b + c + d + e + f + g + h + i + j
        intermediate = result * 2
        final = intermediate / 10
        return final
    
    def unused_function(self):
        """Dead code - unused function."""
        pass
    
    def another_unused_function(self, x, y):
        """More dead code."""
        return x + y

class ReportGenerator:
    """Report generator with tight coupling to DataProcessor."""
    
    def __init__(self, processor):
        self.processor = processor
        self.report_data = {}
    
    def generate_report(self):
        """Generate report with tight coupling."""
        # Direct access to processor internals
        data = self.processor.processed_data
        stats = self.processor.stats
        
        report = {
            'total_processed': len(data),
            'stats': stats,
            'timestamp': datetime.now().isoformat()
        }
        
        # More tight coupling
        if hasattr(self.processor, 'cache'):
            report['cache_size'] = len(self.processor.cache)
        
        return report
    
    def export_report(self, filename):
        """Export with security issues."""
        report = self.generate_report()
        
        # Path traversal vulnerability
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

def main():
    """Main function with multiple issues."""
    # Initialize everything
    config = load_config()
    init_database()
    
    processor = DataProcessor()
    
    # Sample data with issues
    users = [
        {'name': 'John Doe', 'email': 'john@example.com', 'password': 'password123'},
        {'name': 'Jane Smith', 'email': 'jane@example.com', 'password': 'pass456'},
        {'name': 'Bob Johnson', 'email': 'bob@example.com', 'password': 'secret789'}
    ]
    
    # Process data
    processed = processor.process_user_data(users)
    
    # Calculate metrics
    metrics = processor.calculate_metrics(processed)
    
    # Export data
    processor.export_data('output.json', processed)
    
    # Generate report
    generator = ReportGenerator(processor)
    report = generator.generate_report()
    generator.export_report('report.json')
    
    print(f"Processed {len(processed)} users")
    print(f"Metrics: {metrics}")

if __name__ == "__main__":
    main()
