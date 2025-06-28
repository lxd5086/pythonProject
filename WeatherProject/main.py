# -*- coding: utf-8 -*-
"""
浦东新区天气预报爬取项目 - 主程序
"""

import os
import sys
import time
import argparse
from datetime import datetime

# 导入自定义模块
from web_scraper import WeatherScraper
from data_processor import WeatherDataProcessor
from visualizer import WeatherVisualizer
from config import DATA_FILES, LOG_CONFIG

import logging

# 配置日志
logging.basicConfig(
	level=getattr(logging, LOG_CONFIG['level']),
	format=LOG_CONFIG['format'],
	handlers=[
		logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
		logging.StreamHandler(sys.stdout)
	]
)

logger = logging.getLogger(__name__)


class WeatherProjectManager:
	"""天气项目管理器"""

	def __init__(self):
		self.scraper = WeatherScraper()
		self.processor = WeatherDataProcessor()
		self.visualizer = WeatherVisualizer()

	def run_scraping(self):
		"""执行数据爬取"""
		print("🌤️  开始爬取浦东新区天气数据...")
		logger.info("开始数据爬取流程")

		try:
			# 爬取数据
			weather_data = self.scraper.scrape_all_sources()

			if weather_data:
				print(f"✓ 爬取完成，共获取 {len(weather_data)} 条数据")

				# 保存原始数据
				self.scraper.save_to_csv(weather_data)
				self.scraper.save_to_json(weather_data)

				logger.info(f"数据爬取成功，获取 {len(weather_data)} 条记录")
				return True
			else:
				print("✗ 未获取到任何数据")
				logger.warning("数据爬取失败，未获取到数据")
				return False

		except Exception as e:
			print(f"✗ 数据爬取过程出错: {e}")
			logger.error(f"数据爬取异常: {e}")
			return False

	def run_processing(self):
		"""执行数据处理"""
		print("📊 开始处理天气数据...")
		logger.info("开始数据处理流程")

		try:
			# 检查原始数据是否存在
			if not os.path.exists(DATA_FILES['weather_data']):
				print("✗ 未找到原始数据文件，请先执行数据爬取")
				return False

			# 加载并处理数据
			df = self.processor.load_csv_data()

			if df.empty:
				print("✗ 原始数据为空")
				return False

			print(f"✓ 加载了 {len(df)} 条原始数据")

			# 数据清洗和处理
			processed_df = self.processor.process_dataframe(df)

			# 生成统计信息
			stats = self.processor.aggregate_data(processed_df)

			# 保存处理后的数据
			result = self.processor.save_processed_data(processed_df, stats)

			if result:
				print("✓ 数据处理完成")
				print(f"  - 处理后数据: {len(result['processed_data'])} 条")
				print(f"  - 数据来源: {list(stats.get('data_sources', {}).keys())}")

				# 显示天气摘要
				if 'summary' in result:
					print(f"\n📋 天气预报摘要:")
					print(result['summary'])

				logger.info("数据处理成功完成")
				return True
			else:
				print("✗ 数据处理失败")
				return False

		except Exception as e:
			print(f"✗ 数据处理过程出错: {e}")
			logger.error(f"数据处理异常: {e}")
			return False

	def run_visualization(self):
		"""执行数据可视化"""
		print("📈 开始生成数据可视化图表...")
		logger.info("开始数据可视化流程")

		try:
			# 检查处理后的数据是否存在
			if not os.path.exists(DATA_FILES['processed_data']):
				print("✗ 未找到处理后的数据文件，请先执行数据处理")
				return False

			# 生成图表
			charts_generated = self.visualizer.generate_all_charts()

			if charts_generated:
				print(f"✓ 可视化完成，生成了 {len(charts_generated)} 个图表:")
				for chart in charts_generated:
					print(f"  - {chart}")
				print(f"\n📁 图表保存位置: {DATA_FILES['charts']}")

				logger.info(f"数据可视化成功，生成 {len(charts_generated)} 个图表")
				return True
			else:
				print("✗ 未生成任何图表")
				return False

		except Exception as e:
			print(f"✗ 数据可视化过程出错: {e}")
			logger.error(f"数据可视化异常: {e}")
			return False

	def run_full_pipeline(self):
		"""执行完整流程"""
		print("🚀 开始执行完整的天气数据分析流程...")
		print("=" * 60)

		start_time = time.time()
		logger.info("开始完整数据处理流程")

		# 步骤1: 数据爬取
		print("\n【步骤 1/3】数据爬取")
		scraping_success = self.run_scraping()

		if not scraping_success:
			print("❌ 流程终止：数据爬取失败")
			return False

		print("\n" + "-" * 40)

		# 步骤2: 数据处理
		print("\n【步骤 2/3】数据处理")
		processing_success = self.run_processing()

		if not processing_success:
			print("❌ 流程终止：数据处理失败")
			return False

		print("\n" + "-" * 40)

		# 步骤3: 数据可视化
		print("\n【步骤 3/3】数据可视化")
		visualization_success = self.run_visualization()

		# 完成总结
		end_time = time.time()
		duration = end_time - start_time

		print("\n" + "=" * 60)

		if scraping_success and processing_success and visualization_success:
			print("🎉 完整流程执行成功！")
			print(f"⏱️  总耗时: {duration:.2f} 秒")
			print(f"📊 数据文件: {DATA_FILES['weather_data']}")
			print(f"📈 图表目录: {DATA_FILES['charts']}")
			logger.info(f"完整流程执行成功，耗时 {duration:.2f} 秒")

			# 显示项目文件结构
			self.show_project_structure()

			return True
		else:
			print("❌ 流程终止")
			logger.error("完整流程执行失败")
			return False

	def show_project_structure(self):
		"""显示项目文件结构"""
		print(f"\n📁 项目文件结构:")
		print("WeatherProject/")
		print("├── config.py          # 配置文件")
		print("├── web_scraper.py     # 数据爬取模块")
		print("├── data_processor.py  # 数据处理模块")
		print("├── visualizer.py      # 数据可视化模块")
		print("├── main.py           # 主程序入口")
		print("├── utils.py          # 工具函数")
		print("├── data/             # 数据目录")

		# 检查数据文件
		data_files = [
			("weather_data.csv", "原始天气数据"),
			("processed_weather.json", "处理后数据"),
		]

		for filename, description in data_files:
			filepath = os.path.join("data", filename)
			if os.path.exists(filepath):
				size = os.path.getsize(filepath)
				print(f"│   ├── {filename:<20} # {description} ({size} bytes)")
			else:
				print(f"│   ├── {filename:<20} # {description} (不存在)")

		print("│   └── charts/        # 图表目录")

		# 检查图表文件
		charts_dir = DATA_FILES['charts']
		if os.path.exists(charts_dir):
			chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
			for chart_file in chart_files:
				print(f"│       ├── {chart_file}")

		print("└── logs/             # 日志目录")

	def show_status(self):
		"""显示项目状态"""
		print("📊 项目状态检查")
		print("-" * 30)

		# 检查数据文件
		files_to_check = [
			(DATA_FILES['weather_data'], "原始数据"),
			(DATA_FILES['processed_data'], "处理后数据"),
		]

		for filepath, description in files_to_check:
			if os.path.exists(filepath):
				size = os.path.getsize(filepath)
				mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
				print(f"✓ {description}: {size} bytes, 更新于 {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
			else:
				print(f"✗ {description}: 文件不存在")

		# 检查图表文件
		charts_dir = DATA_FILES['charts']
		if os.path.exists(charts_dir):
			chart_files = [f for f in os.listdir(charts_dir) if f.endswith('.png')]
			print(f"✓ 可视化图表: {len(chart_files)} 个文件")
		else:
			print("✗ 可视化图表: 目录不存在")


def create_argument_parser():
	"""创建命令行参数解析器"""
	parser = argparse.ArgumentParser(
		description='浦东新区天气预报数据采集与分析项目',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
使用示例:
  python main.py --full              # 执行完整流程
  python main.py --scrape           # 仅执行数据爬取
  python main.py --process          # 仅执行数据处理
  python main.py --visualize        # 仅执行数据可视化
  python main.py --status           # 查看项目状态
        """
	)

	parser.add_argument('--full', action='store_true',
						help='执行完整流程（爬取→处理→可视化）')
	parser.add_argument('--scrape', action='store_true',
						help='仅执行数据爬取')
	parser.add_argument('--process', action='store_true',
						help='仅执行数据处理')
	parser.add_argument('--visualize', action='store_true',
						help='仅执行数据可视化')
	parser.add_argument('--status', action='store_true',
						help='查看项目状态')

	return parser


def main():
	"""主函数"""
	# 显示项目信息
	print("🌤️  浦东新区天气预报数据采集与分析项目")
	print("=" * 50)
	print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	print()

	# 解析命令行参数
	parser = create_argument_parser()
	args = parser.parse_args()

	# 创建项目管理器实例
	manager = WeatherProjectManager()

	# 根据参数选择执行模式
	if args.full:
		manager.run_full_pipeline()
	elif args.scrape:
		manager.run_scraping()
	elif args.process:
		manager.run_processing()
	elif args.visualize:
		manager.run_visualization()
	elif args.status:
		manager.show_status()
	else:
		print("❗ 请使用 --full, --scrape, --process, --visualize 或 --status 指定操作模式")
		parser.print_help()

	# 记录结束时间
	end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(f"\n结束时间: {end_time}")
	logger.info(f"程序结束，结束时间: {end_time}")


if __name__ == "__main__":
	main()