"""
This file creates a Map class to store information about a map
"""
from utils import normalize_string
import json

def get_diff_info_dict(info_data, diff, lawless):
    """
    Returns a dictionary of the information contained in the info.dat file that is relevant for this difficulty
    """
    # we first want to iterate through dicts
    for beatmap_set in info_data["_difficultyBeatmapSets"]:
        if ((lawless == 0) & (beatmap_set["_beatmapCharacteristicName"] != "Standard")):
            continue
        elif ((lawless == 1) & (beatmap_set["_beatmapCharacteristicName"] != "Lawless")):
            continue
        else:
            for difficulty in beatmap_set["_difficultyBeatmaps"]:
                if (difficulty["_difficultyRank"] == diff):
                    return difficulty
    print("Error finding difficulty metadata in the info.dat file for this difficulty")
    return



def diff_str_to_int(diff_str):
    """
    This takes in a string representing the map's difficulty and outputs the corresponding integer
    easy -> 1, normal -> 3, hard -> 5, expert -> 7, expertplus -> 9
    returns -1 on error (invalid input string)
    """
    normalized_str = normalize_string(diff_str)
    if (normalized_str == "easy"):
        return 1
    elif (normalized_str == "normal"):
        return 3
    elif (normalized_str == "hard"):
        return 5
    elif (normalized_str == "expert"):
        return 7
    elif (normalized_str == "expertplus"):
        return 9
    return -1

def get_diff_path(mapset_path, diff):
    """
    Returns the string for the file path to the difficulty's .dat file
    """
    if (diff == 1):
        return mapset_path + "/EasyStandard.dat"
    elif (diff == 3):
        return mapset_path + "/NormalStandard.dat"
    elif (diff == 5):
        return mapset_path + "/HardStandard.dat"
    elif (diff == 7):
        return mapset_path + "/ExpertStandard.dat"
    return mapset_path + "/ExpertPlusStandard.dat"

class Map:
    """
    Map class declaration
    """
    def __init__(self, mapset_path, diff_str, category, lawless):
        """
        Constructor
        Fields:
        - mapset_path (string): file path of the mapset directory
        - diff (int): integer encoding difficulty label
        - lawless (int): 1 if lawless diff, 0 otherwise
        - info_data (dict): dictionary storing the contents from the info .dat file
        - diff_data (dict): dictionary storing the contents from the respective diff's .dat file
        - category (string): the category of accuracy map
        - njs (int): njs of the map
        - objects (DataFrame): DataFrame of all objects in the map
        """
        self.mapset_path = mapset_path
        self.diff = diff_str_to_int(diff_str)
        self.lawless = lawless
        if (self.diff == -1):
            print("Please provide a valid difficulty label")
            return
        with open(mapset_path + "/Info.dat", "r", encoding="utf-8") as f:
            self.info_data = json.load(f)
        with open(get_diff_path(mapset_path, self.diff), "r", encoding="utf-8") as f:
            self.dict_data = json.load(f)
        self.category = normalize_string(category)
        