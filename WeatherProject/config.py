# -*- coding: utf-8 -*-
"""
天气项目配置文件
"""

import os

# 基础配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# 创建必要的目录
for dir_path in [DATA_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

# 爬虫配置
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 目标网站配置
WEATHER_URLS = {
    'china_weather': 'https://www.weather.com.cn/weather/101020600.shtml',  # 中国天气网-浦东新区
    'tianqi_so': 'https://tianqi.so.com/weather/101020600',  # 全国天气网-浦东新区
    'moji': 'https://tianqi.moji.com/weather/china/shanghai/pudong-new-district'  # 墨迹天气-浦东新区
}

# 请求配置
REQUEST_DELAY = 2  # 请求间隔（秒）
TIMEOUT = 10  # 请求超时时间（秒）
MAX_RETRIES = 3  # 最大重试次数

# 数据库配置（如果需要）
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '',
    'database': 'weather_db',
    'charset': 'utf8mb4'
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(LOGS_DIR, 'weather.log')
}

# 数据文件配置
DATA_FILES = {
    'weather_data': os.path.join(DATA_DIR, 'weather_data.csv'),
    'processed_data': os.path.join(DATA_DIR, 'processed_weather.json'),
    'charts': os.path.join(DATA_DIR, 'charts')
}

# 创建图表目录
os.makedirs(DATA_FILES['charts'], exist_ok=True)