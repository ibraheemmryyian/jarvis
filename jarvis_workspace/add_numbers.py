#!/usr/bin/env python3
"""
This module provides a simple function to add two numbers.

Functions:
    add_numbers(a: float, b: float) -> float: Adds two numbers and returns the result.
"""

def add_numbers(a: float, b: float) -> float:
    """
    Add two numbers and return the result.

    Args:
        a (float): The first number to add.
        b (float): The second number to add.

    Returns:
        float: The sum of a and b.
    """
    return a + b


# Example usage
if __name__ == "__main__":
    # Test the function with sample values
    result = add_numbers(3.5, 2.1)
    print(f"The sum is: {result}")
