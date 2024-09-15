import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import patches
from scipy.stats import shapiro, normaltest, anderson, beta, kstest, alpha

from UALossesDataset.battle_analysis import weekly_counts

BATTLE_LIST = [
    {'start': "2022-02-24", 'end': "2022-04-02", 'label': "Battle of Kyiv", 'color': 'orange'},
    {'start': "2022-05-06", 'end': "2022-07-03", 'label': "Battle of Lysychansk\n&Sievierodonetsk", 'color': 'skyblue'},
    {'start': "2022-08-29", 'end': "2022-11-11", 'label': "Battle of Kherson & Kharkov", 'color': 'lightgreen'},
    ##{'start': "2022-09-01", 'end': "2022-11-30", 'label': "Battle of Kharkov"},
    {'start': "2022-12-01", 'end': "2023-04-30", 'label': "Battle of Bahkmut", 'color': 'skyblue'},
    {'start': "2023-06-04", 'end': "2023-10-31", 'label': "Battle of Zhaporizhia", 'color': 'orange'},
    {'start': "2023-10-10", 'end': "2024-02-17", 'label': "Battle of Avdiivka", 'color': 'lightgreen'},

]


# 添加战役标注
def mark_battle(battle, weekly_counts, ax):
    # 添加红框和标注
    battle_start = pd.to_datetime(battle['start'])
    battle_end = pd.to_datetime(battle['end'])

    # 找到最接近的开始和结束日期
    start_idx = np.abs((pd.to_datetime(weekly_counts.index) - battle_start).days)
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
        facecolor='none',
        alpha=0.7,
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
        bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'),
        alpha = 0.7,
    )


def print_weekly_graph(data, graph_type, title, color='lightcoral', battle=True, top=None):
    # 绘制柱状图
    plt.figure(figsize=(14, 7))
    ax = data.plot(kind=graph_type, color=color)  # 绘制折线图请改kind='line',柱状图kind='bar'

    # 格式化 x 轴日期
    if graph_type == "bar":
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))  # 柱状图每隔 2 周显示一个标签
    plt.xlim(left=0)
    plt.ylim(bottom=0)
    if top:
        plt.ylim(top=top)

    plt.title(f'Weekly {title} Counts')
    plt.xlabel('Week')
    plt.ylabel(f'Number of {title}s')
    plt.xticks(rotation=45)  # 旋转 x 轴标签以提高可读性
    plt.tight_layout()  # 调整布局以避免标签被剪裁

    # Battl=False, 打印原始图像
    if battle:
        for item in BATTLE_LIST:
            mark_battle(item, data, ax)

    # 显示图表
    plt.savefig(f'weekly_counts_{title}_{graph_type}.png')
    print(len(data))


def data_transform(df, date_column='Date of death', column=None, filter=None):
    # 如果有设置筛选，根据设置的筛选来进行
    if column and filter is not None:
        df = df[df[column]==filter]

    # 将 'Date of death' 转换为日期格式，并将无效日期转换为 NaT（Not a Time）
    df[date_column] = pd.to_datetime(df[date_column], format='%B %d, %Y', errors='coerce')

    # 删除无效日期的行
    df = df.dropna(subset=['Date of death'])

    # 将 'Date of death' 设置为索引
    df.set_index('Date of death', inplace=True)

    # 按周分组并统计每周的数量
    weekly_counts = df.resample('7D').size()
    weekly_counts.index = weekly_counts.index.to_series().dt.strftime('%Y-%m-%d')
    return weekly_counts


if __name__ == '__main__':
    # 读取 CSV 文件
    df = pd.read_csv('war_data_clean.csv')

    weekly_counts = data_transform(df, None, None)

    # 打印图像
    print_weekly_graph(weekly_counts, "line", "Death", battle=True)
    print_weekly_graph(weekly_counts, "bar", "Death", battle=True)

    # 绘制直方图
    plt.figure(figsize=(14, 7))
    counts, bins, patches = plt.hist(weekly_counts, bins=range(0, int(weekly_counts.max()) + 50, 50),
                                     color='lightcoral', edgecolor='black')

    # 添加每个柱子的数字标记
    for count, bin_edge in zip(counts, bins[:-1]):
        plt.text(bin_edge + 25, count, str(int(count)), ha='center', va='bottom')

    # 设置标题和标签
    plt.title('Distribution of Weekly Death Counts')
    plt.xlabel('Number of Deaths per Week')
    plt.ylabel('Number of Weeks')
    plt.xticks(range(0, int(weekly_counts.max()) + 50, 50))  # 设置x轴刻度

    # 显示图表
    plt.tight_layout()  # 调整布局以避免标签被剪裁
    plt.savefig('weekly_counts_histogram.png')

    # 进行正态性检验
    print("\nShapiro-Wilk Test:")
    shapiro_test = shapiro(weekly_counts)
    print(f"Statistic: {shapiro_test.statistic}, p-value: {shapiro_test.pvalue}")

    print("\nD'Agostino's K-squared Test:")
    dagostino_test = normaltest(weekly_counts)
    print(f"Statistic: {dagostino_test.statistic}, p-value: {dagostino_test.pvalue}")

    print("\nAnderson-Darling Test:")
    anderson_test = anderson(weekly_counts)
    print(f"Statistic: {anderson_test.statistic}")
    for i in range(len(anderson_test.critical_values)):
        sl, cv = anderson_test.significance_level[i], anderson_test.critical_values[i]
        print(f"Significance Level {sl}: Critical Value {cv}")

    print("\nKolmogorov-Smirnov Test:")
    temp_data = (weekly_counts - np.min(weekly_counts)) / (np.max(weekly_counts) - np.min(weekly_counts))
    D, p_value = kstest(temp_data, 'beta', args=(2, 5))
    print(f"Statistic: {D}, p-value: {p_value}")
