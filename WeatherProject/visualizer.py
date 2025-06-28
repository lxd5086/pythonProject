# -*- coding: utf-8 -*-
"""
天气数据可视化模块
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import json
import numpy as np
from datetime import datetime
import os
import logging
from config import DATA_FILES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherVisualizer:
	def __init__(self):
		self.colors = {
			'primary': '#2E86AB',
			'secondary': '#A23B72',
			'success': '#F18F01',
			'info': '#C73E1D',
			'light': '#F5F5F5',
			'dark': '#2D3748'
		}

		# --- 关键改动：确保字体设置在样式设置之后 ---
		# 1. 首先，应用样式
		plt.style.use('seaborn-v0_8')
		sns.set_palette("husl")

		# 2. 然后，再设置中文字体，这样它就不会被覆盖
		plt.rcParams['font.sans-serif'] = ['SimHei']  # 'SimHei' 是黑体
		plt.rcParams['axes.unicode_minus'] = False  # 解决负号 '-' 显示为方块的问题

	def load_processed_data(self, filename=None):
		"""加载处理后的数据"""
		filename = filename or DATA_FILES['processed_data']
		try:
			with open(filename, 'r', encoding='utf-8') as f:
				data = json.load(f)

			df = pd.DataFrame(data.get('processed_data', []))
			stats = data.get('statistics', {})

			logger.info(f"成功加载可视化数据: {len(df)} 条记录")
			return df, stats

		except Exception as e:
			logger.error(f"加载数据失败: {e}")
			return pd.DataFrame(), {}

	def plot_temperature_trend(self, df, save_path=None):
		"""绘制温度趋势图"""
		if df.empty:
			logger.warning("没有数据可绘制温度趋势")
			return None

		try:
			fig, ax = plt.subplots(figsize=(12, 6))

			# 准备数据
			df_plot = df.copy()
			if 'parsed_date' in df_plot.columns:
				df_plot['parsed_date'] = pd.to_datetime(df_plot['parsed_date'], errors='coerce')
				df_plot = df_plot.sort_values('parsed_date').dropna(subset=['parsed_date'])

			# 绘制高温和低温线
			if 'temp_high_cleaned' in df_plot.columns:
				high_temps = df_plot.dropna(subset=['temp_high_cleaned'])
				if not high_temps.empty:
					ax.plot(high_temps['parsed_date'], high_temps['temp_high_cleaned'],
							marker='o', linewidth=2, label='最高温度', color=self.colors['info'])

			if 'temp_low_cleaned' in df_plot.columns:
				low_temps = df_plot.dropna(subset=['temp_low_cleaned'])
				if not low_temps.empty:
					ax.plot(low_temps['parsed_date'], low_temps['temp_low_cleaned'],
							marker='s', linewidth=2, label='最低温度', color=self.colors['primary'])

			# 填充区域
			if 'temp_high_cleaned' in df_plot.columns and 'temp_low_cleaned' in df_plot.columns:
				temp_data = df_plot.dropna(subset=['temp_high_cleaned', 'temp_low_cleaned'])
				if not temp_data.empty:
					ax.fill_between(temp_data['parsed_date'],
									temp_data['temp_low_cleaned'],
									temp_data['temp_high_cleaned'],
									alpha=0.3, color=self.colors['secondary'])

			# 设置图表样式
			ax.set_title('浦东新区温度变化趋势', fontsize=16, fontweight='bold', pad=20)
			ax.set_xlabel('日期', fontsize=12)
			ax.set_ylabel('温度 (°C)', fontsize=12)
			ax.legend(loc='upper right')
			ax.grid(True, alpha=0.3)

			# 旋转日期标签
			plt.xticks(rotation=45)
			plt.tight_layout()

			# 保存图片
			if save_path is None:
				save_path = os.path.join(DATA_FILES['charts'], 'temperature_trend.png')

			plt.savefig(save_path, dpi=300, bbox_inches='tight')
			logger.info(f"温度趋势图已保存: {save_path}")

			return fig

		except Exception as e:
			logger.error(f"绘制温度趋势图失败: {e}")
			return None

	def plot_weather_distribution(self, df, save_path=None):
		"""绘制天气状况分布饼图"""
		if df.empty:
			logger.warning("没有数据可绘制天气分布")
			return None

		try:
			fig, ax = plt.subplots(figsize=(10, 8))

			# 统计天气状况
			weather_col = 'weather_description' if 'weather_description' in df.columns else 'weather'

			if weather_col in df.columns:
				weather_counts = df[weather_col].value_counts()

				if not weather_counts.empty:
					# 设置颜色
					colors = plt.cm.Set3(np.linspace(0, 1, len(weather_counts)))

					# 绘制饼图
					wedges, texts, autotexts = ax.pie(weather_counts.values,
													  labels=weather_counts.index,
													  colors=colors,
													  autopct='%1.1f%%',
													  startangle=90,
													  explode=[0.05] * len(weather_counts))

					# 美化文本
					for autotext in autotexts:
						autotext.set_color('white')
						autotext.set_fontweight('bold')

					ax.set_title('浦东新区天气状况分布', fontsize=16, fontweight='bold', pad=20)

					# 保存图片
					if save_path is None:
						save_path = os.path.join(DATA_FILES['charts'], 'weather_distribution.png')

					plt.savefig(save_path, dpi=300, bbox_inches='tight')
					logger.info(f"天气分布图已保存: {save_path}")

					return fig

			logger.warning("没有有效的天气数据用于绘制分布图")
			return None

		except Exception as e:
			logger.error(f"绘制天气分布图失败: {e}")
			return None

	def plot_data_sources(self, stats, save_path=None):
		"""绘制数据来源统计图"""
		try:
			data_sources = stats.get('data_sources', {})
			if not data_sources:
				logger.warning("没有数据来源信息")
				return None

			fig, ax = plt.subplots(figsize=(10, 6))

			sources = list(data_sources.keys())
			counts = list(data_sources.values())

			# 绘制柱状图
			bars = ax.bar(sources, counts,
						  color=[self.colors['primary'], self.colors['secondary'], self.colors['success']])

			# 添加数值标签
			for bar in bars:
				height = bar.get_height()
				ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
						f'{int(height)}', ha='center', va='bottom', fontweight='bold')

			ax.set_title('数据来源统计', fontsize=16, fontweight='bold', pad=20)
			ax.set_xlabel('数据源', fontsize=12)
			ax.set_ylabel('记录数量', fontsize=12)
			ax.grid(True, alpha=0.3, axis='y')

			plt.tight_layout()

			# 保存图片
			if save_path is None:
				save_path = os.path.join(DATA_FILES['charts'], 'data_sources.png')

			plt.savefig(save_path, dpi=300, bbox_inches='tight')
			logger.info(f"数据来源统计图已保存: {save_path}")

			return fig

		except Exception as e:
			logger.error(f"绘制数据来源图失败: {e}")
			return None

	def plot_temperature_statistics(self, stats, save_path=None):
		"""绘制温度统计图"""
		try:
			temp_stats = {}
			for key, value in stats.items():
				if 'temp' in key and 'stats' in key:
					temp_stats[key.replace('_cleaned_stats', '')] = value

			if not temp_stats:
				logger.warning("没有温度统计数据")
				return None

			fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

			# 平均温度对比
			temp_types = list(temp_stats.keys())
			mean_temps = [stats['mean'] for stats in temp_stats.values()]

			bars1 = ax1.bar(temp_types, mean_temps, color=[self.colors['info'], self.colors['primary']])
			ax1.set_title('平均温度对比', fontsize=14, fontweight='bold')
			ax1.set_ylabel('温度 (°C)', fontsize=12)

			# 添加数值标签
			for bar in bars1:
				height = bar.get_height()
				ax1.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
						 f'{height:.1f}°C', ha='center', va='bottom', fontweight='bold')

			# 温度范围对比
			temp_ranges = []
			labels = []
			for temp_type, stats in temp_stats.items():
				temp_ranges.append([stats['min'], stats['max']])
				labels.append(temp_type)

			if temp_ranges:
				x_pos = np.arange(len(labels))
				for i, (min_temp, max_temp) in enumerate(temp_ranges):
					ax2.bar(x_pos[i], max_temp - min_temp, bottom=min_temp,
							color=self.colors['secondary'], alpha=0.7, width=0.6)
					ax2.text(x_pos[i], (min_temp + max_temp) / 2,
							 f'{min_temp}°C\n~\n{max_temp}°C',
							 ha='center', va='center', fontweight='bold')

				ax2.set_xticks(x_pos)
				ax2.set_xticklabels(labels)
				ax2.set_title('温度范围', fontsize=14, fontweight='bold')
				ax2.set_ylabel('温度 (°C)', fontsize=12)

			plt.tight_layout()

			# 保存图片
			if save_path is None:
				save_path = os.path.join(DATA_FILES['charts'], 'temperature_statistics.png')

			plt.savefig(save_path, dpi=300, bbox_inches='tight')
			logger.info(f"温度统计图已保存: {save_path}")

			return fig

		except Exception as e:
			logger.error(f"绘制温度统计图失败: {e}")
			return None

	def create_dashboard(self, df, stats):
		"""创建综合仪表盘"""
		try:
			fig = plt.figure(figsize=(20, 12))

			# 创建子图布局
			gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

			# 1. 温度趋势 (占两列)
			ax1 = fig.add_subplot(gs[0, :2])
			self._plot_temp_trend_subplot(df, ax1)

			# 2. 天气分布饼图
			ax2 = fig.add_subplot(gs[0, 2])
			self._plot_weather_pie_subplot(df, ax2)

			# 3. 数据来源统计
			ax3 = fig.add_subplot(gs[1, 0])
			self._plot_sources_subplot(stats, ax3)

			# 4. 温度统计
			ax4 = fig.add_subplot(gs[1, 1:])
			self._plot_temp_stats_subplot(stats, ax4)

			# 5. 文本信息
			ax5 = fig.add_subplot(gs[2, :])
			self._add_text_info(stats, ax5)

			# 设置整体标题
			fig.suptitle('浦东新区天气数据分析仪表盘', fontsize=20, fontweight='bold', y=0.98)

			# 保存图片
			save_path = os.path.join(DATA_FILES['charts'], 'weather_dashboard.png')
			plt.savefig(save_path, dpi=300, bbox_inches='tight')
			logger.info(f"综合仪表盘已保存: {save_path}")

			return fig

		except Exception as e:
			logger.error(f"创建仪表盘失败: {e}")
			return None

	def _plot_temp_trend_subplot(self, df, ax):
		"""绘制温度趋势子图"""
		if 'parsed_date' in df.columns and 'temp_high_cleaned' in df.columns:
			df_plot = df.dropna(subset=['parsed_date', 'temp_high_cleaned'])
			df_plot['parsed_date'] = pd.to_datetime(df_plot['parsed_date'])
			df_plot = df_plot.sort_values('parsed_date')

			ax.plot(df_plot['parsed_date'], df_plot['temp_high_cleaned'],
					marker='o', label='最高温度', color=self.colors['info'])

			if 'temp_low_cleaned' in df.columns:
				df_low = df_plot.dropna(subset=['temp_low_cleaned'])
				ax.plot(df_low['parsed_date'], df_low['temp_low_cleaned'],
						marker='s', label='最低温度', color=self.colors['primary'])

		ax.set_title('温度趋势', fontweight='bold')
		ax.legend()
		ax.grid(True, alpha=0.3)

	def _plot_weather_pie_subplot(self, df, ax):
		"""绘制天气分布子图"""
		weather_col = 'weather_description' if 'weather_description' in df.columns else 'weather'
		if weather_col in df.columns:
			weather_counts = df[weather_col].value_counts().head(5)  # 只显示前5个
			if not weather_counts.empty:
				ax.pie(weather_counts.values, labels=weather_counts.index, autopct='%1.1f%%')
				ax.set_title('天气分布', fontweight='bold')

	def _plot_sources_subplot(self, stats, ax):
		"""绘制数据来源子图"""
		data_sources = stats.get('data_sources', {})
		if data_sources:
			sources = list(data_sources.keys())
			counts = list(data_sources.values())
			ax.bar(sources, counts, color=self.colors['success'])
			ax.set_title('数据来源', fontweight='bold')
			ax.tick_params(axis='x', rotation=45)

	def _plot_temp_stats_subplot(self, stats, ax):
		"""绘制温度统计子图"""
		temp_data = []
		labels = []

		for key, value in stats.items():
			if 'temp' in key and 'stats' in key:
				temp_data.append([value.get('min', 0), value.get('mean', 0), value.get('max', 0)])
				labels.append(key.replace('_cleaned_stats', ''))

		if temp_data:
			x = np.arange(len(labels))
			width = 0.25

			mins = [data[0] for data in temp_data]
			means = [data[1] for data in temp_data]
			maxs = [data[2] for data in temp_data]

			ax.bar(x - width, mins, width, label='最低', color=self.colors['primary'])
			ax.bar(x, means, width, label='平均', color=self.colors['secondary'])
			ax.bar(x + width, maxs, width, label='最高', color=self.colors['info'])

			ax.set_xlabel('温度类型')
			ax.set_ylabel('温度 (°C)')
			ax.set_title('温度统计', fontweight='bold')
			ax.set_xticks(x)
			ax.set_xticklabels(labels)
			ax.legend()

	def _add_text_info(self, stats, ax):
		"""添加文本信息"""
		ax.axis('off')

		info_text = f"""
