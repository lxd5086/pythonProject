# 百度贴吧数据分析爬虫项目

## 项目简介
这是一个用于爬取百度贴吧数据并进行分析的Python项目。

## 项目结构
```
TieBa/
├── data/                    # 数据目录
│   ├── raw/                # 原始数据
│   ├── processed/          # 处理后数据
│   └── dictionaries/       # 词典文件
├── output/                 # 输出目录
│   ├── figures/           # 图表文件
│   └── reports/           # 分析报告
├── src/                   # 源代码
│   ├── utils/            # 工具模块
│   ├── config.py         # 配置文件
│   ├── selenium_scraper.py   # 爬虫模块
│   ├── data_cleaner.py   # 数据清理模块
│   ├── analyzer.py       # 分析模块
│   └── main.py          # 主入口
├── README.md
└── requirements.txt
```

## 安装依赖
```bash
pip install -r requirements.txt
```

## 使用说明
1. 配置参数：编辑 `src/config.py`
2. 运行爬虫：`python src/main.py`

## 注意事项
- 请遵守贴吧robots.txt规则
- 合理设置爬取频率，避免给服务器造成压力
- 仅用于学习和研究目的
