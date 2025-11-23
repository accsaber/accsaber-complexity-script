"""
This is a collection of smaller functions that are used in other libraries
"""
import math

def normalize_string(string):
    """
    Takes an input string and returns the version converted to lowercase and trimmed of whitespace
    """
    return string.lower().strip()

def get_pythagoras(x, y):
    """
    Pythagorean distance
    """
    return math.sqrt(x ** 2 + y ** 2)