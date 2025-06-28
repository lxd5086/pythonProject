# -*- coding: utf-8 -*-
"""
天气数据爬虫模块
"""

import requests
import time
import json
import csv
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import logging
from config import HEADERS, WEATHER_URLS, REQUEST_DELAY, TIMEOUT, MAX_RETRIES, DATA_FILES

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class WeatherScraper:
	def __init__(self):
		self.session = requests.Session()
		self.session.headers.update(HEADERS)

	def get_page_content(self, url, retries=MAX_RETRIES):
		"""获取网页内容"""
		for attempt in range(retries):
			try:
				response = self.session.get(url, timeout=TIMEOUT)
				response.raise_for_status()
				response.encoding = 'utf-8'
				logger.info(f"成功获取页面内容: {url}")
				return response.text
			except requests.RequestException as e:
				logger.warning(f"第{attempt + 1}次请求失败: {url}, 错误: {e}")
				if attempt < retries - 1:
					time.sleep(REQUEST_DELAY * (attempt + 1))
				else:
					logger.error(f"所有重试失败: {url}")
					return None

	def parse_china_weather(self, html_content):
		"""解析中国天气网数据"""
		if not html_content:
			return []

		soup = BeautifulSoup(html_content, 'html.parser')
		weather_data = []

		try:
			# 解析7天天气
			weather_list = soup.find('ul', class_='t clearfix')
			if weather_list:
				items = weather_list.find_all('li')
				for item in items:
					date_elem = item.find('h1')
					weather_elem = item.find('p', class_='wea')
					temp_elem = item.find('p', class_='tem')
					wind_elem = item.find('p', class_='win')

					if all([date_elem, weather_elem, temp_elem]):
						# 提取温度信息
						temp_high = temp_elem.find('span')
						temp_low = temp_elem.find('i')

						weather_info = {
							'date': date_elem.get_text(strip=True),
							'weather': weather_elem.get_text(strip=True),
							'temp_high': temp_high.get_text(strip=True) if temp_high else '',
							'temp_low': temp_low.get_text(strip=True) if temp_low else '',
							'wind': wind_elem.get_text(strip=True) if wind_elem else '',
							'source': 'china_weather',
							'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
						}
						weather_data.append(weather_info)

			logger.info(f"中国天气网解析完成，获取{len(weather_data)}条数据")

		except Exception as e:
			logger.error(f"解析中国天气网数据失败: {e}")

		return weather_data

	def parse_tianqi_so(self, html_content):
		"""解析全国天气网数据"""
		if not html_content:
			return []

		soup = BeautifulSoup(html_content, 'html.parser')
		weather_data = []

		try:
			# 查找天气信息容器
			weather_container = soup.find('div', class_='weather-list')
			if not weather_container:
				weather_container = soup.find('div', id='weather')

			if weather_container:
				weather_items = weather_container.find_all('div', class_='weather-item')
				if not weather_items:
					weather_items = weather_container.find_all('li')

				for item in weather_items:
					try:
						date = item.find(class_='date') or item.find('h3')
						weather = item.find(class_='weather') or item.find('p')
						temperature = item.find(class_='temperature') or item.find(class_='temp')

						if date and weather:
							weather_info = {
								'date': date.get_text(strip=True),
								'weather': weather.get_text(strip=True),
								'temperature': temperature.get_text(strip=True) if temperature else '',
								'source': 'tianqi_so',
								'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
							}
							weather_data.append(weather_info)
					except Exception as e:
						logger.warning(f"解析单个天气项目失败: {e}")
						continue

			logger.info(f"全国天气网解析完成，获取{len(weather_data)}条数据")

		except Exception as e:
			logger.error(f"解析全国天气网数据失败: {e}")

		return weather_data

	def scrape_all_sources(self):
		"""爬取所有数据源"""
		all_weather_data = []

		for source_name, url in WEATHER_URLS.items():
			logger.info(f"开始爬取 {source_name}: {url}")

			html_content = self.get_page_content(url)
			if html_content:
				if source_name == 'china_weather':
					data = self.parse_china_weather(html_content)
				elif source_name == 'tianqi_so':
					data = self.parse_tianqi_so(html_content)
				else:
					# 其他数据源的通用解析
					data = self.parse_generic_weather(html_content, source_name)

				all_weather_data.extend(data)

			# 请求间隔
			time.sleep(REQUEST_DELAY)

		return all_weather_data

	def parse_generic_weather(self, html_content, source_name):
		"""通用天气数据解析"""
		if not html_content:
			return []

		soup = BeautifulSoup(html_content, 'html.parser')
		weather_data = []

		try:
			# 尝试找到包含天气信息的元素
			possible_containers = [
				soup.find('div', class_='forecast'),
				soup.find('div', class_='weather'),
				soup.find('ul', class_='weather-list'),
				soup.find('div', id='forecast'),
			]

			for container in possible_containers:
				if container:
					# 提取基本信息
					text_content = container.get_text(strip=True)
					weather_info = {
						'content': text_content[:200],  # 限制长度
						'source': source_name,
						'crawl_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					}
					weather_data.append(weather_info)
					break

		except Exception as e:
			logger.error(f"通用解析失败 {source_name}: {e}")

		return weather_data

	def save_to_csv(self, weather_data, filename=None):
		"""保存数据到CSV文件"""
		if not weather_data:
			logger.warning("没有数据可保存")
			return

		filename = filename or DATA_FILES['weather_data']

		try:
			# 获取所有可能的字段
			all_fields = set()
			for item in weather_data:
				all_fields.update(item.keys())

			fieldnames = sorted(list(all_fields))

			with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
				writer.writeheader()
				writer.writerows(weather_data)

			logger.info(f"数据已保存到: {filename}, 共{len(weather_data)}条记录")

		except Exception as e:
			logger.error(f"保存CSV文件失败: {e}")

	def save_to_json(self, weather_data, filename=None):
		"""保存数据到JSON文件"""
		if not weather_data:
			logger.warning("没有数据可保存")
			return

		filename = filename or DATA_FILES['processed_data']

		try:
			with open(filename, 'w', encoding='utf-8') as f:
				json.dump(weather_data, f, ensure_ascii=False, indent=2)

			logger.info(f"数据已保存到: {filename}")

		except Exception as e:
			logger.error(f"保存JSON文件失败: {e}")


def main():
	"""主函数"""
	scraper = WeatherScraper()

	print("开始爬取浦东新区天气数据...")
	weather_data = scraper.scrape_all_sources()

	if weather_data:
		print(f"爬取完成，共获取 {len(weather_data)} 条数据")

		# 保存数据
		scraper.save_to_csv(weather_data)
		scraper.save_to_json(weather_data)

		# 显示部分数据
		print("\n最新数据预览:")
		for i, item in enumerate(weather_data[:3]):
			print(f"{i + 1}. {item}")
	else:
		print("未获取到任何数据")


if __name__ == "__main__":
	main()