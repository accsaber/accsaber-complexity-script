"""
This file contains helper functions to calculate map statistics that will be called in the MapStatistics class
"""
import math

def GetLeftSwings(map_object):
    return len(map_object.dataframe_struct.df_new_left_swing)

def GetRightSwings(map_object):
    return len(map_object.dataframe_struct.df_new_right_swing)

def GetTotalSwings(map_object):
    return len(map_object.dataframe_struct.df_new_swing)

def GetLeftTime(map_object):
    return map_object.dataframe_struct.df_new_left_swing['_timeChangeSeconds'].sum()

def GetRightTime(map_object):
    return map_object.dataframe_struct.df_new_right_swing['_timeChangeSeconds'].sum()

def GetLeftAvgSps(map_object):
    return GetLeftSwings(map_object) / GetLeftTime(map_object)

def GetRightAvgSps(map_object):
    return GetRightSwings(map_object) / GetRightTime(map_object)

def GetLeftAvgAngleChange(map_object):
    return map_object.dataframe_struct.df_new_left_swing['_angleMagnitudeChange'].mean()

def GetRightAvgAngleChange(map_object):
    return map_object.dataframe_struct.df_new_right_swing['_angleMagnitudeChange'].mean()

def GetAvgAngleChange(map_object):
    return map_object.dataframe_struct.df_new_swing['_angleMagnitudeChange'].mean()

def GetTotalTime(map_object):
    return map_object.dataframe_struct.df_new_swing['_timeChangeSeconds'].sum()

def GetAvgSps(map_object):
    return GetTotalSwings(map_object) / GetTotalTime(map_object)

def GetNumDoubles(map_object):
    return len(map_object.dataframe_struct.df_new_swing) - len(map_object.dataframe_struct.df_ignore_doubles)

def GetTrueAccAvgSps(map_object):
    return len(map_object.dataframe_struct.df_ignore_doubles) / map_object.dataframe_struct.df_ignore_doubles['_timeChangeSeconds'].sum()

def HasSliders(map_object):
    num_sliders = len(map_object.dataframe_struct.df_left_sliders) + len(map_object.dataframe_struct.df_right_sliders)
    if (num_sliders > 0):
        return 1
    return 0

def GetNumNotes(map_object):
    return len(map_object.dataframe_struct.df_left) + len(map_object.dataframe_struct.df_right)

# The code for calculating peak_sps adapted from Uninstaller's sps calculator

def calculate_swings_list(df_current):
    swing_list = df_current['_seconds'].tolist()
    last = math.floor(df_current['_seconds'].max())
    array = [0 for x in range(math.floor(last) + 1)]
    for swing in swing_list:
        array[math.floor(swing)] += 1
    return array

def calculate_peak_sps(swings_list, interval = 10):

    current_sps_sum = sum(swings_list[:interval])
    max_sps_sum = current_sps_sum
    for x in range(0, len(swings_list) - interval):
        current_sps_sum = current_sps_sum - swings_list[x] + swings_list[x + interval]
        max_sps_sum = max(max_sps_sum, current_sps_sum)
    return round(max_sps_sum / interval, 2)

def GetLeftPeakSps(map_object):
    return calculate_peak_sps(calculate_swings_list(map_object.dataframe_struct.df_new_left_swing))

def GetRightPeakSps(map_object):
    return calculate_peak_sps(calculate_swings_list(map_object.dataframe_struct.df_new_right_swing))

def GetPeakSps(map_object):
    return calculate_peak_sps(calculate_swings_list(map_object.dataframe_struct.df_new_swing))

def GetTrueAccPeakSps(map_object):
    return calculate_peak_sps(calculate_swings_list(map_object.dataframe_struct.df_ignore_doubles))