"""Shared calculate_total function for ollama demo examples."""

from __future__ import annotations

from typing import List, Dict, Any


def calculate_total(items: List[Dict[str, Any]]) -> float:
    """Calculate total price from items list.
    
    Args:
        items: List of dictionaries with 'price' and 'quantity' keys
        
    Returns:
        Total price as float
    """
    total = 0.0
    for item in items:
        try:
            price = float(item.get('price', 0))
            quantity = int(item.get('quantity', 0))
            total += price * quantity
        except (ValueError, TypeError) as e:
            print(f"Error processing item: {e}")
    return total
