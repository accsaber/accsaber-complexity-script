import pandas as pd
import json
import math

#MODIFY THE CODE BELOW ACCORDING TO INSTRUCTIONS
#Change the following variable to 1 if there is a lawless difficulty, or 0 if there is not a lawless difficulty
lawless = 0
#Change the following integer to an integer from 0-4 with 0 corresponding to the lowest standard difficulty, 1 corresponding to the second lowest standard difficulty, etc
difficulty = 0
#Change the following variable to one of the words "True", "Standard", or "Tech" EXACTLY with the quotation marks that corresponds to the category of the map.
category = "Standard" 
#Add the relative paths to the difficulty and info files below
diffPath = 'accsaber-maps/f124 (Avalanche - That_Narwhal)/EasyStandard.dat' #Replace with the difficulty file's relative path
infoPath = 'accsaber-maps/f124 (Avalanche - That_Narwhal)/Info.dat' #Replace with the info file's relative path
madeUsingSeveralVersions = False #Make this boolean "True" if the map was made using several versions of Chromapper

temp_array = diffPath.split("/")
map_name = temp_array[1].split(" ")[1]
diff = temp_array[2].split(".")[0]
both_hands_start_downswing = True

#Reading json data
def get_pythagoras(x, y):
    return math.sqrt(x ** 2 + y ** 2)

with open(diffPath) as diff_json_data:
    diffData = json.load(diff_json_data)

with open(infoPath) as info_json_data:
    infoData = json.load(info_json_data)

#Parse BPM changes if they exist
initialBPM = infoData.get('_beatsPerMinute')
diffDict = infoData.get('_difficultyBeatmapSets')[lawless].get('_difficultyBeatmaps')[difficulty]
njs = diffDict.get('_noteJumpMovementSpeed')
#If the exception is caught, then the map was created using Chromaper
IsChromapper = False
try:
    bpmChangesDict = diffData.get('_customData').get('_BPMChanges')
except:
    IsChromapper = True

if madeUsingSeveralVersions == True:
    IsChromapper = True

#First we will deal with maps created using MMA2
    
#Create columns
if (IsChromapper == False):
    df_BPMChanges = pd.DataFrame(bpmChangesDict)
    df = pd.DataFrame(diffData['_notes'])
    df['_yCenter'] = df.loc[:, ('_lineLayer')].apply(lambda x: 1 + x * 0.55)
    df['_xCenter'] = df.loc[:, ('_lineIndex')].apply(lambda x: -0.9 + x * 0.6)

    #Add bpm column
    df['_bpm'] = initialBPM
    for i in range(len(df)):
        currentTime = df.loc[i, '_time']
        currentRow = 0
        for j in range(len(df_BPMChanges)):
            if currentTime >= df_BPMChanges.loc[j, '_time']:
                df['_bpm'] = df_BPMChanges.loc[j, '_BPM']
   
   
    left = (df[df['_type'] == 0]) #All left handed notes
    right = (df[df['_type'] == 1]) #All right handed notes

    num_notes = len(left) + len(right)

    left['_timeChange'] = left.loc[:, ['_time']].diff().fillna(0)
    right['_timeChange'] = right.loc[:, ['_time']].diff().fillna(0)


    left['_timeChangeSeconds'] = (60 * left['_timeChange']) / left['_bpm']
    right['_timeChangeSeconds'] = (60 * right['_timeChange']) / right['_bpm']

#Account for sliders and stacks
if (IsChromapper == False):
    EPSILON = 0.059
    firstLeftSwingIndex = left.head(1).index[0]
    firstRightSwingIndex = right.head(1).index[0]

    df_newLeftSwing = left[((((60 * left['_timeChange']) / left['_bpm']) > EPSILON) | (left.index == firstLeftSwingIndex))]
    df_newRightSwing = right[((((60 * right['_timeChange']) / right['_bpm']) > EPSILON) | (right.index == firstRightSwingIndex))]
    df_leftSliders = left[(((60 * left['_timeChange']) / left['_bpm']) < EPSILON) & (left['_timeChange'] != 0)]
    df_rightSliders = right[(((60 * right['_timeChange']) / right['_bpm']) < EPSILON) & (right['_timeChange'] != 0)]

    hasSliders = False
    if (len(df_leftSliders) + len(df_rightSliders) > 0):
        hasSliders = True

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


    #Statistics 
    left_swings = len(df_newLeftSwing)
    right_swings = len(df_newRightSwing)
    total_swings = len(df_newSwing)
    left_time = df_newLeftSwing['_timeChangeSeconds'].sum()
    right_time = df_newRightSwing['_timeChangeSeconds'].sum()
    right_avg_sps = right_swings / right_time
    left_avg_sps = left_swings / left_time
    left_avg_angleChange = df_newLeftSwing['_angleMagnitudeChange'].mean()
    right_avg_angleChange = df_newRightSwing['_angleMagnitudeChange'].mean()
    avg_angleChange = df_newSwing['_angleMagnitudeChange'].mean()
    total_time = df_newSwing['_timeChangeSeconds'].sum()
    avg_sps = total_swings / total_time
    num_doubles = len(df_newSwing) - len(df_ignoreDoubles)
    avg_true_acc_sps = len(df_ignoreDoubles) / df_ignoreDoubles['_timeChangeSeconds'].sum()

#The code in this cell is adapted from Uninstaller's sps calculator

if (IsChromapper == False):
    def calculate_swings_list(df_current):
        swing_list = df_current['_seconds'].tolist()
        last = math.floor(df_current['_seconds'].max())
        array = [0 for x in range(math.floor(last) + 1)]
        for swing in swing_list:
            array[math.floor(swing)] += 1
        return array

    

    def calculate_max_sps(swings_list, interval = 10):
    
        current_sps_sum = sum(swings_list[:interval])
        max_sps_sum = current_sps_sum
        for x in range(0, len(swings_list) - interval):
            current_sps_sum = current_sps_sum - swings_list[x] + swings_list[x + interval]
            max_sps_sum = max(max_sps_sum, current_sps_sum)
        return round(max_sps_sum / interval, 2)

    #peak sps statistics

    
    peak_left_sps = calculate_max_sps(calculate_swings_list(df_newLeftSwing))
    peak_right_sps = calculate_max_sps(calculate_swings_list(df_newRightSwing))
    peak_sps = calculate_max_sps(calculate_swings_list(df_newSwing))
    peak_true_acc_sps = calculate_max_sps(calculate_swings_list(df_ignoreDoubles))

