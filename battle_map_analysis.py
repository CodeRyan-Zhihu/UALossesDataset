from datetime import datetime

from map_analysis import map_making
from battle_analysis import BATTLE_LIST

if __name__ == '__main__':
    BATTLE_LIST[1] = {'start': "2022-05-06", 'end': "2022-07-03", 'label': "Battle of Lysychansk and Sievierodonetsk", 'color':'skyblue'}
    for battle in BATTLE_LIST:
        map_making(battle['label'] + " Death", "Died in the area of", filter_time=True,
                   start_date=datetime.strptime(battle["start"], "%Y-%m-%d"),
                   end_date=datetime.strptime(battle["end"], "%Y-%m-%d"),
                   date_column="Date of death")
        map_making(battle['label'] + " Hometown", "From", filter_time=True,
                   start_date=datetime.strptime(battle["start"], "%Y-%m-%d"),
                   end_date=datetime.strptime(battle["end"], "%Y-%m-%d"),
                   date_column="Date of death")