数据统计信息:
• 总记录数: {stats.get('total_records', 0)}
• 数据来源: {len(stats.get('data_sources', {}))} 个
• 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

		ax.text(0.1, 0.5, info_text, fontsize=12, verticalalignment='center',
				bbox=dict(boxstyle="round,pad=0.3", facecolor=self.colors['light']))

	def generate_all_charts(self):
		"""生成所有图表"""
		print("开始生成天气数据可视化图表...")

		# 加载数据
		df, stats = self.load_processed_data()

		if df.empty:
			print("没有找到可视化数据，请先运行数据处理")
			return

		charts_generated = []

		# 生成各种图表
		charts = [
			('温度趋势图', self.plot_temperature_trend),
			('天气分布图', self.plot_weather_distribution),
			('数据来源统计', self.plot_data_sources),
			('温度统计图', self.plot_temperature_statistics),
			('综合仪表盘', self.create_dashboard)
		]

		for chart_name, chart_func in charts:
			try:
				if chart_name == '综合仪表盘':
					result = chart_func(df, stats)
				elif chart_name in ['数据来源统计', '温度统计图']:
					result = chart_func(stats)
				else:
					result = chart_func(df)

				if result:
					charts_generated.append(chart_name)
					print(f"✓ {chart_name} 生成成功")
				else:
					print(f"✗ {chart_name} 生成失败")

			except Exception as e:
				print(f"✗ {chart_name} 生成失败: {e}")

		plt.close('all')  # 关闭所有图表，释放内存

		print(f"\n图表生成完成! 共生成 {len(charts_generated)} 个图表")
		print(f"图表保存位置: {DATA_FILES['charts']}")

		return charts_generated


def main():
	"""主函数"""
	visualizer = WeatherVisualizer()
	visualizer.generate_all_charts()


if __name__ == "__main__":
	main()