#Create columns to help with bombs
if (IsChromapper == False):
    df['_timeChangeBefore'] = df.loc[:, ['_time']].diff().fillna(0)
    df['_timeChangeBefore'] = (60 * df['_timeChangeBefore']) / df['_bpm']
    df['_timeChangeAfter'] = abs(df.loc[:, ['_time']].diff(periods = -1).fillna(0))
    df['_timeChangeAfter'] = (60 * df['_timeChangeAfter']) / df['_bpm']

    #Bombs
    minReactTimeBefore = float('inf')
    minReactTimeAfter = float('inf')

    firstType = df.loc[0, '_time']
    secondType = df.loc[1, '_time']
    secondLastType = df.loc[len(df) - 2, '_time']
    lastType = df.loc[len(df) - 1, '_time']

    #Check for bomb at start
    if (firstType == 3) & (secondType != 3):
        minReactTimeAfter = df.loc[0, '_timeChangeAfter'] * 1000

    #Check for bomb at end
    if (lastType == 3) & (secondLastType != 3):
        if (minReactTimeBefore == float('inf')) | (minReactTimeBefore > df.loc[len(df) - 1, '_timeChangeBefore']):
            minReactTimeBefore = df.loc[len(df) - 1, '_timeChangeBefore'] 

    #Find the minimum time before and after a bomb, ignoring bombs outside the swing's path
    for i in range(len(df) - 2):
        previousType = df.loc[i, '_type']
        thisType = df.loc[i + 1, '_type']
        nextType = df.loc[i + 2, '_type']
        if thisType == 3:
            bombException = False

            #Calculate minimum time before a bomb
            if (previousType == 0) | (previousType == 1):
                #Check for conditions where bomb is out of path of saber
                if (df.loc[i, '_lineLayer'] == 0) & (df.loc[i + 1, '_lineLayer'] == 2): #Note is in bottom layer and bomb is in top layer
                    if (df.loc[i, '_cutDirection'] == 2) | (df.loc[i, '_cutDirection'] == 3) | (df.loc[i, '_cutDirection'] == 8): #Note direction is left, right, or dot
                        bombException = True
                elif (df.loc[i, '_type'] == 0): #Note is red
                    if (df.loc[i, '_lineLayer'] == 0): #Note is bottom layer
                        if (df.loc[i, '_lineIndex'] == 0): #Note has leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 2) | (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in second rightmost or rightmost index
                                #Note direction is up, down, up left, down left, or dot
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 4) | (df.loc[i, '_cutDirection'] == 6) | (df.loc[i, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i, '_lineIndex'] == 1): #Note has second leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in rightmost index
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second rightmost or rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0): #Bomb is in leftmost index
                                #Note direction is up, down, down right, or dot
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 7) | (df.loc[i, '_cutDirection'] == 8):
                                    bombException = True
                    elif (df.loc[i, '_lineLayer'] == 2): #Note is in top layer
                        if (df.loc[i, '_lineIndex'] == 0): #Note has leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 2) | (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in second rightmost or rightmost index
                                #Note direction is up, down, up left, down left, or dot
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 4) | (df.loc[i, '_cutDirection'] == 6) | (df.loc[i, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i, '_lineIndex'] == 1): #Note has second leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in rightmost index
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second rightmost or rightmost index
                            if df.loc[i + 1, '_lineIndex'] == 0: #Bomb is in leftmost index
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                elif (df.loc[i, '_type'] == 1): #Note is blue
                    if (df.loc[i, '_lineLayer'] == 0): #Note is bottom layer
                        if (df.loc[i, '_lineIndex'] == 3): #Note has rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0) | (df.loc[i + 1, '_lineIndex'] == 1): #Bomb is in second leftmost or leftmost index
                                #Note direction is up, down, up right, down right, or dot
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 5) | (df.loc[i, '_cutDirection'] == 7) | (df.loc[i, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i, '_lineIndex'] == 2): #Note has second rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0): #Bomb is in leftmost index
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second leftmost or leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in rightmost index
                                #Note direction is up, down, down left, or dot
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 6) | (df.loc[i, '_cutDirection'] == 8):
                                    bombException = True
                    elif (df.loc[i, '_lineLayer'] == 2): #Note is in top layer
                        if (df.loc[i, '_lineIndex'] == 3): #Note has rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0) | (df.loc[i + 1, '_lineIndex'] == 1): #Bomb is in second leftmost or leftmost index
                                #Note direction is up, down, up right, down right, or dot
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 5) | (df.loc[i, '_cutDirection'] == 7) | (df.loc[i, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i, '_lineIndex'] == 2): #Note has second rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0): #Bomb is in leftmost index
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second leftmost or leftmost index
                            if df.loc[i + 1, '_lineIndex'] == 3: #Bomb is in rightmost index
                                if (df.loc[i, '_cutDirection'] == 0) | (df.loc[i, '_cutDirection'] == 1) | (df.loc[i, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True

                #Update the minimum time before a bomb if needed
                if (bombException == False) & ((minReactTimeBefore == float('inf')) | (minReactTimeBefore > df.loc[i + 1, '_timeChangeBefore'])):
                    minReactTimeBefore = df.loc[i + 1, '_timeChangeBefore']

            #Calculate minimum time after a bomb
            if (nextType == 0) | (nextType == 1):
                #Check for conditions where bomb is out of path of saber
                if (df.loc[i + 2, '_lineLayer'] == 0) & (df.loc[i + 1, '_lineLayer'] == 2): #Note is in bottom layer and bomb is in top layer
                    if (df.loc[i + 2, '_cutDirection'] == 2) | (df.loc[i + 2, '_cutDirection'] == 3) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is left, right, or dot
                        bombException = True
                elif (df.loc[i + 2, '_type'] == 0): #Note is red
                    if (df.loc[i + 2, '_lineLayer'] == 0): #Note is bottom layer
                        if (df.loc[i + 2, '_lineIndex'] == 0): #Note has leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 2) | (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in second rightmost or rightmost index
                                #Note direction is up, down, up left, down left, or dot
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 4) | (df.loc[i + 2, '_cutDirection'] == 6) | (df.loc[i + 2, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i + 2, '_lineIndex'] == 1): #Note has second leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in rightmost index
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second rightmost or rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0): #Bomb is in leftmost index
                                #Note direction is up, down, down right, or dot
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 7) | (df.loc[i + 2, '_cutDirection'] == 8):
                                    bombException = True
                    elif (df.loc[i + 2, '_lineLayer'] == 2): #Note is in top layer
                        if (df.loc[i + 2, '_lineIndex'] == 0): #Note has leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 2) | (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in second rightmost or rightmost index
                                #Note direction is up, down, up left, down left, or dot
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 4) | (df.loc[i + 2, '_cutDirection'] == 6) | (df.loc[i + 2, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i + 2, '_lineIndex'] == 1): #Note has second leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in rightmost index
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second rightmost or rightmost index
                            if df.loc[i + 1, '_lineIndex'] == 0: #Bomb is in leftmost index
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                elif (df.loc[i + 2, '_type'] == 1): #Note is blue
                    if (df.loc[i + 2, '_lineLayer'] == 0): #Note is bottom layer
                        if (df.loc[i + 2, '_lineIndex'] == 3): #Note has rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0) | (df.loc[i + 1, '_lineIndex'] == 1): #Bomb is in second leftmost or leftmost index
                                #Note direction is up, down, up right, down right, or dot
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 5) | (df.loc[i + 2, '_cutDirection'] == 7) | (df.loc[i + 2, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i + 2, '_lineIndex'] == 2): #Note has second rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0): #Bomb is in leftmost index
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second leftmost or leftmost index
                            if (df.loc[i + 1, '_lineIndex'] == 3): #Bomb is in rightmost index
                                #Note direction is up, down, down left, or dot
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 6) | (df.loc[i + 2, '_cutDirection'] == 8):
                                    bombException = True
                    elif (df.loc[i + 2, '_lineLayer'] == 2): #Note is in top layer
                        if (df.loc[i + 2, '_lineIndex'] == 3): #Note has rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0) | (df.loc[i + 1, '_lineIndex'] == 1): #Bomb is in second leftmost or leftmost index
                                #Note direction is up, down, up right, down right, or dot
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 5) | (df.loc[i + 2, '_cutDirection'] == 7) | (df.loc[i + 2, '_cutDirection'] == 8):
                                    bombException = True
                        elif (df.loc[i + 2, '_lineIndex'] == 2): #Note has second rightmost index
                            if (df.loc[i + 1, '_lineIndex'] == 0): #Bomb is in leftmost index
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True
                        else: #Note is in second leftmost or leftmost index
                            if df.loc[i + 1, '_lineIndex'] == 3: #Bomb is in rightmost index
                                if (df.loc[i + 2, '_cutDirection'] == 0) | (df.loc[i + 2, '_cutDirection'] == 1) | (df.loc[i + 2, '_cutDirection'] == 8): #Note direction is up, down, or dot
                                    bombException = True

                #Update the minimum time after a bomb if needed
                if (bombException == False) & ((minReactTimeAfter == float('inf')) | (minReactTimeAfter > df.loc[i + 1, '_timeChangeAfter'])):
                    minReactTimeAfter = df.loc[i + 1, '_timeChangeAfter']

