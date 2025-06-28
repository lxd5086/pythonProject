# -*- coding: utf-8 -*-
"""
天气数据处理模块
"""

import pandas as pd
import json
import re
from datetime import datetime, timedelta
import logging
from config import DATA_FILES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeatherDataProcessor:
	def __init__(self):
		self.processed_data = []

	def load_csv_data(self, filename=None):
		"""加载CSV数据"""
		filename = filename or DATA_FILES['weather_data']
		try:
			df = pd.read_csv(filename, encoding='utf-8')
			logger.info(f"成功加载CSV数据: {len(df)} 条记录")
			return df
		except Exception as e:
			logger.error(f"加载CSV数据失败: {e}")
			return pd.DataFrame()

	def load_json_data(self, filename=None):
		"""加载JSON数据"""
		filename = filename or DATA_FILES['processed_data']
		try:
			with open(filename, 'r', encoding='utf-8') as f:
				data = json.load(f)
			logger.info(f"成功加载JSON数据: {len(data)} 条记录")
			return data
		except Exception as e:
			logger.error(f"加载JSON数据失败: {e}")
			return []

	def clean_temperature(self, temp_input):
		"""
		清理温度数据。
		可以处理数字（int, float）和字符串（'25℃', '-5°'）输入。
		"""
		# --- 修改开始 ---
		# 如果输入已经是数字，直接返回
		if isinstance(temp_input, (int, float)):
			return float(temp_input)

		# 如果输入不是字符串，则无法处理
		if not isinstance(temp_input, str):
			return None
		# --- 修改结束 ---

		# 增强的温度提取正则表达式
		# 匹配格式如: "25℃", "高温 28℃", "-5°C", "28-32℃" 等
		match = re.search(r'(-?\d+\.?\d*)[°℃C]', temp_input) # 允许浮点数
		if match:
			return float(match.group(1))

		# 备用模式：尝试提取任何数字
		numbers = re.findall(r'-?\d+\.?\d*', temp_input) # 允许浮点数
		if numbers:
			return float(numbers[0])

		return None

	def parse_date(self, date_str):
		"""解析日期字符串"""
		if not isinstance(date_str, str):
			return None

		try:
			# 处理各种日期格式
			date_patterns = [
				r'(\d{4})-(\d{1,2})-(\d{1,2})',  # 2024-06-24
				r'(\d{4})/(\d{1,2})/(\d{1,2})',  # 2024/06/24
				r'(\d{1,2})[/-](\d{1,2})',  # 06/24 or 06-24
				r'(\d{1,2})月(\d{1,2})日',  # 6月24日
				r'(\d{1,2})日',  # 24日
				r'今天',
				r'明天',
				r'后天'
			]

			current_date = datetime.now()

			for pattern in date_patterns:
				match = re.search(pattern, date_str)
				if match:
					if pattern == r'(\d{4})-(\d{1,2})-(\d{1,2})':
						year, month, day = match.groups()
						return f"{year}-{int(month):02d}-{int(day):02d}"
					elif pattern == r'(\d{4})/(\d{1,2})/(\d{1,2})':
						year, month, day = match.groups()
						return f"{year}-{int(month):02d}-{int(day):02d}"
					elif pattern == r'(\d{1,2})[/-](\d{1,2})':
						month, day = match.groups()
						return f"{current_date.year}-{int(month):02d}-{int(day):02d}"
					elif pattern == r'(\d{1,2})月(\d{1,be})日':
						month, day = match.groups()
						return f"{current_date.year}-{int(month):02d}-{int(day):02d}"
					elif pattern == r'(\d{1,2})日':
						day = match.group(1)
						return f"{current_date.year}-{current_date.month:02d}-{int(day):02d}"
					elif pattern == '今天':
						return current_date.strftime('%Y-%m-%d')
					elif pattern == '明天':
						return (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
					elif pattern == '后天':
						return (current_date + timedelta(days=2)).strftime('%Y-%m-%d')

			# 尝试直接解析标准日期格式
			try:
				dt = pd.to_datetime(date_str)
				return dt.strftime('%Y-%m-%d')
			except:
				pass

			logger.warning(f"无法解析日期: {date_str}, 将使用当前日期")
			return current_date.strftime('%Y-%m-%d')  # 使用当前日期作为后备方案

		except Exception as e:
			logger.warning(f"日期解析失败: {date_str}, 错误: {e}")
			return datetime.now().strftime('%Y-%m-%d')  # 返回当前日期作为兜底方案

	def extract_weather_info(self, weather_str):
		"""提取天气信息"""
		if not isinstance(weather_str, str):
			return {'condition': '', 'description': ''}

		# 常见天气状况
		weather_conditions = {
			'晴': 'sunny',
			'多云': 'cloudy',
			'阴': 'overcast',
			'小雨': 'light_rain',
			'中雨': 'moderate_rain',
			'大雨': 'heavy_rain',
			'暴雨': 'heavy_rain',
			'雷阵雨': 'thunderstorm',
			'雷': 'thunderstorm',
			'雪': 'snow',
			'小雪': 'light_snow',
			'中雪': 'moderate_snow',
			'大雪': 'heavy_snow',
			'雾': 'fog',
			'霾': 'haze',
			'沙尘': 'dust'
		}

		condition = ''
		for chinese, english in weather_conditions.items():
			if chinese in weather_str:
				condition = english
				break

		return {
			'condition': condition or 'unknown',  # 默认为unknown而不是空字符串
			'description': weather_str or '未知天气'  # 默认为"未知天气"而不是空字符串
		}

	def process_dataframe(self, df):
		"""处理DataFrame数据"""
		if df.empty:
			logger.warning("传入的DataFrame为空，无法处理")
			return df

		processed_df = df.copy()

		try:
			# 确保必要的列存在
			required_columns = ['date', 'temp_high', 'temp_low', 'weather']
			for col in required_columns:
				if col not in processed_df.columns:
					logger.warning(f"缺少必要的列: {col}，将创建空列")
					processed_df[col] = None

			# 处理日期列
			processed_df['parsed_date'] = processed_df['date'].apply(self.parse_date)

			# 调试信息
			logger.info(f"日期解析结果示例: {processed_df['parsed_date'].head(3).tolist()}")

			# 处理温度列
			temp_columns = ['temp_high', 'temp_low', 'temperature']
			for col in temp_columns:
				if col in processed_df.columns:
					processed_df[f'{col}_cleaned'] = processed_df[col].apply(self.clean_temperature)

					# 打印调试信息
					non_null_count = processed_df[f'{col}_cleaned'].notnull().sum()
					logger.info(f"列 {col} 清理后有 {non_null_count} 个非空值")

					# 显示一些样本值
					if non_null_count > 0:
						sample_values = processed_df[[col, f'{col}_cleaned']].dropna().head(3).to_dict('records')
						logger.info(f"{col} 样本值: {sample_values}")

			# 处理天气描述
			if 'weather' in processed_df.columns:
				weather_info = processed_df['weather'].apply(self.extract_weather_info)
				processed_df['weather_condition'] = weather_info.apply(lambda x: x['condition'])
				processed_df['weather_description'] = weather_info.apply(lambda x: x['description'])

			# 添加处理时间
			processed_df['processed_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

			# 确保所有日期格式一致
			if 'parsed_date' in processed_df.columns:
				# 将无效日期替换为当前日期
				mask = processed_df['parsed_date'].isnull()
				if mask.any():
					logger.warning(f"有 {mask.sum()} 个日期无法解析，将使用当前日期")
					processed_df.loc[mask, 'parsed_date'] = datetime.now().strftime('%Y-%m-%d')

			logger.info("数据处理完成")

		except Exception as e:
			logger.error(f"数据处理失败: {e}")
			import traceback
			logger.error(traceback.format_exc())

		return processed_df

	def aggregate_data(self, df):
		"""聚合数据分析"""
		if df.empty:
			return {}

		stats = {}

		try:
			# 基本统计信息
			stats['total_records'] = len(df)
			stats['data_sources'] = df['source'].value_counts().to_dict() if 'source' in df.columns else {}

			# 温度统计
			temp_cols = [col for col in df.columns if 'temp' in col and 'cleaned' in col]
			for col in temp_cols:
				if col in df.columns:
					temp_data = df[col].dropna()
					if not temp_data.empty:
						stats[f'{col}_stats'] = {
							'mean': round(temp_data.mean(), 2),
							'min': int(temp_data.min()),
							'max': int(temp_data.max()),
							'std': round(temp_data.std(), 2)
						}
					else:
						logger.warning(f"{col} 列没有有效的温度数据")

			# 天气状况统计
			if 'weather_condition' in df.columns:
				weather_counts = df['weather_condition'].value_counts()
				stats['weather_conditions'] = weather_counts.to_dict()

			# 日期范围
			if 'parsed_date' in df.columns:
				valid_dates = df['parsed_date'].dropna()
				if not valid_dates.empty:
					stats['date_range'] = {
						'start': valid_dates.min(),
						'end': valid_dates.max()
					}

			logger.info("数据聚合完成")

		except Exception as e:
			logger.error(f"数据聚合失败: {e}")
			import traceback
			logger.error(traceback.format_exc())

		return stats

	def generate_forecast_summary(self, df):
		"""生成天气预报摘要"""
		if df.empty:
			return "暂无天气数据"

		try:
			summary_parts = []

			# 按日期排序
			if 'parsed_date' in df.columns:
				# 确保parsed_date列都有值
				df = df.dropna(subset=['parsed_date'])

				if df.empty:
					return "天气数据中缺少有效日期信息"

				df_sorted = df.sort_values('parsed_date')

				# 获取未来几天的预报
				for _, row in df_sorted.head(7).iterrows():
					date = row.get('parsed_date', '未知日期')
					weather = row.get('weather_description', row.get('weather', ''))
					temp_high = row.get('temp_high_cleaned')
					temp_low = row.get('temp_low_cleaned')

					temp_info = ""
					if pd.notnull(temp_high) and pd.notnull(temp_low):
						temp_info = f" {int(temp_high)}°C/{int(temp_low)}°C"
					elif pd.notnull(temp_high):
						temp_info = f" 高温{int(temp_high)}°C"
					elif pd.notnull(temp_low):
						temp_info = f" 低温{int(temp_low)}°C"

					if weather:
						summary_parts.append(f"{date}: {weather}{temp_info}")

				if summary_parts:
					return "浦东新区天气预报:\n" + "\n".join(summary_parts)

			return "天气数据处理中，请稍后查看"

		except Exception as e:
			logger.error(f"生成预报摘要失败: {e}")
			import traceback
			logger.error(traceback.format_exc())
			return "天气预报摘要生成失败"

	def save_processed_data(self, df, stats, filename=None):
		"""保存处理后的数据"""
		filename = filename or DATA_FILES['processed_data']

		try:
			# 检查温度数据是否有效
			temp_columns = ['temp_high_cleaned', 'temp_low_cleaned']
			temp_data_exists = False

			for col in temp_columns:
				if col in df.columns and df[col].notnull().any():
					temp_data_exists = True
					logger.info(f"列 {col} 有有效数据: {df[col].notnull().sum()} 条")
				elif col in df.columns:
					logger.warning(f"列 {col} 所有值均为空")

			if not temp_data_exists:
				logger.warning("没有有效的温度数据，可视化将无法显示温度趋势")

			# 确保日期数据有效
			if 'parsed_date' in df.columns:
				date_count = df['parsed_date'].notnull().sum()
				logger.info(f"有效日期数据: {date_count} 条")
				if date_count == 0:
					logger.warning("没有有效的日期数据，可视化将无法显示时间轴")

			output_data = {
				'processed_data': df.to_dict('records') if not df.empty else [],
				'statistics': stats,
				'processed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
				'summary': self.generate_forecast_summary(df)
			}

			with open(filename, 'w', encoding='utf-8') as f:
				json.dump(output_data, f, ensure_ascii=False, indent=2, default=lambda x: int(x) if isinstance(x, float) and x.is_integer() else x)

			logger.info(f"处理后的数据已保存: {filename}")
			return output_data

		except Exception as e:
			logger.error(f"保存处理数据失败: {e}")
			import traceback
			logger.error(traceback.format_exc())
			return None


def main():
	"""主函数"""
	processor = WeatherDataProcessor()

	print("开始处理天气数据...")

	# 加载原始数据
	df = processor.load_csv_data()

	if not df.empty:
		print(f"加载了 {len(df)} 条原始数据")

		# 显示原始数据的列和前几行，帮助调试
		print("\n原始数据列名:", df.columns.tolist())
		print("\n原始数据预览:")
		print(df.head(3))

		# 处理数据
		processed_df = processor.process_dataframe(df)

		# 显示处理后的温度数据统计
		temp_columns = ['temp_high_cleaned', 'temp_low_cleaned']
		for col in temp_columns:
			if col in processed_df.columns:
				valid_count = processed_df[col].notnull().sum()
				total_count = len(processed_df)
				print(f"\n{col} 有效数据: {valid_count}/{total_count} ({valid_count / total_count * 100:.1f}%)")
				if valid_count > 0:
					print(f"示例值: {processed_df[col].dropna().head(3).tolist()}")

		# 生成统计信息
		stats = processor.aggregate_data(processed_df)

		# 保存处理后的数据
		result = processor.save_processed_data(processed_df, stats)

		if result:
			print("\n数据处理完成!")
			print(f"处理后数据条数: {len(result['processed_data'])}")
			print(f"数据来源统计: {stats.get('data_sources', {})}")
			print(f"\n天气预报摘要:\n{result['summary']}")
		else:
			print("数据处理失败")
	else:
		print("没有找到可处理的数据，请先运行爬虫获取数据")


if __name__ == "__main__":
	main()