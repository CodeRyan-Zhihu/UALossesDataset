# 进度文件
import json
import os
import re
from datetime import datetime

import pandas as pd
from tqdm import tqdm

# UA Losses的月份简写并不是标准形式
def format_date(date_str):
    return date_str.replace("Jan.", "January").replace("Feb.", "February").replace("Aug.", "August") \
        .replace("Sept.", "September").replace("Oct.", "October").replace("Nov.", "November") \
        .replace("Dec.", "December")


def verify_dates(row):
    # 经检验全部相符
    # 使用正则表达式提取 Name 中的日期部分
    match = re.search(r'\((.*?)- (.*?)\)', row['Name'])
    if match:
        birth_date_from_name = format_date(match.group(1).strip())
        death_date_from_name = format_date(match.group(2).strip())

        # 比较提取的日期与 DataFrame 中的日期
        birth_match = birth_date_from_name == row['Date of birth']
        death_match = death_date_from_name == row['Date of death']

        # 输出比较结果
        # print(f"Name: {name_cleaned}")
        # print(f"Birth Date Matches: {birth_match}, Death Date Matches: {death_match}")
        # print(f"Extracted Birth Date: {birth_date_from_name}, Actual Birth Date: {row['Date of birth']}")
        # print(f"Extracted Death Date: {death_date_from_name}, Actual Death Date: {row['Date of death']}\n")
        if birth_match and death_match:
            return True
        else:
            return False
    else:
        print(f"No valid date format found in Name field of {row['Name']}")
        return False

# 定义日期比较函数
def is_after_target_date(date_str, target_date):
    try:
        # 将字符串转换为日期对象
        date_str = format_date(date_str)
        date_obj = datetime.strptime(date_str, '%B %d, %Y')  # %B表示月份全拼
        # 检查日期是否在目标日期之后
        return date_obj >= target_date
    except ValueError:
        return False  # 如果日期解析失败，则返回False


if __name__ == '__main__':
    progress_file = "progress.json"
    save_progress_file = "save_progress.json"
    duplicate_remove_file = "soldiers_data_source.json"
    unknown_death_remove_file = "soldiers_data_remove_unknown_death_date.json"
    war_death_file = "war_data.csv"


    with open(progress_file, "r", encoding="utf-8") as f:
        progress = json.load(f)
    with open(save_progress_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 清除重复
    print(len(data))
    duplicate = set()
    remove_duplicate = []
    for item in tqdm(data):
        if item["Name"] not in duplicate:
            duplicate.add(item["Name"])
            remove_duplicate.append(item)
        else:
            continue
    print("UA Losses all:", len(remove_duplicate))
    with open(duplicate_remove_file, "w", encoding="utf-8") as f:
        json.dump(remove_duplicate, f, ensure_ascii=False, indent=True)
    del data

    # 应用清理和验证函数, 找到2022年以后战争死亡
    counter = 0
    for i in tqdm(range(len(remove_duplicate))):
        # 清理 Name 字段中的换行符和多余空格
        row = remove_duplicate[i]
        name_cleaned = re.sub(r'[\n\s]+', ' ', row['Name']).strip()
        row['Name'] = name_cleaned
        row['Date of birth'] = format_date(row['Date of birth'])
        row['Date of death'] = format_date(row['Date of death'])
        row['Date of burial'] = format_date(row['Date of burial'])
        if not verify_dates(row):
            counter += 1
        else:
            row['Name'] = re.sub(r'\s*\(.*?\)\s*', '', row['Name']).strip()

    temp = pd.DataFrame(remove_duplicate)
    temp.to_csv("soldiers_data_source.csv", index=False, encoding="utf-8")

    # 清除死亡时间不明
    remove_unknown_death = []
    for item in tqdm(remove_duplicate):
        if item["Date of death"] == "?":
            continue
        remove_unknown_death.append(item)
    print("Death date existed:", len(remove_unknown_death))
    with open(unknown_death_remove_file, "w", encoding="utf-8") as f:
        json.dump(remove_unknown_death, f, ensure_ascii=False, indent=True)

    # 将 JSON 数据转换为 DataFrame
    df = pd.DataFrame(remove_unknown_death)



    # 设置目标日期为 2022 年 2 月 24 日
    target_date = datetime(2022, 2, 24)

    # 筛选出 'Date of death' 晚于目标日期的数据
    filtered_data = df[df['Date of death'].apply(lambda x: is_after_target_date(x, target_date))]
    print("Died after 2022-02-24:", len(filtered_data))

    filtered_data.to_csv(war_death_file, index_label="#")
    filtered_data = json.loads(filtered_data.to_json(orient="records", lines=False))