def FindSectionsBreakingPeakSps(swings_list, category, interval = 10):
    data = []
    peak_sps_limit = 5.75
    
    if (category == "True"):
        peak_sps_limit = 1.75

    current_sps_sum = sum(swings_list[:interval])
    
    for x in range(0, len(swings_list) - interval):
        current_sps_sum = current_sps_sum - swings_list[x] + swings_list[x + interval]
        if ((current_sps_sum / interval) > peak_sps_limit):
            start = x
            end = x + 10
            data.append(str(start) + ' seconds to ' + str(end) + ' seconds (' + str(current_sps_sum/interval) + ' sps)' )
    return data

def PrintPeakSpsLog(category):
    if (category == "True"):
        swings = calculate_swings_list(df_ignoreDoubles)
    else:
        swings = calculate_swings_list(df_newSwing)
    failed_sections = FindSectionsBreakingPeakSps(swings, category)
    print('The sections that broke the peak sps are')
    for x in failed_sections:
        print(str(x))


#Criteria Check
#This script does not check for towers or sliders in maps that are not tech acc
passLog = ""
failLog = ""
passTests = True
if (IsChromapper == False):
    if (minReactTimeBefore != float('inf')):
        minReactTimeBefore = math.floor(minReactTimeBefore * 1000)
    if (minReactTimeAfter != float('inf')):
        minReactTimeAfter = math.floor(minReactTimeAfter * 1000)
    avg_sps = round(avg_sps, 2)
    peak_sps = round(peak_sps, 2)
    avg_true_acc_sps = round(avg_true_acc_sps, 2)
    peak_true_acc_sps = round(peak_true_acc_sps, 2)
    total_time = round(total_time, 2)

    #General criteria checks

    #Check if time between first and last note is between 2-6 minutes inclusive
    if ((total_time < 120) | (total_time > 300)):
        passTests = False
        failLog += "Fail: The time between the first and last note is " + str(total_time) + " seconds which is outside of the range of 120 to 300 seconds\n"
    else:
        passLog += "Pass: The time between the first and last note is " + str(total_time) + " seconds which is between 120 and 300 seconds\n"
    if (((df_newLeftSwing.iloc[0].loc['_cutDirection'] != 1) & (df_newLeftSwing.iloc[0].loc['_cutDirection'] != 8) & (df_newLeftSwing.iloc[0].loc['_cutDirection'] != 6) & (df_newLeftSwing.iloc[0].loc['_cutDirection'] != 7)) | ((df_newRightSwing.iloc[0].loc['_cutDirection'] != 1) & (df_newRightSwing.iloc[0].loc['_cutDirection'] != 8) & (df_newRightSwing.iloc[0].loc['_cutDirection'] != 6) & (df_newRightSwing.iloc[0].loc['_cutDirection'] != 7))):
        passTests = False
        both_hands_start_downswing = False
        failLog += "Fail: At least one of the hands does not start on a downswing\n"
    else:
        passLog += "Pass: Both hands start on a downswing\n"
    if (num_notes < 115):
        passTests = False
        failLog += "Fail: There are " + str(num_notes) + " notes, which is less than 115\n"
    else: 
        passLog += "Pass: There are " + str(num_notes) + " notes, which is at least 115\n"
    if ((minReactTimeAfter != float('inf')) & (minReactTimeAfter < 200)):
        passTests = False
        failLog += "Fail: The minimum reaction time after a bomb is " + str(minReactTimeAfter) + " miliseconds, which is less than 200\n"
    else:
        passLog += "Pass: The minimum reaction time after a bomb is " + str(minReactTimeAfter) + " miliseconds, which is at least 200\n"

    #Category specific criteria checks
    if (category == "True"):
        if (num_notes != len(df_newSwing)):
            passTests = False
            failLog += "Fail: There are sliders, stacks, towers, or windows in this map\n"
        else:
            passLog += "Pass: There are no sliders, stacks, towers, or windows in this map\n"
        if (njs > 12):
            passTests = False
            failLog += "Fail: The njs is " + str(njs) + " which is greater than 12\n"
        else:
            passLog += "Pass: The njs is " + str(njs) + " which is no more than 12\n"
        if ((minReactTimeBefore != float('inf')) & (minReactTimeBefore < 500)):
            passTests = False
            failLog += "Fail: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is less than 500\n"
        else:
            passLog += "Pass: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is at least 500\n"
        if (avg_true_acc_sps > 1.5):
            passTests = False
            failLog += "Fail: The average sps counting doubles as one swing is " + str(avg_true_acc_sps) + " swings per second, which is more than 1.5\n"
        else:
            passLog += "Pass: The average sps counting doubles as one swing is " + str(avg_true_acc_sps) + " swings per second, which is no more than 1.5\n"
        if (peak_true_acc_sps > 1.75):
            passTests = False
            failLog += "Fail: The peak sps counting doubles as one swing is " + str(peak_true_acc_sps) + " swings per second, which is more than 1.75\n"
            PrintPeakSpsLog("True")
        else:
            passLog += "Pass: The peak sps counting doubles as one swing is " + str(peak_true_acc_sps) + " swings per second, which is no more than 1.75\n"
    elif (category == "Standard"):
        if (njs > 16):
            passTests = False
            failLog += "Fail: The njs is " + str(njs) + " which is greater than 16\n"
        else:
            passLog += "Pass: The njs is " + str(njs) + " which is no more than 16\n"
        if ((minReactTimeBefore != float('inf')) & (minReactTimeBefore < 350)):
            passTests = False
            failLog += "Fail: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is less than 350\n"
        else:
            passLog += "Pass: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is at least 350\n"
        if (avg_sps > 4):
            passTests = False
            failLog += "Fail: The average sps is " + str(avg_sps) + " which is greater than 4 sps\n"
        else:
            passLog += "Pass: The average sps is " + str(avg_sps) + " which is no more than 4 sps\n"
        if (peak_sps > 5.75):
            passTests = False
            failLog += "Fail: The peak sps is " + str(peak_sps) + " which is greater than 5.75 sps\n"
            PrintPeakSpsLog("Standard")
        else:
            passLog += "Pass: The peak sps is " + str(peak_sps) + " which is no more than 5.75 sps\n"
        if (hasSliders == True):
            passTests = False
            failLog += "Fail: This map has sliders\n"
        else:
            passLog += "Pass: This map does not have sliders\n"
    elif (category == "Tech"):
        if (njs > 16):
            passTests = False
            failLog += "Fail: The njs is " + str(njs) + " which is greater than 16\n"
        else:
             passLog += "Pass: The njs is " + str(njs) + " which is no more than 16\n"
        if ((minReactTimeBefore != float('inf')) & (minReactTimeBefore < 300)):
            passTests = False
            failLog += "Fail: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is less than 300\n"
        else:
            passLog += "Pass: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is at least 300\n"
        if (avg_sps > 4):
            passTests = False
            failLog += "Fail: The average sps is " + str(avg_sps) + " which is greater than 4 sps\n"
        else:
            passLog += "Pass: The average sps is " + str(avg_sps) + " which is no more than 4 sps\n"
        if (peak_sps > 5.75):
            passTests = False
            failLog += "Fail: The peak sps is " + str(peak_sps) + " which is greater than 5.75 sps\n"
            PrintPeakSpsLog("Tech")
        else:
            passLog += "Pass: The peak sps is " + str(peak_sps) + " which is no more than 5.75 sps\n"
    else:
        print("Check your category variable for spelling errors")

