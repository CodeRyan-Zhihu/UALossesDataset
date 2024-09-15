import pandas as pd

from UALosses.map_analysis import add_oblast_raion_from_json
from battle_analysis import data_transform, print_weekly_graph
choice = {
'Bakhmut District':"Bakhmut Battle Death",
'Pokrovsk District':"Avdiivka-Pokrovsk Battle Death"
}
df = pd.read_csv('war_data_clean.csv')
df, oblast_value, raion_value, oblast_counter, raion_counter = add_oblast_raion_from_json(df, "Died in the area of", "Date of death", start_date=None, end_date=None)
for key,item in choice.items():
    weekly_counts = data_transform(df,'Date of death', 'Raion', key)
    print_weekly_graph(weekly_counts,"bar",item,battle=True,top=250)