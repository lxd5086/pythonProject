# data_extractor.py - 数据提取器

import re
import json
from datetime import datetime

# 导入本地模块
try:
	from utils import Utils
	from config import Config
except ImportError:
	print("请确保 utils.py 和 config.py 文件在同一目录下")
	exit(1)


class DataExtractor:
	"""数据提取器"""

	def __init__(self):
		self.utils = Utils()
		self.config = Config()

	def extract_all_data(self, soup):
		"""提取所有类型的数据"""
		self.utils.print_section("数据提取")
		weather_data = []

		# 1. 提取脚本数据
		self.utils.print_step(1, "提取JavaScript数据")
		script_data = self._extract_script_data(soup)
		weather_data.extend(script_data)
		print(f"   从脚本提取到 {len(script_data)} 条数据")

		# 2. 提取当前天气
		self.utils.print_step(2, "提取当前天气")
		current_data = self._extract_current_weather(soup)
		if current_data:
			weather_data.append(current_data)
			print("   成功提取当前天气数据")
		else:
			print("   未找到当前天气数据")

		# 3. 提取预报数据
		self.utils.print_step(3, "提取天气预报")
		forecast_data = self._extract_forecast_data(soup)
		weather_data.extend(forecast_data)
		print(f"   提取到 {len(forecast_data)} 条预报数据")

		# 4. 提取通用数据（备用方案）
		self.utils.print_step(4, "提取通用天气信息")
		generic_data = self._extract_generic_weather(soup)
		weather_data.extend(generic_data)
		print(f"   提取到 {len(generic_data)} 条通用数据")

		return weather_data

	def _extract_script_data(self, soup):
		"""提取脚本中的数据"""
		weather_data = []
		scripts = soup.find_all('script')

		script_count = 0
		for script in scripts:
			if not script.string:
				continue

			script_count += 1

			# 提取小时数据
			hour_data = self._extract_hour_data(script.string)
			if hour_data:
				weather_data.extend(hour_data)
				print(f"     脚本{script_count}: 找到小时数据 {len(hour_data)} 条")

			# 提取观测数据
			observe_data = self._extract_observe_data(script.string)
			if observe_data:
				weather_data.extend(observe_data)
				print(f"     脚本{script_count}: 找到观测数据 {len(observe_data)} 条")

			# 提取其他可能的数据格式
			other_data = self._extract_other_script_data(script.string)
			if other_data:
				weather_data.extend(other_data)
				print(f"     脚本{script_count}: 找到其他数据 {len(other_data)} 条")

		print(f"   总共检查了 {script_count} 个脚本标签")
		return weather_data

	def _extract_hour_data(self, script_content):
		"""提取小时级数据"""
		try:
			# 多种可能的变量名
			patterns = [
				r'var hour3data=(\[.*?\]);',
				r'hour3data\s*=\s*(\[.*?\]);',
				r'hourData\s*=\s*(\[.*?\]);',
			]

			for pattern in patterns:
				match = re.search(pattern, script_content, re.DOTALL)
				if match:
					data = self.utils.safe_json_loads(match.group(1))
					if data:
						return self._parse_hour_data(data)

		except Exception as e:
			print(f"   小时数据提取错误: {e}")

		return []

	def _parse_hour_data(self, data):
		"""解析小时数据"""
		weather_list = []
		for item in data:
			if isinstance(item, dict):
				weather_info = {
					'time': item.get('jf', item.get('time', '')),
					'temperature': item.get('jb', item.get('temp', '')),
					'weather': item.get('ja', item.get('weather', '')),
					'wind_direction': item.get('jd', item.get('wind_dir', '')),
					'wind_speed': item.get('jc', item.get('wind_speed', '')),
					'data_type': 'hourly'
				}
				weather_list.append(weather_info)
		return weather_list

	def _extract_observe_data(self, script_content):
		"""提取24小时观测数据"""
		try:
			patterns = [
				r'var observe24h_data=(\{.*?\});',
				r'observe24h_data\s*=\s*(\{.*?\});',
				r'observeData\s*=\s*(\{.*?\});',
			]

			for pattern in patterns:
				match = re.search(pattern, script_content, re.DOTALL)
				if match:
					data = self.utils.safe_json_loads(match.group(1))
					if data:
						return self._parse_observe_data(data)

		except Exception as e:
			print(f"   观测数据提取错误: {e}")

		return []

	def _parse_observe_data(self, data):
		"""解析观测数据"""
		weather_list = []
		for key, value in data.items():
			if isinstance(value, dict):
				weather_info = {
					'time': key,
					'temperature': value.get('temp', ''),
					'humidity': value.get('humidity', ''),
					'pressure': value.get('pressure', ''),
					'weather': value.get('weather', ''),
					'data_type': 'observe'
				}
				weather_list.append(weather_info)
		return weather_list

	def _extract_other_script_data(self, script_content):
		"""提取其他脚本数据"""
		weather_data = []

		# 查找任何包含温度、天气信息的JSON数据
		json_patterns = [
			r'(\{[^{}]*(?:"temp"|"temperature")[^{}]*\})',
			r'(\[[^\[\]]*(?:"temp"|"temperature")[^\[\]]*\])',
			r'(\{[^{}]*(?:"weather"|"wea")[^{}]*\})',
		]

		for pattern in json_patterns:
			matches = re.findall(pattern, script_content)
			for match in matches:
				try:
					data = self.utils.safe_json_loads(match)
					if data:
						weather_info = {
							'raw_data': data,
							'data_type': 'script_other',
							'extract_time': self.utils.get_current_timestamp()
						}
						weather_data.append(weather_info)
				except:
					continue

		return weather_data

	def _extract_current_weather(self, soup):
		"""提取当前天气信息"""
		try:
			current_info = {}

			# 多种可能的温度元素
			temp_selectors = [
				'span.temp', 'em', '.temperature', '.temp-value',
				'span[class*="temp"]', 'div[class*="temp"]'
			]

			for selector in temp_selectors:
				temp_elem = soup.select_one(selector)
				if temp_elem:
					current_info['temperature'] = temp_elem.get_text().strip()
					break

			# 多种可能的天气状况元素
			weather_selectors = [
				'p.wea', '.weather', '.weather-desc',
				'span[class*="wea"]', 'p[class*="weather"]'
			]

			for selector in weather_selectors:
				weather_elem = soup.select_one(selector)
				if weather_elem:
					current_info['weather'] = weather_elem.get_text().strip()
					break

			# 查找其他信息
			info_divs = soup.find_all('div', class_='con')
			for div in info_divs:
				text = div.get_text()
				if '湿度' in text:
					current_info['humidity'] = text
				elif '气压' in text:
					current_info['pressure'] = text
				elif '能见度' in text:
					current_info['visibility'] = text

			if current_info:
				current_info['time'] = self.utils.get_current_timestamp()
				current_info['data_type'] = 'current'
				return current_info

		except Exception as e:
			print(f"   当前天气提取错误: {e}")

		return None

	def _extract_forecast_data(self, soup):
		"""提取天气预报数据"""
		forecast_list = []

		try:
			# 多种可能的预报元素选择器
			forecast_selectors = [
				'li.sky.skyid', '.forecast-item', '.weather-item',
				'li[class*="sky"]', 'div[class*="forecast"]'
			]

			forecast_items = []
			for selector in forecast_selectors:
				items = soup.select(selector)
				if items:
					forecast_items = items
					print(f"   使用选择器: {selector}, 找到 {len(items)} 个预报项")
					break

			for i, item in enumerate(forecast_items):
				forecast_info = {'item_index': i}

				# 提取日期
				date_elem = item.find('h1') or item.find('h2') or item.find('h3')
				if date_elem:
					forecast_info['date'] = date_elem.get_text().strip()

				# 提取天气描述
				weather_elem = item.find('big', class_='wea') or item.select_one('.weather-desc')
				if weather_elem:
					forecast_info['weather'] = weather_elem.get_text().strip()

				# 提取温度
				temp_elems = item.find_all('span')
				temps = []
				for temp in temp_elems:
					temp_text = temp.get_text().strip()
					if '°' in temp_text:
						temps.append(temp_text)

				if temps:
					forecast_info['temperature_range'] = ' / '.join(temps)

				# 提取风向风速
				wind_elem = item.find('span', title=True)
				if wind_elem:
					forecast_info['wind'] = wind_elem.get('title', '')

				if len(forecast_info) > 1:  # 除了item_index外还有其他数据
					forecast_info['data_type'] = 'forecast'
					forecast_list.append(forecast_info)

		except Exception as e:
			print(f"   预报数据提取错误: {e}")

		return forecast_list

	def _extract_generic_weather(self, soup):
		"""提取通用天气信息（备用方案）"""
		weather_data = []

		try:
			# 查找所有包含温度相关文本的元素
			temp_elements = soup.find_all(text=re.compile(r'\d+°'))
			for elem in temp_elements:
				parent = elem.parent if hasattr(elem, 'parent') else None
				if parent:
					weather_info = {
						'temperature': elem.strip(),
						'element_tag': parent.name,
						'element_class': parent.get('class', []),
						'data_type': 'generic_temp'
					}
					weather_data.append(weather_info)

			# 查找所有可能的天气描述
			weather_keywords = ['晴', '多云', '阴', '雨', '雪', '雾', '霾', '风']
			for keyword in weather_keywords:
				elements = soup.find_all(text=re.compile(keyword))
				for elem in elements[:2]:  # 限制数量
					weather_info = {
						'weather': elem.strip(),
						'keyword': keyword,
						'data_type': 'generic_weather'
					}
					weather_data.append(weather_info)

		except Exception as e:
			print(f"   通用数据提取错误: {e}")

		return weather_data[:10]  # 限制返回数量