#Now we will deal with maps created using Chromapper
#Create columns
if (IsChromapper == True):
    temp_array = diffPath.split('/')
    
    bpmPath = temp_array[0] + '/' + temp_array[1] + '/BPMInfo.dat'
    with open(bpmPath) as bpm_json_data:
        bpmData = json.load(bpm_json_data)
    song_frequency = bpmData.get('_songFrequency')
    bpmChangesDict = bpmData.get('_regions')
    df_BPMChanges = pd.DataFrame(bpmChangesDict)
    df_BPMChanges['_change_in_time'] = (df_BPMChanges['_endSampleIndex'] - df_BPMChanges['_startSampleIndex']) / song_frequency
    df_BPMChanges['_BPM'] = (df_BPMChanges['_endBeat'] - df_BPMChanges['_startBeat']) * (60 / df_BPMChanges['_change_in_time'])
    df_BPMChanges['_time'] = df_BPMChanges['_change_in_time'].cumsum()

    df = pd.DataFrame(diffData['colorNotes'])
    df['_yCenter'] = df.loc[:, ('y')].apply(lambda x: 1 + x * 0.55)
    df['_xCenter'] = df.loc[:, ('x')].apply(lambda x: -0.9 + x * 0.6)

    #Add bpm column
    df['_bpm'] = initialBPM
    for i in range(len(df)):
        currentTime = df.loc[i, 'b']
        currentRow = 0
        for j in range(len(df_BPMChanges)):
            if currentTime >= df_BPMChanges.loc[j, '_time']:
                df['_bpm'] = df_BPMChanges.loc[j, '_BPM']
   
   
    left = (df[df['c'] == 0]) #All left handed notes
    right = (df[df['c'] == 1]) #All right handed notes

    num_notes = len(left) + len(right)

    left['_timeChange'] = left.loc[:, ['b']].diff().fillna(0)
    right['_timeChange'] = right.loc[:, ['b']].diff().fillna(0)


    left['_timeChangeSeconds'] = (60 * left['_timeChange']) / left['_bpm']
    right['_timeChangeSeconds'] = (60 * right['_timeChange']) / right['_bpm']

