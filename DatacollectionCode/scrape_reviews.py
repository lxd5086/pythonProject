# 1_scrape_hottest_reviews.py
# 最终版功能：通过手动辅助登录，爬取按热度排序的影评完整内容。

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time
import random
import os

# ==================== 配置区 ====================
DOUBAN_LOGIN_URL = 'https://accounts.douban.com/passport/login'
TARGET_REVIEWS_URL = 'https://movie.douban.com/subject/1889243/reviews?sort=hotest'

MANUAL_LOGIN_WAIT_SECONDS = 60
MAX_PAGES_TO_SCRAPE = 5
OUTPUT_DIR = r'C:\code-python\pythonProject\DatacollectionCode\data'
JSON_FILENAME = 'interstellar_HOTTEST_reviews.json'
WAIT_TIMEOUT = 15


# ==================== 主程序 ====================
def scrape_hottest_full_content():
	"""通过点击“展开”抓取热门影评的完整内容"""
	print("--- 启动“热门影评完整内容”爬取任务 ---")

	try:
		service = ChromeService(executable_path=ChromeDriverManager().install())
		driver = webdriver.Chrome(service=service)
		print("浏览器初始化成功！")
	except Exception as e:
		print(f"错误：浏览器驱动初始化失败 - {e}")
		return

	# --- 手动登录环节 ---
	try:
		driver.get(DOUBAN_LOGIN_URL)
		print("\n============================================================")
		print(f"浏览器已打开，请在 {MANUAL_LOGIN_WAIT_SECONDS} 秒内，手动完成微信扫码登录操作。")
		print("登录成功后，程序将自动开始爬取。")
		print("============================================================")
		time.sleep(MANUAL_LOGIN_WAIT_SECONDS)
		print("\n手动登录时间到，开始执行自动化爬取任务...")
	except Exception as e:
		print(f"导航到登录页面时出错: {e}")
		driver.quit()
		return

	# --- 自动化爬取逻辑 ---
	all_reviews = []
	full_path = os.path.join(OUTPUT_DIR, JSON_FILENAME)
	os.makedirs(OUTPUT_DIR, exist_ok=True)

	try:
		for i in range(MAX_PAGES_TO_SCRAPE):
			current_page_num = i + 1
			start_param = i * 20
			page_url = f"{TARGET_REVIEWS_URL}&start={start_param}"

			print(f"\n正在爬取热门榜第 {current_page_num}/{MAX_PAGES_TO_SCRAPE} 页...")
			driver.get(page_url)

			try:
				WebDriverWait(driver, WAIT_TIMEOUT).until(
					EC.presence_of_element_located((By.CLASS_NAME, "review-list"))
				)
				review_elements_xpath = "//div[contains(@class, 'review-item')]"
				review_elements = driver.find_elements(By.XPATH, review_elements_xpath)

				print(f"本页找到 {len(review_elements)} 个评论区，开始逐一展开...")
				for index in range(len(review_elements)):
					review_item = driver.find_elements(By.XPATH, review_elements_xpath)[index]
					try:
						expand_button = review_item.find_element(By.XPATH, ".//a[contains(@class, 'unfold')]")
						driver.execute_script("arguments[0].click();", expand_button)
						time.sleep(0.5)
					except NoSuchElementException:
						pass

				print("本页所有评论已展开，开始提取完整文本...")
				page_html = driver.page_source
				soup = BeautifulSoup(page_html, 'html.parser')

				review_items_soup = soup.select('div.review-item')
				for item_soup in review_items_soup:
					content_div = item_soup.select_one('div.review-content')
					if content_div:
						all_reviews.append({'content': content_div.get_text(strip=True)})

			except TimeoutException:
				print("错误：等待超时，页面上未找到评论列表。")
				break

			sleep_time = random.uniform(2, 4)
			print(f"本页处理完毕，暂停 {sleep_time:.2f} 秒...")
			time.sleep(sleep_time)

	finally:
		print("\n爬取循环结束，正在关闭浏览器...")
		driver.quit()
		if all_reviews:
			print(f"共获得 {len(all_reviews)} 条完整的热门影评，正在保存...")
			with open(full_path, 'w', encoding='utf-8') as f:
				json.dump(all_reviews, f, ensure_ascii=False, indent=4)
			print(f"数据已成功保存到 {full_path}")
		else:
			print("警告: 未能获取任何影评。")
		print("--- 爬虫任务结束 ---")


if __name__ == '__main__':
	scrape_hottest_full_content()