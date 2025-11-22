"""
This is a collection of smaller functions that are used in other libraries
"""

def normalize_string(string):
    """
    Takes an input string and returns the version converted to lowercase and trimmed of whitespace
    """
    return string.lower().strip()