#Account for sliders and stacks
if (IsChromapper == True):
    EPSILON = 0.059
    firstLeftSwingIndex = left.head(1).index[0]
    firstRightSwingIndex = right.head(1).index[0]

    df_newLeftSwing = left[((((60 * left['_timeChange']) / left['_bpm']) > EPSILON) | (left.index == firstLeftSwingIndex))]
    df_newRightSwing = right[((((60 * right['_timeChange']) / right['_bpm']) > EPSILON) | (right.index == firstRightSwingIndex))]
    df_leftSliders = left[(((60 * left['_timeChange']) / left['_bpm']) < EPSILON) & (left['_timeChange'] != 0)]
    df_rightSliders = right[(((60 * right['_timeChange']) / right['_bpm']) < EPSILON) & (right['_timeChange'] != 0)]
    
    hasSliders = False
    if (len(df_leftSliders) + len(df_rightSliders) > 0):
        hasSliders = True

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


    #Statistics 
    left_swings = len(df_newLeftSwing)
    right_swings = len(df_newRightSwing)
    total_swings = len(df_newSwing)
    left_time = df_newLeftSwing['_timeChangeSeconds'].sum()
    right_time = df_newRightSwing['_timeChangeSeconds'].sum()
    right_avg_sps = right_swings / right_time
    left_avg_sps = left_swings / left_time
    left_avg_angleChange = df_newLeftSwing['_angleMagnitudeChange'].mean()
    right_avg_angleChange = df_newRightSwing['_angleMagnitudeChange'].mean()
    avg_angleChange = df_newSwing['_angleMagnitudeChange'].mean()
    total_time = df_newSwing['_timeChangeSeconds'].sum()
    avg_sps = total_swings / total_time
    num_doubles = len(df_newSwing) - len(df_ignoreDoubles)
    avg_true_acc_sps = len(df_ignoreDoubles) / df_ignoreDoubles['_timeChangeSeconds'].sum()

#The code in this cell is adapted from Uninstaller's sps calculator
if (IsChromapper == True):
    def calculate_swings_list(df_current):
        swing_list = df_current['_seconds'].tolist()
        last = math.floor(df_current['_seconds'].max())
        array = [0 for x in range(math.floor(last) + 1)]
        for swing in swing_list:
            array[math.floor(swing)] += 1
        return array

    

    def calculate_max_sps(swings_list, interval = 10):
    
        current_sps_sum = sum(swings_list[:interval])
        max_sps_sum = current_sps_sum
        for x in range(0, len(swings_list) - interval):
            current_sps_sum = current_sps_sum - swings_list[x] + swings_list[x + interval]
            max_sps_sum = max(max_sps_sum, current_sps_sum)
        return round(max_sps_sum / interval, 2)

    #peak sps statistics
    peak_left_sps = calculate_max_sps(calculate_swings_list(df_newLeftSwing))
    peak_right_sps = calculate_max_sps(calculate_swings_list(df_newRightSwing))
    peak_sps = calculate_max_sps(calculate_swings_list(df_newSwing))
    peak_true_acc_sps = calculate_max_sps(calculate_swings_list(df_ignoreDoubles))