# 单独运行测试
if __name__ == "__main__":
	print("🔍 数据提取器测试")

	# 尝试从调试文件加载HTML
	config = Config()
	utils = Utils()

	html_content = utils.load_debug_file(config.DEBUG_HTML_FILE)

	if html_content:
		print("✅ 从调试文件加载HTML")

		from bs4 import BeautifulSoup

		soup = BeautifulSoup(html_content, 'html.parser')

		extractor = DataExtractor()
		weather_data = extractor.extract_all_data(soup)

		print(f"\n📊 提取结果:")
		print(f"总数据量: {len(weather_data)}")

		# 按类型统计
		type_counts = {}
		for item in weather_data:
			data_type = item.get('data_type', 'unknown')
			type_counts[data_type] = type_counts.get(data_type, 0) + 1

		print("数据类型分布:")
		for data_type, count in type_counts.items():
			print(f"  {data_type}: {count} 条")

		# 保存提取的数据
		if weather_data:
			utils.save_debug_file(weather_data, config.DEBUG_JSON_FILE)
			print(f"✅ 数据已保存到 {config.DEBUG_JSON_FILE}")

			# 显示部分数据样例
			print("\n📝 数据样例:")
			for i, item in enumerate(weather_data[:3]):
				print(f"  样例 {i + 1}: {item}")

	else:
		print("❌ 未找到调试HTML文件")
		print("请先运行 web_scraper.py 生成调试文件")