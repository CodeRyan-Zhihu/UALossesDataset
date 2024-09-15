import json
from datetime import datetime

import geopandas as gpd
import numpy as np
import pandas as pd
from geopandas import GeoSeries
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
from process import format_date


def add_oblast_raion_from_json(data, column_name, date_column, start_date=None, end_date=None):
    # 将 JSON 数据转换为 DataFrame
    df = pd.DataFrame(data)

    # 初始化 oblast 和 raion 列
    df['Oblast'] = None
    df['Raion'] = None

    oblast_value = {}
    raion_value = {}
    oblast_counter = 0
    raion_counter = 0

    for index, row in df.iterrows():
        # 过滤日期
        if start_date and end_date:
            if row[date_column] == "?":
                continue
            try:
                death_date = datetime.strptime(row[date_column], "%Y-%m-%d")
            except Exception:
                try:
                    death_date = datetime.strptime(row[date_column], "%B %d, %Y")
                except Exception:
                    continue
            if death_date < start_date or death_date > end_date:
                continue

        # 过滤没有位置信息的行
        if pd.isna(row[column_name]) or not row[column_name] or row[column_name] == "?":
            continue

        # 提取 oblast 和 raion
        location = row[column_name].split(",")
        oblast_name = location[-1].strip()
        oblast_counter += 1
        raion_name = location[-2].strip() if len(location) >= 2 else None

        # 更新 oblast 和 raion 的计数
        oblast_value.setdefault(oblast_name, 0)
        oblast_value[oblast_name] += 1
        if raion_name:
            raion_value.setdefault(raion_name, 0)
            raion_value[raion_name] += 1
            raion_counter += 1

        # 将提取的 oblast 和 raion 添加到 DataFrame
        df.at[index, 'Oblast'] = oblast_name
        df.at[index, 'Raion'] = raion_name

    return df, oblast_value, raion_value, oblast_counter, raion_counter


