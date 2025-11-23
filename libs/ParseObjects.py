"""
This file deals with creating a DataFrame of the objects in a map
"""
import pandas as pd
from utils import get_pythagoras
import math
import os
import json
import MapDataFrames
EPSILON = 0.059 # Epsilon threshold in ms for detecting when blocks count towards the same swing

def BuildNewSwingsv2(map_object, left, right):
    """
    Sets the df_left, df_right, df_new_left_swing, df_new_right_swing, df_left_sliders, df_right_sliders, df_new_swing, and df_ignore_doubles fields of map_object.dataframe_struct
    """
    firstLeftSwingIndex = left.head(1).index[0]
    firstRightSwingIndex = right.head(1).index[0]

    df_newLeftSwing = left[((((60 * left['_timeChange']) / left['_bpm']) > EPSILON) | (left.index == firstLeftSwingIndex))]
    df_newRightSwing = right[((((60 * right['_timeChange']) / right['_bpm']) > EPSILON) | (right.index == firstRightSwingIndex))]
    df_leftSliders = left[(((60 * left['_timeChange']) / left['_bpm']) < EPSILON) & (left['_timeChange'] != 0)]
    df_rightSliders = right[(((60 * right['_timeChange']) / right['_bpm']) < EPSILON) & (right['_timeChange'] != 0)]

    #Create and update columns
    df_newLeftSwing['_xMovement'] = df_newLeftSwing.loc[:, ['_xCenter']].diff().fillna(0)
    df_newLeftSwing['_yMovement'] = df_newLeftSwing.loc[:, ['_yCenter']].diff().fillna(0)
    df_newLeftSwing['_totMovement'] = df_newLeftSwing.apply(lambda x: get_pythagoras(x['_xMovement'], x['_yMovement']), axis=1).fillna(0) 
    df_newLeftSwing['_angleMagnitudeChange'] = abs(df_newLeftSwing.apply(lambda x: math.atan(x['_yMovement']/x['_xMovement']), axis=1))
    df_newLeftSwing['_timeChange'] = df_newLeftSwing.loc[:, ['_time']].diff().fillna(0)
    df_newLeftSwing['_timeChangeSeconds'] = (60 * df_newLeftSwing['_timeChange']) / df_newLeftSwing['_bpm']

    df_newRightSwing['_xMovement'] = df_newRightSwing.loc[:, ['_xCenter']].diff().fillna(0)
    df_newRightSwing['_yMovement'] = df_newRightSwing.loc[:, ['_yCenter']].diff().fillna(0)
    df_newRightSwing['_totMovement'] = df_newRightSwing.apply(lambda x: get_pythagoras(x['_xMovement'], x['_yMovement']), axis=1).fillna(0)
    df_newRightSwing['_angleMagnitudeChange'] = abs(df_newRightSwing.apply(lambda x: math.atan(x['_yMovement']/x['_xMovement']), axis=1))
    df_newRightSwing['_timeChange'] = df_newRightSwing.loc[:, ['_time']].diff().fillna(0)
    df_newRightSwing['_timeChangeSeconds'] = (60 * df_newRightSwing['_timeChange']) / df_newRightSwing['_bpm']

    df_newSwing = pd.concat([df_newLeftSwing, df_newRightSwing])

    df_newSwing = df_newSwing.sort_values('_time')
    df_newSwing['_timeChange'] = df_newSwing.loc[:, ['_time']].diff().fillna(0)
    df_newSwing['_timeChangeSeconds'] = (60 * df_newSwing['_timeChange']) / df_newSwing['_bpm']


    df_newLeftSwing['_seconds'] = df_newLeftSwing['_timeChangeSeconds'].cumsum()
    df_newRightSwing['_seconds'] = df_newRightSwing['_timeChangeSeconds'].cumsum()
    df_newSwing['_seconds'] = df_newSwing['_timeChangeSeconds'].cumsum()
    df_ignoreDoubles = df_newSwing.groupby('_seconds', as_index=False).agg('first')

    # Set the dataframe_struct field of map_object
    dfs = MapDataFrames(left, right, df_newLeftSwing, df_newRightSwing, df_leftSliders, df_rightSliders, df_newSwing, df_ignoreDoubles)
    map_object.dataframe_struct = dfs
    
def BuildObjectsDataFramev2(map_object, bpm_changes, diff_data, initial_bpm):
    """
    Builds the DataFrame of all objects for maps using v2 metadata
    """
    df = pd.DataFrame(diff_data['_notes'])
    df['_yCenter'] = df.loc[:, ('_lineLayer')].apply(lambda x: 1 + x * 0.55)
    df['_xCenter'] = df.loc[:, ('_lineIndex')].apply(lambda x: -0.9 + x * 0.6)

    #Add bpm column
    df['_bpm'] = initial_bpm
    for i in range(len(df)):
        currentTime = df.loc[i, '_time']
        for j in range(len(bpm_changes)):
            if currentTime >= bpm_changes.loc[j, '_time']:
                df['_bpm'] = bpm_changes.loc[j, '_BPM']
   
   
    left = (df[df['_type'] == 0]) #All left handed notes
    right = (df[df['_type'] == 1]) #All right handed notes

    left['_timeChange'] = left.loc[:, ['_time']].diff().fillna(0)
    right['_timeChange'] = right.loc[:, ['_time']].diff().fillna(0)


    left['_timeChangeSeconds'] = (60 * left['_timeChange']) / left['_bpm']
    right['_timeChangeSeconds'] = (60 * right['_timeChange']) / right['_bpm']

    BuildNewSwingsv2(map_object, left, right)

