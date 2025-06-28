# src/config.py

import os
from matplotlib import font_manager

# --- 基础路径配置 ---
# 项目根目录 (TieBa/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- 数据输入/输出路径 ---
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

RAW_DATA_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
DICT_DIR = os.path.join(DATA_DIR, "dictionaries")
FIGURES_DIR = os.path.join(OUTPUT_DIR, "figures")

# --- 爬虫配置 ---
TIEBA_NAME = "数据科学与大数据技术"
SEARCH_PAGES = 2  # 在搜索结果页翻几页来寻找帖子
MAX_THREADS_TO_SCRAPE = 10  # 最多爬取多少个帖子
MAX_REPLIES_PER_THREAD = 50 # 每个帖子最多爬取多少条回复

# --- 文件路径配置 ---
RAW_DATA_PATH = os.path.join(RAW_DATA_DIR, "1_raw_posts.csv")
CLEANED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "2_cleaned_data.csv")
ANALYZED_DATA_PATH = os.path.join(PROCESSED_DATA_DIR, "3_analyzed_data.csv")

# --- 词典文件配置 ---
# 加载您提到的所有停用词表
STOPWORDS_FILES = [
    os.path.join(DICT_DIR, "baidu.txt"),
    os.path.join(DICT_DIR, "哈工大停用词表.txt"),
    os.path.join(DICT_DIR, "四川大学机器智能实验室停用词库.txt"),
    os.path.join(DICT_DIR, "中文停用词表.txt"),
]
# 权威情感词典路径
DUT_SENTIMENT_PATH = os.path.join(DICT_DIR, "情感词汇本体.xlsx")

# --- 可视化配置 ---
FONT_LIST = ['SimHei', 'Heiti SC', 'PingFang SC', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
try:
    AVAILABLE_FONT = next((font for font in FONT_LIST if font_manager.findfont(font, fallback_to_default=False)), None)
except NameError: # 以防matplotlib未安装
    AVAILABLE_FONT = None