# -*- coding: utf-8 -*-
"""
Lianjia.com Scraper - 修复翻页功能版本

主要修复：
1. 优化"下一页"按钮的定位策略
2. 增加多种翻页方式的备选方案
3. 改进页面加载等待机制
4. 增加更详细的调试信息
"""

import time
import json
import csv
import os
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException, \
	WebDriverException, ElementClickInterceptedException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# --- 全局配置 (Global Configuration) ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")

TARGET_DISTRICT = "pudong"
CITY_CODE = "sh"
CITY_HOMEPAGE_URL = f"https://{CITY_CODE}.lianjia.com/"
BASE_URL = f"https://{CITY_CODE}.lianjia.com/zufang/{TARGET_DISTRICT}/"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIE_FILE_PATH = os.path.join(BASE_DIR, 'data', 'lianjia_cookies.json')  # 修改此处
OUTPUT_FILE_NAME = os.path.join(BASE_DIR, 'data', f"Lianjia_{TARGET_DISTRICT}_rentals.csv")

def get_user_page_count():
	"""获取用户想要爬取的最大页数。"""
	while True:
		try:
			pages = input("请输入希望爬取的最大页数（输入0则抓取所有页面，推荐先用1-2页测试）：")
			pages = int(pages)
			if pages < 0:
				print("页数不能为负数，请重新输入。")
				continue
			return pages if pages > 0 else float('inf')
		except ValueError:
			print("请输入一个有效的数字 (例如: 3)。")


def init_driver() -> webdriver.Chrome:
	"""初始化Chrome浏览器驱动。"""
	logging.info("正在初始化Chrome浏览器驱动...")
	ua = UserAgent()
	options = webdriver.ChromeOptions()
	options.add_argument(f"user-agent={ua.random}")
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option('useAutomationExtension', False)
	options.add_argument('--start-maximized')

	service = Service(ChromeDriverManager().install(), log_path=os.path.join(BASE_DIR, 'chromedriver.log'))

	try:
		driver = webdriver.Chrome(service=service, options=options)
		driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
			"source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
		})
		return driver
	except Exception as e:
		logging.error(f"驱动初始化失败: {e}")
		raise


def handle_login(driver: webdriver.Chrome, cookie_path: str):
	"""处理登录流程，优先使用Cookie，否则提示用户在城市首页手动登录。"""
	driver.get(CITY_HOMEPAGE_URL)
	time.sleep(1)

	if os.path.exists(cookie_path):
		logging.info(f"发现Cookie文件，正在加载: {cookie_path}")
		with open(cookie_path, 'r', encoding='utf-8') as f:
			cookies = json.load(f)
		for cookie in cookies:
			try:
				driver.add_cookie(cookie)
			except Exception:
				pass
		logging.info("Cookie已加载。将直接刷新页面并开始爬取。")
		driver.refresh()
		time.sleep(2)
		return

	# --- 手动登录流程 ---
	logging.warning("Cookie文件不存在，需要您手动登录一次以生成Cookie文件。")
	driver.get(CITY_HOMEPAGE_URL)
	logging.warning("=" * 60)
	logging.warning("浏览器已打开上海链家首页。")
	logging.warning("请在该页面手动点击右上角的【登录】按钮，并完成扫码登录。")
	input(">>> 登录成功后，请将光标切回本窗口，然后按【回车键】继续...")

	logging.info("操作已确认，正在保存您当前的登录状态 (Cookies)...")
	try:
		with open(cookie_path, 'w', encoding='utf-8') as f:
			json.dump(driver.get_cookies(), f)
		logging.info(f"Cookies已成功保存到 {cookie_path}，下次运行将实现自动登录。")
	except Exception as e:
		logging.error(f"保存Cookie失败: {e}")