def BuildNewSwingsv3(map_object, left, right):
    firstLeftSwingIndex = left.head(1).index[0]
    firstRightSwingIndex = right.head(1).index[0]

    df_newLeftSwing = left[((((60 * left['_timeChange']) / left['_bpm']) > EPSILON) | (left.index == firstLeftSwingIndex))]
    df_newRightSwing = right[((((60 * right['_timeChange']) / right['_bpm']) > EPSILON) | (right.index == firstRightSwingIndex))]
    df_leftSliders = left[(((60 * left['_timeChange']) / left['_bpm']) < EPSILON) & (left['_timeChange'] != 0)]
    df_rightSliders = right[(((60 * right['_timeChange']) / right['_bpm']) < EPSILON) & (right['_timeChange'] != 0)]

    #Create and update columns
    df_newLeftSwing['_xMovement'] = df_newLeftSwing.loc[:, ['_xCenter']].diff().fillna(0)
    df_newLeftSwing['_yMovement'] = df_newLeftSwing.loc[:, ['_yCenter']].diff().fillna(0)
    df_newLeftSwing['_totMovement'] = df_newLeftSwing.apply(lambda x: get_pythagoras(x['_xMovement'], x['_yMovement']), axis=1).fillna(0) 
    df_newLeftSwing['_angleMagnitudeChange'] = abs(df_newLeftSwing.apply(lambda x: math.atan(x['_yMovement']/x['_xMovement']), axis=1))
    df_newLeftSwing['_timeChange'] = df_newLeftSwing.loc[:, ['b']].diff().fillna(0)
    df_newLeftSwing['_timeChangeSeconds'] = (60 * df_newLeftSwing['_timeChange']) / df_newLeftSwing['_bpm']

    df_newRightSwing['_xMovement'] = df_newRightSwing.loc[:, ['_xCenter']].diff().fillna(0)
    df_newRightSwing['_yMovement'] = df_newRightSwing.loc[:, ['_yCenter']].diff().fillna(0)
    df_newRightSwing['_totMovement'] = df_newRightSwing.apply(lambda x: get_pythagoras(x['_xMovement'], x['_yMovement']), axis=1).fillna(0)
    df_newRightSwing['_angleMagnitudeChange'] = abs(df_newRightSwing.apply(lambda x: math.atan(x['_yMovement']/x['_xMovement']), axis=1))
    df_newRightSwing['_timeChange'] = df_newRightSwing.loc[:, ['b']].diff().fillna(0)
    df_newRightSwing['_timeChangeSeconds'] = (60 * df_newRightSwing['_timeChange']) / df_newRightSwing['_bpm']

    df_newSwing = pd.concat([df_newLeftSwing, df_newRightSwing])
    df_newSwing = df_newSwing.sort_values('b')
    df_newSwing['_timeChange'] = df_newSwing.loc[:, ['b']].diff().fillna(0)
    df_newSwing['_timeChangeSeconds'] = (60 * df_newSwing['_timeChange']) / df_newSwing['_bpm']


    df_newLeftSwing['_seconds'] = df_newLeftSwing['_timeChangeSeconds'].cumsum()
    df_newRightSwing['_seconds'] = df_newRightSwing['_timeChangeSeconds'].cumsum()
    df_newSwing['_seconds'] = df_newSwing['_timeChangeSeconds'].cumsum()
    df_ignoreDoubles = df_newSwing.groupby('_seconds', as_index=False).agg('first')

    # Set the dataframe_struct field of map_object
    dfs = MapDataFrames(left, right, df_newLeftSwing, df_newRightSwing, df_leftSliders, df_rightSliders, df_newSwing, df_ignoreDoubles)
    map_object.dataframe_struct = dfs


def BuildObjectsDataFramev3(map_object, mapset_path, bpm_changes, diff_data, initial_bpm):
    """
    Builds the DataFrame of all objects for maps using v3 metadata
    """
    bpmPath = os.path.join(mapset_path, "BPMInfo.dat")
    if os.path.exists(bpmPath):
        with open(bpmPath, encoding="utf-8") as bpm_json_data:
            bpmData = json.load(bpm_json_data)
        song_frequency = bpmData.get('_songFrequency', 44100)
    bpm_changes['_change_in_time'] = (bpm_changes['_endSampleIndex'] - bpm_changes['_startSampleIndex']) / song_frequency
    bpm_changes['_BPM'] = (bpm_changes['_endBeat'] - bpm_changes['_startBeat']) * (60 / bpm_changes['_change_in_time'])
    bpm_changes['_time'] = bpm_changes['_change_in_time'].cumsum()

    df = pd.DataFrame(diff_data['colorNotes'])
    df['_yCenter'] = df.loc[:, ('y')].apply(lambda x: 1 + x * 0.55)
    df['_xCenter'] = df.loc[:, ('x')].apply(lambda x: -0.9 + x * 0.6)

    #Add bpm column
    df['_bpm'] = initial_bpm
    for i in range(len(df)):
        currentTime = df.loc[i, 'b']
        currentRow = 0
        for j in range(len(bpm_changes)):
            if currentTime >= bpm_changes.loc[j, '_time']:
                df['_bpm'] = bpm_changes.loc[j, '_BPM']
   
   
    left = (df[df['c'] == 0]) #All left handed notes
    right = (df[df['c'] == 1]) #All right handed notes

    num_notes = len(left) + len(right)

    left['_timeChange'] = left.loc[:, ['b']].diff().fillna(0)
    right['_timeChange'] = right.loc[:, ['b']].diff().fillna(0)


    left['_timeChangeSeconds'] = (60 * left['_timeChange']) / left['_bpm']
    right['_timeChangeSeconds'] = (60 * right['_timeChange']) / right['_bpm']

    BuildNewSwingsv3(map_object, left, right)