#Create columns to help with bombs
if (IsChromapper == True):
    df['_timeChangeBefore'] = df.loc[:, ['b']].diff().fillna(0)
    df['_timeChangeBefore'] = (60 * df['_timeChangeBefore']) / df['_bpm']
    df['_timeChangeAfter'] = abs(df.loc[:, ['b']].diff(periods = -1).fillna(0))
    df['_timeChangeAfter'] = (60 * df['_timeChangeAfter']) / df['_bpm']

    #Bombs
    minReactTimeBefore = float('inf')
    minReactTimeAfter = float('inf')

   
    df_bombs = pd.DataFrame(diffData['bombNotes'])

    if (len(df_bombs) > 0):
        
        #Add bomb columns
        df_bombs['c'] = 3
        df_bombs['d'] = 8
        df_bombs['a'] = 0

        df_bombs['_yCenter'] = df_bombs.loc[:, ('y')].apply(lambda x: 1 + x * 0.55)
        df_bombs['_xCenter'] = df_bombs.loc[:, ('x')].apply(lambda x: -0.9 + x * 0.6)

        #Add bpm column
        df_bombs['_bpm'] = initialBPM
        for i in range(len(df_bombs)):
            currentTime = df_bombs.loc[i, 'b']
            currentRow = 0
            for j in range(len(df_BPMChanges)):
                if currentTime >= df_BPMChanges.loc[j, '_time']:
                     df_bombs['_bpm'] = df_BPMChanges.loc[j, '_BPM']

        df_bombs['_timeChange'] = df_bombs.loc[:, ['b']].diff().fillna(0)
        df_bombs['_timeChangeSeconds'] = (60 * df_bombs['_timeChange']) / df_bombs['_bpm']

        df_combined = pd.concat([df, df_bombs]).sort_values('b').reset_index(drop=True)
        df_combined.drop(['_timeChange', '_timeChangeSeconds', '_timeChangeBefore', '_timeChangeAfter'], axis = 1)
        df_combined['_timeChangeBefore'] = df_combined.loc[:, ['b']].diff().fillna(0)
        df_combined['_timeChangeBefore'] = (60 * df_combined['_timeChangeBefore']) / df['_bpm']
        df_combined['_timeChangeAfter'] = abs(df_combined.loc[:, ['b']].diff(periods = -1).fillna(0))
        df_combined['_timeChangeAfter'] = (60 * df_combined['_timeChangeAfter']) / df['_bpm']

        firstType = df_combined.loc[0, 'c']
        secondType = df_combined.loc[1, 'c']
        secondLastType = df_combined.loc[len(df_combined) - 2, 'c']
        lastType = df_combined.loc[len(df_combined) - 1, 'c']

        #Check for bomb at start
        if (firstType == 3) & (secondType != 3):
            minReactTimeAfter = df_combined.loc[0, '_timeChangeAfter'] * 1000

        #Check for bomb at end
        if (lastType == 3) & (secondLastType != 3):
            if (minReactTimeBefore == float('inf')) | (minReactTimeBefore > df_combined.loc[len(df) - 1, '_timeChangeBefore']):
                minReactTimeBefore = df_combined.loc[len(df_combined) - 1, '_timeChangeBefore'] 


        #Find the minimum time before and after a bomb, ignoring bombs outside the swing's path
        for i in range(len(df_combined) - 2):
            previousType = df_combined.loc[i, 'c']
            thisType = df_combined.loc[i + 1, 'c']
            nextType = df_combined.loc[i + 2, 'c']
            if thisType == 3:
                bombException = False

                #Calculate minimum time before a bomb
                if (previousType == 0) | (previousType == 1):
                    #Check for conditions where bomb is out of path of saber
                    if (df_combined.loc[i, 'y'] == 0) & (df_combined.loc[i + 1, 'y'] == 2): #Note is in bottom layer and bomb is in top layer
                        if (df_combined.loc[i, 'd'] == 2) | (df_combined.loc[i, 'd'] == 3) | (df_combined.loc[i, 'd'] == 8): #Note direction is left, right, or dot
                            bombException = True
                    elif (df_combined.loc[i, 'c'] == 0): #Note is red
                        if (df_combined.loc[i, 'y'] == 0): #Note is bottom layer
                            if (df_combined.loc[i, 'x'] == 0): #Note has leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 2) | (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in second rightmost or rightmost index
                                    #Note direction is up, down, up left, down left, or dot
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 4) | (df_combined.loc[i, 'd'] == 6) | (df_combined.loc[i, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i, 'x'] == 1): #Note has second leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in rightmost index
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second rightmost or rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0): #Bomb is in leftmost index
                                    #Note direction is up, down, down right, or dot
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 7) | (df_combined.loc[i, 'd'] == 8):
                                        bombException = True
                        elif (df_combined.loc[i, 'y'] == 2): #Note is in top layer
                            if (df_combined.loc[i, 'x'] == 0): #Note has leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 2) | (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in second rightmost or rightmost index
                                    #Note direction is up, down, up left, down left, or dot
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 4) | (df_combined.loc[i, 'd'] == 6) | (df_combined.loc[i, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i, 'x'] == 1): #Note has second leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in rightmost index
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second rightmost or rightmost index
                                if df_combined.loc[i + 1, 'x'] == 0: #Bomb is in leftmost index
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                        elif (df_combined.loc[i, 'c'] == 1): #Note is blue
                            if (df_combined.loc[i, 'y'] == 0): #Note is bottom layer
                                if (df_combined.loc[i, 'x'] == 3): #Note has rightmost index
                                    if (df_combined.loc[i + 1, 'x'] == 0) | (df_combined.loc[i + 1, 'x'] == 1): #Bomb is in second leftmost or leftmost index
                                        #Note direction is up, down, up right, down right, or dot
                                        if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 5) | (df_combined.loc[i, 'd'] == 7) | (df_combined.loc[i, 'd'] == 8):
                                            bombException = True
                            elif (df_combined.loc[i, 'x'] == 2): #Note has second rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0): #Bomb is in leftmost index
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second leftmost or leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in rightmost index
                                    #Note direction is up, down, down left, or dot
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 6) | (df_combined.loc[i, 'd'] == 8):
                                        bombException = True
                        elif (df_combined.loc[i, 'y'] == 2): #Note is in top layer
                            if (df_combined.loc[i, 'x'] == 3): #Note has rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0) | (df_combined.loc[i + 1, 'x'] == 1): #Bomb is in second leftmost or leftmost index
                                    #Note direction is up, down, up right, down right, or dot
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 5) | (df_combined.loc[i, 'd'] == 7) | (df_combined.loc[i, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i, 'x'] == 2): #Note has second rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0): #Bomb is in leftmost index
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second leftmost or leftmost index
                                if df_combined.loc[i + 1, 'x'] == 3: #Bomb is in rightmost index
                                    if (df_combined.loc[i, 'd'] == 0) | (df_combined.loc[i, 'd'] == 1) | (df_combined.loc[i, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True

                    #Update the minimum time before a bomb if needed
                    if (bombException == False) & ((minReactTimeBefore == float('inf')) | (minReactTimeBefore > df_combined.loc[i + 1, '_timeChangeBefore'])):
                        minReactTimeBefore = df_combined.loc[i + 1, '_timeChangeBefore']

                #Calculate minimum time after a bomb
                if (nextType == 0) | (nextType == 1):
                    #Check for conditions where bomb is out of path of saber
                    if (df_combined.loc[i + 2, 'y'] == 0) & (df_combined.loc[i + 1, 'y'] == 2): #Note is in bottom layer and bomb is in top layer
                        if (df_combined.loc[i + 2, 'd'] == 2) | (df_combined.loc[i + 2, 'd'] == 3) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is left, right, or dot
                            bombException = True
                    elif (df_combined.loc[i + 2, 'c'] == 0): #Note is red
                        if (df_combined.loc[i + 2, 'y'] == 0): #Note is bottom layer
                            if (df_combined.loc[i + 2, 'x'] == 0): #Note has leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 2) | (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in second rightmost or rightmost index
                                    #Note direction is up, down, up left, down left, or dot
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 4) | (df_combined.loc[i + 2, 'd'] == 6) | (df_combined.loc[i + 2, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i + 2, 'x'] == 1): #Note has second leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in rightmost index
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second rightmost or rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0): #Bomb is in leftmost index
                                    #Note direction is up, down, down right, or dot
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 7) | (df_combined.loc[i + 2, 'd'] == 8):
                                        bombException = True
                        elif (df_combined.loc[i + 2, 'y'] == 2): #Note is in top layer
                            if (df_combined.loc[i + 2, 'x'] == 0): #Note has leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 2) | (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in second rightmost or rightmost index
                                    #Note direction is up, down, up left, down left, or dot
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 4) | (df_combined.loc[i + 2, 'd'] == 6) | (df_combined.loc[i + 2, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i + 2, 'x'] == 1): #Note has second leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in rightmost index
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second rightmost or rightmost index
                                if df_combined.loc[i + 1, 'x'] == 0: #Bomb is in leftmost index
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                    elif (df_combined.loc[i + 2, 'c'] == 1): #Note is blue
                        if (df_combined.loc[i + 2, 'y'] == 0): #Note is bottom layer
                            if (df_combined.loc[i + 2, 'x'] == 3): #Note has rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0) | (df_combined.loc[i + 1, 'x'] == 1): #Bomb is in second leftmost or leftmost index
                                    #Note direction is up, down, up right, down right, or dot
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 5) | (df_combined.loc[i + 2, 'd'] == 7) | (df_combined.loc[i + 2, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i + 2, 'x'] == 2): #Note has second rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0): #Bomb is in leftmost index
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second leftmost or leftmost index
                                if (df_combined.loc[i + 1, 'x'] == 3): #Bomb is in rightmost index
                                    #Note direction is up, down, down left, or dot
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 6) | (df_combined.loc[i + 2, 'd'] == 8):
                                        bombException = True
                        elif (df_combined.loc[i + 2, 'y'] == 2): #Note is in top layer
                            if (df_combined.loc[i + 2, 'x'] == 3): #Note has rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0) | (df_combined.loc[i + 1, 'x'] == 1): #Bomb is in second leftmost or leftmost index
                                    #Note direction is up, down, up right, down right, or dot
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 5) | (df_combined.loc[i + 2, 'd'] == 7) | (df_combined.loc[i + 2, 'd'] == 8):
                                        bombException = True
                            elif (df_combined.loc[i + 2, 'x'] == 2): #Note has second rightmost index
                                if (df_combined.loc[i + 1, 'x'] == 0): #Bomb is in leftmost index
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True
                            else: #Note is in second leftmost or leftmost index
                                if df_combined.loc[i + 1, 'x'] == 3: #Bomb is in rightmost index
                                    if (df_combined.loc[i + 2, 'd'] == 0) | (df_combined.loc[i + 2, 'd'] == 1) | (df_combined.loc[i + 2, 'd'] == 8): #Note direction is up, down, or dot
                                        bombException = True

                    #Update the minimum time after a bomb if needed
                    if (bombException == False) & ((minReactTimeAfter == float('inf')) | (minReactTimeAfter > df_combined.loc[i + 1, '_timeChangeAfter'])):
                        minReactTimeAfter = df_combined.loc[i + 1, '_timeChangeAfter']

