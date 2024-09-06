import json

from tqdm import tqdm

data = json.load(open('soldiers_data_source.json', "r", encoding="utf-8"))
counter = 0
for item in tqdm(data):
    if item["Date of death"] == "?":
        if item["Date of burial"] != "?":
            counter += 1

print("Death date existed:", counter)