def parse_page(driver: webdriver.Chrome) -> list:
	"""解析当前页面的房源信息。"""
	rental_list = []
	wait = WebDriverWait(driver, 20)
	try:
		wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content__list")))

		logging.info("正在向下滚动页面以加载所有房源...")
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight * 0.8);")
		time.sleep(random.uniform(2, 4))
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(random.uniform(2, 4))

		items = driver.find_elements(By.CSS_SELECTOR, ".content__list--item")
		logging.info(f"在本页找到 {len(items)} 个房源条目。")

		for item in items:
			try:
				title_element = item.find_element(By.CSS_SELECTOR, ".content__list--item--title")
				title = title_element.text.strip()
				link = title_element.find_element(By.TAG_NAME, "a").get_attribute("href")
				price_element = item.find_element(By.CSS_SELECTOR, ".content__list--item-price em")
				price = price_element.text.strip()
				des_element = item.find_element(By.CSS_SELECTOR, ".content__list--item--des")
				des_links = des_element.find_elements(By.TAG_NAME, "a")
				district = des_links[0].text.strip() if des_links else "N/A"
				full_des_text = des_element.text
				parts = [p.strip() for p in full_des_text.split('/')]
				area = next((p for p in parts if '㎡' in p), "N/A")
				layout = next((p for p in parts if '室' in p or '厅' in p), "N/A")
				orientation = next((p for p in parts if '朝' in p), "N/A")
				update_time_element = item.find_element(By.CSS_SELECTOR, ".content__list--item--time")
				update_time = update_time_element.text.strip()
				tags_elements = item.find_elements(By.CSS_SELECTOR,
												   ".content__list--item--bottom .content__list--item--tags")
				tags = ', '.join([tag.text for tag in tags_elements]) if tags_elements else "无"
				rental_data = {
					"title": title, "link": link, "district": district, "layout": layout,
					"area": area, "orientation": orientation, "price": f"{price} 元/月",
					"update_time": update_time, "tags": tags
				}
				rental_list.append(rental_data)

			except NoSuchElementException:
				pass

	except TimeoutException:
		logging.error("等待房源列表超时，页面可能未正确加载。")

	logging.info(f"本页成功解析 {len(rental_list)} 条有效数据。")
	return rental_list


def try_next_page(driver: webdriver.Chrome, current_page: int) -> bool:
	"""
	尝试翻页到下一页，使用多种策略
	返回 True 表示成功翻页，False 表示无法翻页（可能到达最后一页）
	"""
	wait = WebDriverWait(driver, 15)

	# 策略1: 查找并分析分页区域
	logging.info("正在分析页面分页信息...")
	try:
		# 滚动到页面底部，确保分页区域可见
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(2)

		# 查找分页容器
		page_selectors = [
			"div.page-box",
			".page-box",
			"div[class*='page']",
			"div[class*='pager']",
			"div[class*='pagination']"
		]

		page_container = None
		for selector in page_selectors:
			try:
				page_container = driver.find_element(By.CSS_SELECTOR, selector)
				logging.info(f"找到分页容器: {selector}")
				break
			except NoSuchElementException:
				continue

		if page_container:
			# 打印分页区域的HTML，便于调试
			page_html = page_container.get_attribute('outerHTML')
			logging.info(f"分页区域HTML结构: {page_html[:500]}...")

			# 查找所有可能的下一页按钮
			next_selectors = [
				"a.next",
				"a[class*='next']",
				"a:contains('下一页')",
				"a:contains('下页')",
				"a:contains('>')",
				f"a[href*='pg{current_page + 1}']",  # 直接查找包含下一页页码的链接
				f"a:contains('{current_page + 1}')"  # 查找包含下一页页码的链接
			]

			next_button = None
			for selector in next_selectors:
				try:
					if ":contains(" in selector:
						# 使用XPath处理包含文本的选择器
						xpath = f"//a[contains(text(), '{selector.split('(')[1].split(')')[0]}')]"
						next_button = page_container.find_element(By.XPATH, xpath)
					else:
						next_button = page_container.find_element(By.CSS_SELECTOR, selector)

					# 检查按钮是否可点击（不是disabled状态）
					if next_button.is_enabled() and next_button.is_displayed():
						button_class = next_button.get_attribute('c-lass') or ''
						if 'disabled' not in button_class.lower():
							logging.info(f"找到可用的下一页按钮: {selector}")
							break
					next_button = None
				except NoSuchElementException:
					continue

			# 策略2: 如果没找到下一页按钮，尝试查找具体页码链接
			if not next_button:
				try:
					next_page_num = current_page + 1
					page_links = page_container.find_elements(By.TAG_NAME, "a")
					for link in page_links:
						link_text = link.text.strip()
						if link_text == str(next_page_num):
							next_button = link
							logging.info(f"找到页码链接: {next_page_num}")
							break
				except Exception as e:
					logging.debug(f"查找页码链接时出错: {e}")

			# 尝试点击下一页按钮
			if next_button:
				try:
					# 确保按钮在视图中
					driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
					time.sleep(1)

					# 获取当前URL，用于验证是否成功翻页
					current_url = driver.current_url

					# 尝试点击
					next_button.click()
					logging.info("已点击下一页按钮，等待页面加载...")

					# 等待URL变化或页面内容更新
					time.sleep(random.uniform(3, 5))

					# 验证是否成功翻页
					new_url = driver.current_url
					if new_url != current_url:
						logging.info(f"URL已变化，翻页成功: {new_url}")
						return True
					else:
						# URL没变化，等待页面内容更新
						try:
							wait.until(EC.staleness_of(next_button))
							logging.info("页面内容已更新，翻页成功")
							return True
						except TimeoutException:
							logging.warning("点击后页面未发生预期变化")

				except ElementClickInterceptedException:
					# 如果普通点击被拦截，尝试JavaScript点击
					logging.info("普通点击被拦截，尝试JavaScript点击...")
					try:
						driver.execute_script("arguments[0].click();", next_button)
						time.sleep(random.uniform(3, 5))
						new_url = driver.current_url
						if new_url != current_url:
							logging.info("JavaScript点击成功，翻页成功")
							return True
					except Exception as e:
						logging.error(f"JavaScript点击也失败: {e}")

				except Exception as e:
					logging.error(f"点击下一页按钮时出错: {e}")

		# 策略3: 尝试直接构造下一页URL
		current_url = driver.current_url
		if f"/pg{current_page}/" in current_url:
			next_url = current_url.replace(f"/pg{current_page}/", f"/pg{current_page + 1}/")
		elif current_page == 1 and "/pg" not in current_url:
			# 第一页通常不包含pg参数
			if current_url.endswith('/'):
				next_url = f"{current_url}pg2/"
			else:
				next_url = f"{current_url}/pg2/"
		else:
			next_url = None

		if next_url:
			logging.info(f"尝试直接访问下一页URL: {next_url}")
			driver.get(next_url)
			time.sleep(random.uniform(3, 5))

			# 检查页面是否有效加载
			try:
				wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.content__list")))
				logging.info("直接URL访问成功，翻页成功")
				return True
			except TimeoutException:
				logging.warning("直接URL访问后页面加载异常")

	except Exception as e:
		logging.error(f"翻页过程中发生错误: {e}")

	logging.info("所有翻页策略都失败，可能已到达最后一页")
	return False