#Criteria Check
#This script does not check for towers or sliders in maps that are not tech acc
if (IsChromapper == True):
    if (minReactTimeBefore != float('inf')):
        minReactTimeBefore = math.floor(minReactTimeBefore * 1000)
    if (minReactTimeAfter != float('inf')):
        minReactTimeAfter = math.floor(minReactTimeAfter * 1000)
    avg_sps = round(avg_sps, 2)
    peak_sps = round(peak_sps, 2)
    avg_true_acc_sps = round(avg_true_acc_sps, 2)
    peak_true_acc_sps = round(peak_true_acc_sps, 2)
    total_time = round(total_time, 2)

    #General criteria checks

    #Check if time between first and last note is between 2-6 minutes inclusive
    if ((total_time < 120) | (total_time > 300)):
        passTests = False
        failLog += "Fail: The time between the first and last note is " + str(total_time) + " seconds which is outside of the range of 120 to 300 seconds\n"
    else:
        passLog += "Pass: The time between the first and last note is " + str(total_time) + " seconds which is between 120 and 300 seconds\n"
    if (((df_newLeftSwing.iloc[0].loc['d'] != 1) & (df_newLeftSwing.iloc[0].loc['d'] != 8) & (df_newLeftSwing.iloc[0].loc['d'] != 6) & (df_newLeftSwing.iloc[0].loc['d'] != 7)) | ((df_newRightSwing.iloc[0].loc['d'] != 1) & (df_newRightSwing.iloc[0].loc['d'] != 8) & (df_newRightSwing.iloc[0].loc['d'] != 6) & (df_newRightSwing.iloc[0].loc['d'] != 7))):
        passTests = False
        both_hands_start_downswing = False
        failLog += "Fail: At least one of the hands does not start on a downswing\n"
    else:
        passLog += "Pass: Both hands start on a downswing\n"
    if (num_notes < 115):
        passTests = False
        failLog += "Fail: There are " + str(num_notes) + " notes, which is less than 115\n"
    else: 
        passLog += "Pass: There are " + str(num_notes) + " notes, which is at least 115\n"
    if ((minReactTimeAfter != float('inf')) & (minReactTimeAfter < 200)):
        passTests = False
        failLog += "Fail: The minimum reaction time after a bomb is " + str(minReactTimeAfter) + " miliseconds, which is less than 200\n"
    else:
        passLog += "Pass: The minimum reaction time after a bomb is " + str(minReactTimeAfter) + " miliseconds, which is at least 200\n"

    #Category specific criteria checks
    if (category == "True"):
        if (num_notes != len(df_newSwing)):
            passTests = False
            failLog += "Fail: There are sliders, stacks, towers, or windows in this map\n"
        else:
            passLog += "Pass: There are no sliders, stacks, towers, or windows in this map\n"
        if (njs > 12):
            passTests = False
            failLog += "Fail: The njs is " + str(njs) + " which is greater than 12\n"
        else:
            passLog += "Pass: The njs is " + str(njs) + " which is no more than 12\n"
        if ((minReactTimeBefore != float('inf')) & (minReactTimeBefore < 500)):
            passTests = False
            failLog += "Fail: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is less than 500\n"
        else:
            passLog += "Pass: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is at least 500\n"
        if (avg_true_acc_sps > 1.5):
            passTests = False
            failLog += "Fail: The average sps counting doubles as one swing is " + str(avg_true_acc_sps) + " swings per second, which is more than 1.5\n"
        else:
            passLog += "Pass: The average sps counting doubles as one swing is " + str(avg_true_acc_sps) + " swings per second, which is no more than 1.5\n"
        if (peak_true_acc_sps > 1.75):
            passTests = False
            failLog += "Fail: The peak sps counting doubles as one swing is " + str(peak_true_acc_sps) + " swings per second, which is more than 1.75\n"
            PrintPeakSpsLog("True")
        else:
            passLog += "Pass: The peak sps counting doubles as one swing is " + str(peak_true_acc_sps) + " swings per second, which is no more than 1.75\n"
    elif (category == "Standard"):
        if (njs > 16):
            passTests = False
            failLog += "Fail: The njs is " + str(njs) + " which is greater than 16\n"
        else:
            passLog += "Pass: The njs is " + str(njs) + " which is no more than 16\n"
        if ((minReactTimeBefore != float('inf')) & (minReactTimeBefore < 350)):
            passTests = False
            failLog += "Fail: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is less than 350\n"
        else:
            passLog += "Pass: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is at least 350\n"
        if (avg_sps > 4):
            passTests = False
            failLog += "Fail: The average sps is " + str(avg_sps) + " which is greater than 4 sps\n"
        else:
            passLog += "Pass: The average sps is " + str(avg_sps) + " which is no more than 4 sps\n"
        if (peak_sps > 5.75):
            passTests = False
            failLog += "Fail: The peak sps is " + str(peak_sps) + " which is greater than 5.75 sps\n"
            PrintPeakSpsLog("Standard")
        else:
            passLog += "Pass: The peak sps is " + str(peak_sps) + " which is no more than 5.75 sps\n"
        if (hasSliders == True):
            passTests = False
            failLog += "Fail: This map has sliders\n"
        else:
            passLog += "Pass: This map does not have sliders\n"
    elif (category == "Tech"):
        if (njs > 16):
            passTests = False
            failLog += "Fail: The njs is " + str(njs) + " which is greater than 16\n"
        else:
            passLog += "Pass: The njs is " + str(njs) + " which is no more than 16\n"
        if ((minReactTimeBefore != float('inf')) & (minReactTimeBefore < 300)):
            passTests = False
            failLog += "Fail: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is less than 300\n"
        else:
            passLog += "Pass: The minimum reaction time before a bomb is " + str(minReactTimeBefore) + " miliseconds, which is at least 300\n"
        if (avg_sps > 4):
            passTests = False
            failLog += "Fail: The average sps is " + str(avg_sps) + " which is greater than 4 sps\n"
        else:
            passLog += "Pass: The average sps is " + str(avg_sps) + " which is no more than 4 sps\n"
        if (peak_sps > 5.75):
            passTests = False
            failLog += "Fail: The peak sps is " + str(peak_sps) + " which is greater than 5.75 sps\n"
            PrintPeakSpsLog("Tech")
        else:
            passLog += "Pass: The peak sps is " + str(peak_sps) + " which is no more than 5.75 sps\n"
    else:
        print("Check your category variable for spelling errors")

