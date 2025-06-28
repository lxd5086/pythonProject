# src/selenium_scraper.py

import time
import random
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import config


class TiebaSeleniumScraper:
	def __init__(self):
		self.tieba_name = config.TIEBA_NAME
		self.pages_to_scrape = config.PAGES_TO_SCRAPE
		self.save_path = config.RAW_DATA_PATH
		self.max_replies_per_post = 20  # 每个帖子最多爬取20个回复
		self.max_posts_per_page = 10  # 每页最多爬取10个帖子
		self.driver = None
		self.wait = None

	def setup_driver(self):
		"""设置Chrome浏览器驱动"""
		chrome_options = Options()
		# 设置为无头模式（不显示浏览器界面）
		# chrome_options.add_argument('--headless')
		chrome_options.add_argument('--no-sandbox')
		chrome_options.add_argument('--disable-dev-shm-usage')
		chrome_options.add_argument('--disable-gpu')
		chrome_options.add_argument('--window-size=1920,1080')

		# 设置用户代理
		chrome_options.add_argument(
			'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

		# 禁用图片加载以提高速度
		prefs = {
			"profile.managed_default_content_settings.images": 2,
			"profile.default_content_setting_values.notifications": 2
		}
		chrome_options.add_experimental_option("prefs", prefs)

		try:
			self.driver = webdriver.Chrome(options=chrome_options)
			self.wait = WebDriverWait(self.driver, 10)
			print("Chrome浏览器启动成功")
			return True
		except Exception as e:
			print(f"Chrome浏览器启动失败: {e}")
			return False

	def search_tieba(self):
		"""搜索目标贴吧"""
		try:
			# 访问百度贴吧首页
			print("正在访问百度贴吧首页...")
			self.driver.get("https://tieba.baidu.com/")
			time.sleep(2)

			# 找到搜索框并输入贴吧名称
			search_box = self.wait.until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "#wd1"))
			)
			search_box.clear()
			search_box.send_keys(self.tieba_name)

			# 点击搜索按钮
			search_button = self.driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='进入贴吧']")
			search_button.click()

			print(f"成功搜索贴吧: {self.tieba_name}")
			time.sleep(3)
			return True

		except Exception as e:
			print(f"搜索贴吧失败: {e}")
			return False

	def get_post_links(self):
		"""获取当前页面的帖子链接"""
		post_links = []
		try:
			# 等待帖子列表加载
			self.wait.until(
				EC.presence_of_element_located((By.CSS_SELECTOR, ".threadlist_title"))
			)

			# 获取帖子链接
			post_elements = self.driver.find_elements(By.CSS_SELECTOR, ".threadlist_title a")

			for element in post_elements[:self.max_posts_per_page]:
				link = element.get_attribute('href')
				title = element.text.strip()
				if link and title:
					post_links.append({
						'title': title,
						'url': link
					})

			print(f"当前页面获取到 {len(post_links)} 个帖子链接")
			return post_links

		except Exception as e:
			print(f"获取帖子链接失败: {e}")
			return []

	def scrape_post_content(self, post_url, post_title):
		"""爬取单个帖子的内容和回复"""
		try:
			print(f"正在爬取帖子: {post_title}")
			self.driver.get(post_url)
			time.sleep(2)

			# 获取帖子主内容
			main_content = ""
			try:
				main_content_element = self.wait.until(
					EC.presence_of_element_located((By.CSS_SELECTOR, ".d_post_content"))
				)
				main_content = main_content_element.text.strip()
			except:
				# 如果主选择器失败，尝试其他选择器
				try:
					main_content_element = self.driver.find_element(By.CSS_SELECTOR, ".post_bubble_middle")
					main_content = main_content_element.text.strip()
				except:
					main_content = "无法获取帖子内容"

			# 获取回复列表
			replies = []
			try:
				reply_elements = self.driver.find_elements(By.CSS_SELECTOR, ".l_post")

				for i, reply_element in enumerate(reply_elements[1:self.max_replies_per_post + 1]):  # 跳过第一个（主帖）
					try:
						# 获取回复内容
						reply_content_element = reply_element.find_element(By.CSS_SELECTOR, ".d_post_content")
						reply_content = reply_content_element.text.strip()

						# 获取回复者用户名
						try:
							username_element = reply_element.find_element(By.CSS_SELECTOR, ".p_author_name")
							username = username_element.text.strip()
						except:
							username = "匿名用户"

						# 获取回复时间
						try:
							time_element = reply_element.find_element(By.CSS_SELECTOR, ".tail-info")
							reply_time = time_element.text.strip()
						except:
							reply_time = "未知时间"

						if reply_content:
							replies.append({
								'username': username,
								'content': reply_content,
								'time': reply_time
							})

					except Exception as e:
						continue

			except Exception as e:
				print(f"获取回复失败: {e}")

			post_data = {
				'title': post_title,
				'url': post_url,
				'main_content': main_content,
				'replies': replies,
				'reply_count': len(replies)
			}

			print(f"成功爬取帖子，回复数: {len(replies)}")
			return post_data

		except Exception as e:
			print(f"爬取帖子内容失败: {e}")
			return None

	def go_to_next_page(self):
		"""翻到下一页"""
		try:
			# 查找下一页按钮
			next_button = self.driver.find_element(By.CSS_SELECTOR, "#frs_list_pager > a.next.pagination-item")
			if next_button and next_button.is_enabled():
				next_button.click()
				time.sleep(3)
				return True
			else:
				print("没有找到下一页按钮或已到最后一页")
				return False
		except Exception as e:
			print(f"翻页失败: {e}")
			return False

	def run(self):
		"""执行爬虫的主函数"""
		print(f"--- [Selenium爬虫模块] 任务开始，目标贴吧: '{self.tieba_name}'，计划爬取 {self.pages_to_scrape} 页 ---")

		# 设置浏览器驱动
		if not self.setup_driver():
			return

		try:
			# 搜索目标贴吧
			if not self.search_tieba():
				return

			all_posts_data = []

			for page in range(self.pages_to_scrape):
				print(f"\n--- 正在处理第 {page + 1}/{self.pages_to_scrape} 页 ---")

				# 获取当前页面的帖子链接
				post_links = self.get_post_links()

				if not post_links:
					print("当前页面没有找到帖子，跳过")
					if page < self.pages_to_scrape - 1:
						if not self.go_to_next_page():
							break
					continue

				# 爬取每个帖子的详细内容
				for post_link in post_links:
					post_data = self.scrape_post_content(post_link['url'], post_link['title'])
					if post_data:
						all_posts_data.append(post_data)

					# 随机延迟
					time.sleep(random.uniform(1, 3))

				print(f"第 {page + 1} 页完成，共爬取 {len(post_links)} 个帖子")

				# 翻页（除了最后一页）
				if page < self.pages_to_scrape - 1:
					if not self.go_to_next_page():
						break

			# 保存数据
			if all_posts_data:
				self.save_data(all_posts_data)
				print(f"--- [Selenium爬虫模块] 任务完成，共爬取 {len(all_posts_data)} 个帖子 ---")
			else:
				print("--- [Selenium爬虫模块] 任务失败，未能获取任何数据 ---")

		except Exception as e:
			print(f"爬虫执行过程中发生错误: {e}")
		finally:
			# 关闭浏览器
			if self.driver:
				self.driver.quit()
				print("浏览器已关闭")

	def save_data(self, all_posts_data):
		"""保存爬取的数据"""
		try:
			# 保存为JSON格式（包含完整的回复信息）
			json_path = self.save_path.replace('.csv', '.json')
			with open(json_path, 'w', encoding='utf-8') as f:
				json.dump(all_posts_data, f, ensure_ascii=False, indent=2)
			print(f"完整数据已保存至: {json_path}")

			# 保存为CSV格式（扁平化的数据）
			csv_data = []
			for post in all_posts_data:
				# 主帖数据
				csv_data.append({
					'post_title': post['title'],
					'post_url': post['url'],
					'content': post['main_content'],
					'type': '主帖',
					'username': '楼主',
					'time': '',
					'reply_count': post['reply_count']
				})

				# 回复数据
				for reply in post['replies']:
					csv_data.append({
						'post_title': post['title'],
						'post_url': post['url'],
						'content': reply['content'],
						'type': '回复',
						'username': reply['username'],
						'time': reply['time'],
						'reply_count': post['reply_count']
					})

			df = pd.DataFrame(csv_data)
			df.to_csv(self.save_path, index=False, encoding='utf-8-sig')
			print(f"CSV数据已保存至: {self.save_path}")

		except Exception as e:
			print(f"保存数据失败: {e}")


# 使用示例
if __name__ == "__main__":
	scraper = TiebaSeleniumScraper()
	scraper.run()