def save_to_csv(data: list, filename: str):
	"""保存数据到CSV文件。"""
	if not data:
		logging.warning("没有爬取到任何数据，将不会创建CSV文件。")
		return

	logging.info(f"共爬取 {len(data)} 条数据，准备写入文件: {filename}")
	fieldnames = ["title", "price", "layout", "area", "orientation", "district", "update_time", "tags", "link"]

	try:
		with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
			writer = csv.DictWriter(f, fieldnames=fieldnames)
			writer.writeheader()
			writer.writerows(data)
		logging.info(f"数据已成功保存到: {filename}")
	except IOError as e:
		logging.error(f"保存文件失败: {e}")


def main():
	"""主执行函数。"""
	logging.info("=" * 60)
	logging.info(f"  链家租房数据爬虫启动 - 目标区域: {TARGET_DISTRICT.upper()}")
	logging.info("=" * 60)

	driver = None
	all_rentals = []

	try:
		max_pages = get_user_page_count()
		driver = init_driver()

		handle_login(driver, COOKIE_FILE_PATH)

		logging.info(f"登录流程处理完毕，即将开始爬取目标页面: {BASE_URL}")
		driver.get(BASE_URL)
		time.sleep(random.uniform(3, 5))

		current_page = 1
		while current_page <= max_pages:
			logging.info(f"--- 正在爬取第 {current_page} 页 ---")

			page_data = parse_page(driver)
			if not page_data:
				logging.info("当前页面无数据，可能已到达末页，爬取结束。")
				break

			all_rentals.extend(page_data)
			logging.info(f"第 {current_page} 页爬取完成，累计获取 {len(all_rentals)} 条数据")

			if current_page >= max_pages:
				logging.info(f"已达到用户设定的最大页数 {max_pages}，爬取结束。")
				break

			# 尝试翻页
			if try_next_page(driver, current_page):
				current_page += 1
				# 翻页成功后等待页面稳定
				time.sleep(random.uniform(2, 4))
			else:
				logging.info("无法继续翻页，爬取结束。")
				break

	except (NoSuchWindowException, WebDriverException) as e:
		if isinstance(e, NoSuchWindowException):
			logging.error("浏览器窗口被意外关闭，程序终止。")
		else:
			logging.error(f"发生WebDriver错误: {e}", exc_info=False)
	except Exception as e:
		logging.error(f"发生未预料的严重错误: {e}", exc_info=True)
	finally:
		if driver:
			try:
				driver.quit()
				logging.info("浏览器驱动已关闭。")
			except Exception:
				pass

		save_to_csv(all_rentals, OUTPUT_FILE_NAME)
		logging.info("=" * 60)
		logging.info("程序执行完毕。")
		logging.info("=" * 60)


if __name__ == "__main__":
	main()