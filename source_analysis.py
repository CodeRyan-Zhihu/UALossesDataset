import json
from tqdm import tqdm
import csv

# 一些奇葩站点的多域名字典
URL_DUPLICATE = {
    'm.facebook.com': 'facebook.com'
}

# 读取数据
data = json.load(open("soldiers_data_source.json","r",encoding="utf-8"))
counter = {}
google_docs = set()

# 将url切割并拆出主域名
for row in tqdm(data):
    urls = row["Sources"].split(",")
    duplicate = set()
    for url in urls:
        temp = url.replace("https://", "").replace("http://", "")
        main_field = temp.split("/")[0].strip().replace("www.","")
        if main_field in URL_DUPLICATE:
            main_field = URL_DUPLICATE[main_field]
        if main_field not in duplicate:
            duplicate.add(main_field)
            counter.setdefault(main_field, 0)
            counter[main_field] += 1
        if main_field == "docs.google.com":
            google_docs.add(url)

#排序
sorted_counter = sorted(counter.items(), key=lambda item: item[1], reverse=True)

# 输出文件名
output_file = 'announcement_source.csv'

# 打开文件并写入数据
with open(output_file, mode='w',encoding="utf-8", newline='') as file:
    writer = csv.writer(file)

    # 写入表头
    writer.writerow(['Source', 'Number'])

    # 写入数据行
    for key, value in sorted_counter:
        writer.writerow([key, value])
#
# print(f'Data has been written to {output_file}')
#
# print(len(counter))

print(google_docs)
