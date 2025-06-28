#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度贴吧爬虫项目架构生成脚本
用于在PyCharm中快速创建项目目录结构和文件
"""

import os
import sys


def create_project_structure():
	"""创建项目目录结构"""

	# 项目根目录
	project_name = "TieBa"

	# 定义项目结构
	project_structure = {
		# 数据目录
		"data": {
			"raw": {},  # 原始数据目录
			"processed": {},  # 处理后数据目录
			"dictionaries": {}  # 词典文件目录
		},

		# 输出目录
		"output": {
			"figures": {},  # 图表文件目录
			"reports": {}  # 分析报告目录
		},

		# 源代码目录
		"src": {
			"utils": {},  # 工具模块目录
			"__init__.py": "",  # 包初始化文件
			"config.py": "",  # 配置文件
			"selenium_scraper.py": "",  # 爬虫模块
			"data_cleaner.py": "",  # 数据清理模块
			"analyzer.py": "",  # 分析模块
			"main.py": ""  # 主入口文件
		}
	}

	# 根目录文件
	root_files = {
		"README.md": "",
		"requirements.txt": "",
		"__init__.py": "",
		".gitignore": ""
	}

	def create_directory_structure(base_path, structure):
		"""递归创建目录结构"""
		for name, content in structure.items():
			path = os.path.join(base_path, name)

			if isinstance(content, dict):
				# 如果是字典，说明是目录
				print(f"创建目录: {path}")
				os.makedirs(path, exist_ok=True)

				# 递归创建子目录
				if content:  # 如果字典不为空
					create_directory_structure(path, content)
				else:
					# 空目录，创建.gitkeep文件
					gitkeep_path = os.path.join(path, ".gitkeep")
					with open(gitkeep_path, 'w', encoding='utf-8') as f:
						f.write("")
					print(f"创建占位文件: {gitkeep_path}")
			else:
				# 如果不是字典，说明是文件
				print(f"创建文件: {path}")
				with open(path, 'w', encoding='utf-8') as f:
					f.write(content)

	# 创建项目根目录
	if not os.path.exists(project_name):
		os.makedirs(project_name)
		print(f"创建项目根目录: {project_name}")

	# 切换到项目目录
	os.chdir(project_name)

	# 创建目录结构
	create_directory_structure(".", project_structure)

	# 创建根目录文件
	for filename, content in root_files.items():
		print(f"创建根目录文件: {filename}")
		with open(filename, 'w', encoding='utf-8') as f:
			f.write(content)

	# 创建utils目录的__init__.py
	utils_init_path = os.path.join("src", "utils", "__init__.py")
	with open(utils_init_path, 'w', encoding='utf-8') as f:
		f.write("")
	print(f"创建文件: {utils_init_path}")


def create_file_templates():
	"""创建文件模板内容"""

	# requirements.txt 内容
	requirements_content = """# Web爬虫相关
selenium>=4.0.0
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0

# 数据处理相关
pandas>=1.3.0
numpy>=1.21.0

# 文本分析相关
jieba>=0.42.1
textblob>=0.17.1
wordcloud>=1.8.0

# 可视化相关
matplotlib>=3.5.0
seaborn>=0.11.0
plotly>=5.0.0

# 其他工具
tqdm>=4.62.0
python-dotenv>=0.19.0
"""

	# .gitignore 内容
	gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/
cover/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# 项目特定
data/raw/*.csv
data/processed/*.csv
output/figures/*.png
output/figures/*.jpg
output/reports/*.html
logs/
*.log

# 浏览器驱动
chromedriver.exe
geckodriver.exe
"""

	# README.md 内容
	readme_content = """# 百度贴吧数据分析爬虫项目

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
"""

	# 写入文件内容
	with open("requirements.txt", 'w', encoding='utf-8') as f:
		f.write(requirements_content)

	with open(".gitignore", 'w', encoding='utf-8') as f:
		f.write(gitignore_content)

	with open("README.md", 'w', encoding='utf-8') as f:
		f.write(readme_content)

	print("文件模板创建完成！")


def create_python_file_headers():
	"""为Python文件创建文件头注释"""

	python_files = {
		"src/config.py": "# 项目配置文件\n# 包含爬虫配置、数据路径、分析参数等\n\n",
		"src/selenium_scraper.py": "# Selenium爬虫模块\n# 负责爬取百度贴吧数据\n\n",
		"src/data_cleaner.py": "# 数据清理模块\n# 负责清洗和预处理爬取的数据\n\n",
		"src/analyzer.py": "# 数据分析模块\n# 负责文本分析、情感分析、可视化等\n\n",
		"src/main.py": "# 项目主入口文件\n# 统一调度各个模块\n\n",
		"src/__init__.py": "# src包初始化文件\n",
		"src/utils/__init__.py": "# utils工具包初始化文件\n"
	}

	for filepath, header in python_files.items():
		if os.path.exists(filepath):
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write(header)
			print(f"添加文件头: {filepath}")


def print_project_tree():
	"""打印项目目录树"""
	print("\n" + "=" * 50)
	print("项目目录结构:")
	print("=" * 50)

	tree_structure = """
TieBa/
├── data/
│   ├── raw/
│   │   └── .gitkeep
│   ├── processed/
│   │   └── .gitkeep
│   └── dictionaries/
│       └── .gitkeep
├── output/
│   ├── figures/
│   │   └── .gitkeep
│   └── reports/
│       └── .gitkeep
├── src/
│   ├── utils/
│   │   ├── __init__.py
│   │   └── .gitkeep
│   ├── __init__.py
│   ├── config.py
│   ├── selenium_scraper.py
│   ├── data_cleaner.py
│   ├── analyzer.py
│   └── main.py
├── __init__.py
├── README.md
├── requirements.txt
└── .gitignore
"""

	print(tree_structure)


def main():
	"""主函数"""
	print("开始创建百度贴吧爬虫项目架构...")
	print("=" * 50)

	try:
		# 创建项目结构
		create_project_structure()

		# 创建文件模板
		create_file_templates()

		# 添加Python文件头
		create_python_file_headers()

		# 打印项目树
		print_project_tree()

		print("\n✅ 项目架构创建完成！")
		print(f"项目位置: {os.path.abspath('.')}")
		print("\n下一步操作:")
		print("1. 在PyCharm中打开项目目录")
		print("2. 安装依赖: pip install -r requirements.txt")
		print("3. 开始编写具体的爬虫代码")

	except Exception as e:
		print(f"❌ 创建项目时出错: {e}")
		sys.exit(1)


if __name__ == "__main__":
	main()