"""
This is the entry point of the ranking criteria checker
"""
import sys
from libs.Map import Map
from libs.CriteriaChecker import RunCriteriaChecks

def main():
    mapset_path = "examples/414df (i won't run - VoltageO)"
    diff_str = "ExpertPlus"
    category = "Standard"

    map_object = Map(mapset_path, diff_str, category)

    results = RunCriteriaChecks(map_object)
    print(results)
    return 0

if __name__ == "__main__":
    main()
    sys.exit(0)