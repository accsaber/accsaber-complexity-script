import pandas as pd
import json
import math

def get_pythagoras(x, y):
    return math.sqrt(x ** 2 + y ** 2)
diffPath = "accsaber-maps/1a2f6 (Digital World - SlimyBlob)/HardStandard.dat" #Replace with your diffFilePath
infoPath = "accsaber-maps/1a2f6 (Digital World - SlimyBlob)/Info.dat" #Replace with your infoPath
with open(diffPath) as diff_json_data:
    diffData = json.load(diff_json_data)
df = pd.DataFrame(diffData['_notes'])
df['_yCenter'] = df.loc[:, ('_lineLayer')].apply(lambda x: 1 + x * 0.55)
df['_xCenter'] = df.loc[:, ('_lineIndex')].apply(lambda x: -0.9 + x * 0.6)
left = (df[df['_type'] == 0]) #All left handed notes
right = (df[df['_type'] == 1]) #All right handed notes

left['_xMovement'] = left.loc[:, ['_xCenter']].diff().fillna(0)
left['_yMovement'] = left.loc[:, ['_yCenter']].diff().fillna(0)
left['_totMovement'] = left.apply(lambda x: get_pythagoras(x['_xMovement'], x['_yMovement']), axis=1).fillna(0) 
left['_angleChange'] = left.apply(lambda x: math.atan(x['_yMovement']/x['_xMovement']), axis=1)
left['_timeChange'] = left.loc[:, ['_time']].diff().fillna(0)

right['_xMovement'] = right.loc[:, ['_xCenter']].diff().fillna(0)
right['_yMovement'] = right.loc[:, ['_yCenter']].diff().fillna(0)
right['_totMovement'] = right.apply(lambda x: get_pythagoras(x['_xMovement'], x['_yMovement']), axis=1).fillna(0)
right['_angleChange'] = right.apply(lambda x: math.atan(x['_yMovement']/x['_xMovement']), axis=1)
right['_timeChange'] = left.loc[:, ['_time']].diff().fillna(0)

average_angle = (left['_angleChange'].mean() + right['_angleChange'].mean()) / 2
time = 0
for i in left:
    if (left.loc[i, '_timeChange'] > 5):
        time += left.loc[i, '_timeChange']
for i in right:
    if (right.loc[i, '_timeChange'] > 5):
        time += right.loc[i, '_timeChange']


total_distance = 0
for i in left:
    if (left.loc[i, '_totMovement'] > 0.54):
        total_distance += left.loc[i, '_totMovement']
for i in right:
    if (right.loc[i, '_totMovement'] > 0.54):
        total_distance += right.loc[i, '_totMovement']

df['timeChangeBefore'] = df.loc[:, ['_time']].diff().fillna(0)
df['timeChangeAfter'] = df.loc[:, ['_time']].diff(periods = -1).fillna(0)
df_bombs = df[df['_type'] == 3]
minReactTimeBefore = df_bombs.iloc[1]['timeChangeBefore']
minReactTimeAfter = df_bombs.iolc[0]['timeChangeAfter']
for i in range(2, df_bombs.len()):
    if (df.iloc[i]['timeChangeBefore'] < minReactTimeBefore):
        minReactTimeBefore = df.iloc[i]['timeChangeBefore']
for i in range(1, df_bombs.len() - 1):
    if (df.iloc[i]['timeChangeAfter'] < minReactTimeAfter):
        minReactTimeAfter = df.iloc[i]['timeChangeAfter']

avg_speed = total_distance/time
print("The shortest reaction time before a bomb is " + minReactTimeBefore)
print("The shortest reaction time after a bomb is " + minReactTimeAfter)
print("The average speed is" + avg_speed)

#complexity_speed= avg_speed*15
#complexity_angle= average_angle

#complexity = complexity_angle + complexity_speed

# print(complexity)