def map_making(title, column_name="Died in the area of", filter_time=False, start_date: datetime = None,
               end_date: datetime = None,
               date_column="Date of death"):
    '''

    :param title: For the title of map as of Raion-Level {title} Distribution Map of Ukraine
    :param column_name: options are ["Died in the area of", "From"]
    :param filter_time: bool, if True, the function will only process the data of certain date range.
    :param start_date: datetime, required when filter_time is True.
    :param end_date: datetime, required when filter_time is True.
    :param date_column: options are ["Date of birth", "Date of death", "Date of burial"]
    :return:
    '''
    data = json.load(open("soldiers_data_source.json", "r", encoding="utf-8"))

    # 读取地区数据
    if filter_time:
        df, oblast_value, raion_value, oblast_counter, raion_counter = add_oblast_raion_from_json(data, column_name, date_column, start_date, end_date)
    else:
        df, oblast_value, raion_value, oblast_counter, raion_counter = add_oblast_raion_from_json(data, column_name, date_column, None, None)
    # oblast_counter = 0
    # raion_counter = 0
    # for row in data:
    #     if filter_time:
    #         if row[date_column] == "?":
    #             continue
    #         try:
    #             death_date = datetime.strptime(row[date_column], "%Y-%m-%d")
    #         except Exception as e:
    #             # date not format
    #             try:
    #                 death_date = datetime.strptime(format_date(row[date_column]), "%B %d, %Y")
    #             except Exception as e:
    #                 # Not processable date.
    #                 continue
    #         if death_date < start_date or death_date > end_date:
    #             continue
    #     if not row[column_name] or row[column_name] == "?":
    #         continue
    #     oblast_counter += 1
    #     location = row[column_name].split(",")
    #     oblast_name = location[-1].strip()
    #     raion_name = location[-2].strip() if len(location) >= 2 else None
    #
    #     oblast_value.setdefault(oblast_name, 0)
    #     oblast_value[oblast_name] += 1
    #     if raion_name:
    #         raion_value.setdefault(raion_name, 0)
    #         raion_value[raion_name] += 1
    #         raion_counter += 1

    # 微调名称
    english_to_ukrainian = {
        'Autonomous Republic of Crimea': 'Avtonomna Respublika Krym',
        'Vinnytsia': 'Vinnytska',
        'Volyn': 'Volynska',
        'Dnipropetrovsk': 'Dnipropetrovska',
        'Donetsk': 'Donetska',
        'Zhytomyr': 'Zhytomyrska',
        'Zakarpattia': 'Zakarpatska',
        'Zaporizhzhia': 'Zaporizka',
        'Ivano-Frankivsk': 'Ivano-Frankivska',
        'Kyiv': 'Kyivska',
        'Kirovohrad': 'Kirovohradska',
        'Luhansk': 'Luhanska',
        'Lviv': 'Lvivska',
        'Mykolaiv': 'Mykolaivska',
        'Odesa': 'Odeska',
        'Poltava': 'Poltavska',
        'Rivne': 'Rivnenska',
        'Sumy': 'Sumska',
        'Ternopil': 'Ternopilska',
        'Kharkiv': 'Kharkivska',
        'Kherson': 'Khersonska',
        'Khmelnytskyi': 'Khmelnytska',
        'Cherkasy': 'Cherkaska',
        'Chernivtsi': 'Chernivetska',
        'Chernihiv': 'Chernihivska',
        'Sevastopol': 'Sevastopilska'
    }
    new_oblast_value = {}
    for key in oblast_value:
        new_oblast_value[english_to_ukrainian[key.replace(" Oblast", "")]] = oblast_value[key]

    # oblast_value['Zaporizhia Oblast'] = oblast_value['Zaporizhzhia Oblast']
    # oblast_value['Odessa Oblast'] = oblast_value['Odesa Oblast']

    # 按照州级绘制
    ukraine_map = gpd.read_file("map/geoBoundaries-UKR-ADM1.geojson")
    ukraine_map['value'] = ukraine_map['shapeName'].map(new_oblast_value)
    # print(ukraine_map['shapeName'])
    fig, ax = plt.subplots(1, 1, figsize=(25, 15))
    ukraine_map.boundary.plot(ax=ax, linewidth=1, color='black')
    # ukraine_map.plot(column='value', ax=ax, legend=True, cmap='OrRd', missing_kwds={'color': 'lightgrey'})

    # 自定义颜色映射和图例
    cmap = plt.cm.OrRd
    norm = mcolors.BoundaryNorm(boundaries=[0, 100, 500, 1000, 2000, 3000, 4000, 5000], ncolors=cmap.N)

    # 绘制地图
    plot = ukraine_map.plot(column='value', ax=ax, cmap=cmap, norm=norm, legend=True,
                            legend_kwds={'label': "Death", 'orientation': "vertical", 'extend': 'max'})

    # 计算每个oblast的几何中心（质心）并标注名字
    ukraine_map['centroid'] = ukraine_map.geometry.centroid
    for idx, row in ukraine_map.iterrows():
        plt.text(row['centroid'].x, row['centroid'].y,
                 row['shapeName'] + "-" + str(new_oblast_value[row['shapeName']]) if row[
                                                                                         'shapeName'] in new_oblast_value else
                 row[
                     'shapeName'], fontsize=8, ha='center')

    # 调整图例顶部显示'>5000'
    cbar = plot.get_figure().get_axes()[1]
    cbar.set_yticks([100, 500, 1000, 2000, 3000, 4000, 5000])
    cbar.set_yticklabels(['100', '500', '1000', '2000', '3000', '4000', '>5000'])

    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)  # 缩小边距
    plt.title(f'Oblast-Level {title} Distribution Map of Ukraine')
    plt.savefig(f"oblast_level_{title.lower().replace(' ', '_')}_distribution.png")

    # 处理乌克兰语二级行政区
    raion_value['Sievierodonetsk District'] = raion_value['Sieverodonetsk District']
    del raion_value['Sieverodonetsk District']

    special_change = {
        "Bucha": "Buchanskyi",
        "Dnipro": "Dniprovskyi",
        "Lubny": "Lubenskyi",
        "Dubno": "Dubenskyi",
        "Romny": "Romenskyi",
        "Chernivtsi": "Cnernivetskyi",
    }

    stupid_change = {
        "Zaporizhzhiaskyi": "Zaporizkyi",
        'Berehoveskyi': 'Berehivskyi',
        'Drohobycskyi': 'Drohobytskyi',
        'Kolomyiaskyi': 'Kolomyiskyi',
        'Kryvyi Riskyi': 'Kryvorizkyi',
        'Mukachevoskyi': 'Mukachivskyi',
        'Nadvirnaskyi': 'Nadvirnianskyi',
        'Odesaskyi': 'Odeskyi',
        'Oleksandriiaskyi': 'Oleksandriiskyi',
        'Pologskyi': 'Polohivskyi',
        'Poltavaskyi': 'Poltavskyi',
        'Prylukskyi': 'Prylutskyi',
        'Rivneskyi': 'Rivnenskyi',
        'Rovenkskyi': 'Rovenkivskyi',
        'Rozdilnaskyi': 'Rozdilnianskyi',
        'Sarnskyi': 'Sarnenskyi',
        'Shchastiaskyi': 'Shchastynskyi',
        'Shostskyi': 'Shostkynskyi',
        'Svatoveskyi': 'Svativskyi',
        'Synelnykoveskyi': 'Synelnykivskyi',
        'Vinnytsiaskyi': 'Vinnytskyi',
        'Volnovakhaskyi': 'Volnovaskyi',
        'Vyzhnytsiaskyi': 'Vyzhnytskyi',
        'Zolotonoshaskyi': 'Zolotoniskyi',
        'Lozovaskyi': 'Lozivskyi',
        'Bila Tserkvaskyi': 'Bilotserkivskyi',
        'Verkhovynaskyi': 'Verkhovynskyi',
    }

    new_raion_value = {}
    for key in raion_value:
        last = key.replace(" District", "")
        if last in special_change:
            new_raion_value[special_change[last]] = raion_value[key]
        else:
            if last[-4:] == "skyi":
                new_raion_value[key.replace(" District", "")] = raion_value[key]
            elif last[-3:] == "ske":
                new_raion_value[key.replace("e District", "yi")] = raion_value[key]
            elif last[-2:] == "sk":
                new_raion_value[key.replace(" District", "yi")] = raion_value[key]
            elif last[-2:] == "ka":
                new_raion_value[key.replace("ka District", "skyi")] = raion_value[key]
            elif last[-2:] == "sy":
                new_raion_value[key.replace("sy District", "skyi")] = raion_value[key]
            elif last[-2:] == "sh":
                new_raion_value[key.replace("sh District", "skyi")] = raion_value[key]
            elif last[-1:] == "y":
                new_raion_value[key.replace("y District", "skyi")] = raion_value[key]
            elif last[-1:] == "s":
                new_raion_value[key.replace(" District", "kyi")] = raion_value[key]
            elif last[-1:] == "k":
                new_raion_value[key.replace("k District", "tskyi")] = raion_value[key]
            elif last[-1:] == "h":
                new_raion_value[key.replace("h District", "skyi")] = raion_value[key]
            else:
                new_raion_value[key.replace(" District", "skyi")] = raion_value[key]
    raion_value = {}
    for key in new_raion_value:
        if key in stupid_change:
            raion_value[stupid_change[key]] = new_raion_value[key]
        else:
            raion_value[key] = new_raion_value[key]
    del new_raion_value
    raion_value['Kyivska'] = new_oblast_value['Kyivska']

    print(title, "|Oblast counter:", oblast_counter)
    print(title, "|Raion counter:", raion_counter)

    # 按照区级绘制
    ukraine_map = gpd.read_file("map/geoBoundaries-UKR-ADM2.geojson")
    ukraine_map['value'] = ukraine_map['shapeName'].map(raion_value)
    # print(sorted(set(raion_value).difference(set(ukraine_map['shapeName']))))
    fig, ax = plt.subplots(1, 1, figsize=(25, 15))
    ukraine_map.boundary.plot(ax=ax, linewidth=1, color='black')
    # ukraine_map.plot(column='value', ax=ax, legend=True, cmap='OrRd', missing_kwds={'color': 'lightgrey'})
    # print(sorted(set(ukraine_map['shapeName']).difference(set(raion_value))))

    # 自定义颜色映射和图例
    cmap = plt.cm.OrRd
    norm = mcolors.BoundaryNorm(boundaries=[0, 200, 400, 600, 800, 1000, 1200, 1500], ncolors=cmap.N)

    # 绘制地图
    plot = ukraine_map.plot(column='value', ax=ax, cmap=cmap, norm=norm, legend=True,
                            legend_kwds={'label': "Death", 'orientation': "vertical", 'extend': 'max'})

    # 计算每个oblast的几何中心（质心）并标注名字
    ukraine_map['centroid'] = ukraine_map.geometry.centroid
    for idx, row in ukraine_map.iterrows():
        plt.text(row['centroid'].x, row['centroid'].y,
                 row['shapeName'] + "-" + (
                     str(raion_value[row['shapeName']]) if row['shapeName'] in raion_value else 'N/A'),
                 fontsize=6,
                 ha='center')

    # 调整图例顶部显示'>1500'
    cbar = plot.get_figure().get_axes()[1]
    cbar.set_yticks([200, 400, 600, 800, 1000, 1200])
    cbar.set_yticklabels(['200', '400', '600', '800', '1200', '>1500'])

    plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)  # 缩小边距
    plt.title(f'Raion-Level {title} Distribution Map of Ukraine')
    plt.savefig(f"raion_level_{title.lower().replace(' ', '_')}_distribution.png")


if __name__ == "__main__":
    processing_type = "Died in the area of"  # 分析是From，分析阵亡地是Died in the area of
    map_making("Death", processing_type)

    processing_type = "From"  # 分析是From，分析阵亡地是Died in the area of
    map_making("Hometown", processing_type)