#Print command
if (passTests == True):
    print("This map passed all the Accsaber ranking critera for the " + category + " category that were checked! Triangles and other criteria that are obvious during playtests were not checked. If you wish to know detailed statistics about this map, run the following cell.")
    if (category != "Tech"):
        print("Make sure the map has no windows.")
elif (passTests == False):
    print("This map failed the Accsaber ranking critera for the " + category + " category. The failed tests that were checked are displayed below. Triangles and other criteria that are obvious during playtests were not checked. If you wish to see what tests passed, run the following cell.\n" + failLog)

#Passed tests
print(passLog)

#Format JSON
#map_name, diff, category, passTests, total_time, both_hands_start_downswing, num_notes, 
#minReactTimeBefore, minReactTimeAfter, njs, avg_sps, peak_sps

data = {
    "name": map_name, 
    "difficulty": diff,
    "category": category,
    "passCriteria": passTests,
    "time": total_time,
    "startDownswing": both_hands_start_downswing,
    "notes": num_notes,
    "reactTimeBeforeBomb": minReactTimeBefore,
    "reactTimeAfterBomb": minReactTimeAfter,
    "njs": njs,
    "averageSPS": avg_sps,
    "peakSPS": peak_sps,
}

# json_object = json.dumps(data)
# print(type(json_object))
# print(json_object)

with open("output_file.json", "w") as outfile:
    json.dump(data, outfile)