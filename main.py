"""
This is the entry point of the ranking criteria checker
"""
import sys
from libs.Map import Map
from libs.CriteriaChecker import RunCriteriaChecks
"""
# TODO Add bomb detector
"""

def main():
    mapset_path = "./examples/3cba5 (Hypnotized - Viking & Taddus)"
    diff_str = "Expert"
    category = "Standard"

    map_object = Map(mapset_path, diff_str, category)

    results = RunCriteriaChecks(map_object)
    print(results)
    return 0

if __name__ == "__main__":
    main()
    sys.exit(0)