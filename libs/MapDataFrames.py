"""
This file defines a class MapDataFrames that stores various DataFrames related to a map
This class will be a field stored within the Map class
The nested structure is for readability, separating the DataFrames from other fields with primitive data types
"""

class MapDataFrames:
    """
    MapDataFrames class declaration
    Fields: 
        - df_left (DataFrame): DataFrame storing all red notes
        - df_right (DataFrame): DataFrame storing all blue notes
        - df_new_left_swing (DataFrame): stores all notes that begin a new left-handed swing
        - df_new_right_swing (DataFrame): stores all notes that begin a new right-handed swing
        - df_left_sliders (DataFrame): stores all left-handed sliders
        - df_right_sliders (DataFrame): stores all right-handed sliders
        - df_new_swing (DataFrame): stores all notes that begin a new swing on either hand
        - df_ignore_doubles (DataFrame): ignores doubles (only keeps one of the notes)
    """
    def __init__(self, df_left, df_right, df_new_left_swing, df_new_right_swing, df_left_sliders, df_right_sliders, df_new_swing, df_ignore_doubles):
        """
        Constructor
        """
        self.df_left = df_left
        self.df_right = df_right
        self.df_new_left_swing = df_new_left_swing
        self.df_new_right_swing = df_new_right_swing
        self.df_left_sliders = df_left_sliders
        self.df_right_sliders = df_right_sliders
        self.df_new_swing = df_new_swing
        self.df_ignore_doubles = df_ignore_doubles