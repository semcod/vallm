"""
Refactored code for demonstration.
Fixed issues and improved quality.
"""

import os
import json
from typing import List, Dict, Any

# Global variable - bad practice
data_cache = {}

from .utils import load_config, save_data, calculate_total


def main():
    """Main function with improvements."""
    from .utils import run_demo_main
    run_demo_main()

if __name__ == "__main__":
    main()