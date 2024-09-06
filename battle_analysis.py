import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import patches

# 读取 CSV 文件
df = pd.read_csv('war_data_clean.csv')

# 将 'Date of death' 转换为日期格式，并将无效日期转换为 NaT（Not a Time）
df['Date of death'] = pd.to_datetime(df['Date of death'], format='%B %d, %Y', errors='coerce')

# 删除无效日期的行
df = df.dropna(subset=['Date of death'])

# 将 'Date of death' 设置为索引
df.set_index('Date of death', inplace=True)

# 按周分组并统计每周的数量
weekly_counts = df.resample('7D').size()
weekly_counts.index = weekly_counts.index.to_series().dt.strftime('%Y-%m-%d')

# 绘制柱状图
plt.figure(figsize=(14, 7))
ax = weekly_counts.plot(kind='bar', color='lightcoral') # 绘制折线图请改kind='line',柱状图kind='bar'

# 格式化 x 轴日期
# ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))  #柱状图请恢复此句，每隔 2 周显示一个标签
plt.xlim(left=0)
plt.ylim(bottom=0)


plt.title('Weekly Death Counts')
plt.xlabel('Week')
plt.ylabel('Number of Deaths')
plt.xticks(rotation=45)  # 旋转 x 轴标签以提高可读性
plt.tight_layout()  # 调整布局以避免标签被剪裁

battle_list = [
    {'start': "2022-02-24", 'end': "2022-03-31", 'label': "Battle of Kyiv", 'color': 'orange'},
    {'start': "2022-08-29", 'end': "2022-11-11", 'label': "Battle of Kherson & Kharkov", 'color': 'lightgreen'},
    ##{'start': "2022-09-01", 'end': "2022-11-30", 'label': "Battle of Kharkov"},
    {'start': "2022-12-01", 'end': "2023-04-30", 'label': "Battle of Bahkmut", 'color': 'skyblue'},
    {'start': "2023-06-04", 'end': "2023-10-31", 'label': "Battle of Zhaporizhia", 'color': 'orange'},
    {'start': "2023-10-10", 'end': "2024-02-17", 'label': "Battle of Avdiivka", 'color': 'lightgreen'},

]


# 添加战役标注
def mark_battle(battle, weekly_counts):
    # 添加红框和标注
    battle_start = pd.to_datetime(battle['start'])
    battle_end = pd.to_datetime(battle['end'])

    # 找到最接近的开始和结束日期
    start_idx =  np.abs((pd.to_datetime(weekly_counts.index) - battle_start).days)
    end_idx = np.abs((pd.to_datetime(weekly_counts.index) - battle_end).days)
    start_idx = weekly_counts.index[np.argmin(start_idx)]
    end_idx = weekly_counts.index[np.argmin(end_idx)]

    # 找到索引位置
    start_idx_pos = weekly_counts.index.get_loc(start_idx)
    end_idx_pos = weekly_counts.index.get_loc(end_idx)

    # 绘制矩形框
    rect = patches.Rectangle(
        (start_idx_pos - 0.5, 0),
        (end_idx_pos - start_idx_pos + 1),
        weekly_counts.max(),
        linewidth=2,
        edgecolor=battle['color'],
        facecolor='none'
    )
    ax.add_patch(rect)

    # 添加标注
    plt.text(
        (start_idx_pos + end_idx_pos) / 2,
        weekly_counts.max() * 0.9,
        battle['label'],
        horizontalalignment='center',
        color=battle['color'],
        fontsize=10,
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none')
    )

# 注释此部分打印原始图像
for item in battle_list:
    mark_battle(item, weekly_counts)

# 显示图表
plt.savefig('weekly_counts_bar.png') # TODO 改为默认格式
