# -*- coding: utf-8 -*-
"""
JD.com Scraper - Optimized for www.jd.com with Custom Page Count
This script scrapes laptop data from www.jd.com after manual login,
using #J_bottomPage > span.p-num > a.pn-next selector, user-defined page count,
reduced CAPTCHA triggers, and non-duplicate data.
"""

import time
import json
import csv
import os
import logging
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent

# --- 全局配置 ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")
SEARCH_KEYWORD = "笔记本电脑"
PERSISTENCE_STRATEGY = 'cookie'  # 默认使用 cookie，稳定性更高；可改为 'profile'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_PROFILE_PATH = os.path.join(BASE_DIR, 'JDProfile')
COOKIE_FILE_PATH = os.path.join(BASE_DIR, 'jd_cookies.json')
OUTPUT_FILE_NAME = os.path.join(BASE_DIR, f"JD_{SEARCH_KEYWORD}_products.csv")

def get_user_page_count():
    """获取用户输入的爬取页数。"""
    while True:
        try:
            pages = input("请输入想爬取的页数（例如，3 表示爬取 3 页）：")
            pages = int(pages)
            if pages < 1:
                print("页数必须为正整数，请重新输入。")
                continue
            return pages
        except ValueError:
            print("请输入有效的数字，例如 3。")

def init_driver(strategy: str, profile_path: str = None) -> webdriver.Chrome:
    """初始化 Chrome 浏览器驱动。"""
    logging.info("初始化Chrome浏览器驱动...")
    ua = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--start-maximized')
    # 可选：添加代理以减少验证码触发（需自行配置）
    # options.add_argument('--proxy-server=http://your_proxy:port')
    if strategy == 'profile' and profile_path:
        logging.info(f"使用用户数据目录: {profile_path}")
        options.add_argument(f'--user-data-dir={profile_path}')
    service = Service(ChromeDriverManager().install(), log_path=os.path.join(BASE_DIR, 'chromedriver.log'))
    for attempt in range(3):
        try:
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            })
            return driver
        except Exception as e:
            logging.warning(f"驱动初始化失败，重试 {attempt+1}/3: {e}")
            time.sleep(2)
    raise Exception("驱动初始化失败，程序终止")

def check_captcha(driver):
    """检查是否存在验证码页面。"""
    try:
        if "captcha" in driver.current_url.lower() or "verify" in driver.page_source.lower():
            logging.warning("检测到验证码，请手动完成验证后按 Enter 继续...")
            logging.warning("注意：您无需手动点击'下一页'，只需完成验证码并按回车。")
            input(">>> 完成验证码后按回车继续...")
            time.sleep(3)  # 增加延迟以确保页面稳定
            return True
    except NoSuchWindowException:
        logging.error("浏览器窗口已关闭，尝试重新初始化...")
        raise
    return False

def is_logged_in(driver):
    """检查是否已登录。"""
    try:
        driver.get('https://www.jd.com/')  # 先访问主页
        time.sleep(random.uniform(2, 4))  # 模拟人类行为
        check_captcha(driver)
        driver.get('https://order.jd.com/center/list.action')  # 检查订单页面
        check_captcha(driver)
        if 'login' in driver.current_url.lower() or 'passport' in driver.current_url.lower():
            return False
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nickname, .jd_user, .user-info, .login-info"))
        )
        return True
    except (TimeoutException, NoSuchWindowException):
        return False

def handle_login(driver: webdriver.Chrome, strategy: str, cookie_path: str):
    """处理登录流程。"""
    try:
        if strategy == 'profile':
            if is_logged_in(driver):
                logging.info("检测到已登录状态，跳过登录步骤。")
                return
            logging.warning("=" * 60)
            logging.warning("检测到未登录，请在弹出的浏览器中手动完成登录。")
            driver.get("https://passport.jd.com/new/login.aspx")
            check_captcha(driver)
            input(">>> 登录成功后，请将光标切回本窗口，然后按【回车键】继续...")
            check_captcha(driver)
            if not is_logged_in(driver):
                logging.error("登录验证失败，请重试")
                raise Exception("登录失败")

        elif strategy == 'cookie':
            if os.path.exists(cookie_path):
                logging.info(f"正在加载Cookies从 {cookie_path}...")
                driver.get("https://www.jd.com/")
                time.sleep(random.uniform(2, 4))  # 确保主页加载
                with open(cookie_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        logging.warning(f"添加 cookie 出错: {e}")
                driver.refresh()
                time.sleep(2)
                if is_logged_in(driver):
                    logging.info("Cookie登录成功！")
                    return
            logging.warning("Cookie无效或不存在，需要手动登录。")
            driver.get("https://passport.jd.com/new/login.aspx")
            check_captcha(driver)
            logging.warning("=" * 60)
            logging.warning("请在浏览器中手动登录（扫码或账号密码）。")
            input(">>> 登录成功后，请将光标切回本窗口，然后按【回车键】继续...")
            check_captcha(driver)
            if is_logged_in(driver):
                logging.info("正在保存新的Cookies...")
                with open(cookie_path, 'w', encoding='utf-8') as f:
                    json.dump(driver.get_cookies(), f)
                logging.info(f"Cookies已保存到 {cookie_path}")
            else:
                logging.error("登录验证失败，请重试")
                raise Exception("登录失败")
    except NoSuchWindowException:
        logging.error("浏览器窗口意外关闭，程序终止")
        raise

def scroll_page(driver, max_scrolls=10):
    """滚动页面加载更多商品。"""
    logging.info("滚动页面加载更多商品...")
    last_count = 0
    for i in range(max_scrolls):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(4, 6))  # 增加延迟以减少反爬
            check_captcha(driver)
            items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
            if len(items) == last_count and i > 0:
                break
            last_count = len(items)
        except NoSuchWindowException:
            logging.error("浏览器窗口关闭，滚动失败")
            raise
    logging.info(f"滚动完成，共加载 {last_count} 个商品")

def search_and_scrape(driver: webdriver.Chrome, keyword: str, max_pages: int):
    """执行搜索、滚动、解析和翻页。"""
    logging.info(f"开始搜索关键词: '{keyword}'")
    for attempt in range(3):
        try:
            driver.get("https://www.jd.com/")  # 先访问主页
            time.sleep(random.uniform(2, 4))  # 模拟人类行为
            # 模拟搜索框输入
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "key"))
                )
                search_box.clear()
                for char in keyword:  # 逐字符输入，模拟人类
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                time.sleep(1)
                search_box.send_keys(Keys.ENTER)
                time.sleep(random.uniform(2, 4))
            except TimeoutException:
                logging.warning("无法找到搜索框，使用直接 URL 访问")
                encoded_keyword = urllib.parse.quote(keyword)
                driver.get(f"https://search.jd.com/Search?keyword={encoded_keyword}&enc=utf-8")
            check_captcha(driver)
            wait = WebDriverWait(driver, 30)
            wait.until(EC.presence_of_element_located((By.ID, "J_goodsList")))
            break
        except (TimeoutException, NoSuchWindowException) as e:
            logging.warning(f"搜索页面加载失败，重试 {attempt+1}/3: {e}")
            if attempt == 2:
                logging.error("搜索页面加载失败，程序终止")
                return []
            time.sleep(5)

    all_products = []
    seen_titles = set()  # 跟踪已爬取的商品标题，防止重复
    for page in range(1, max_pages + 1):
        logging.info(f"--- 正在爬取第 {page}/{max_pages} 页 ---")
        try:
            current_url = driver.current_url
            logging.info(f"当前页面 URL: {current_url}")
            scroll_page(driver)
            items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
            logging.info(f"本页找到 {len(items)} 个商品条目。")
            new_items = 0  # 跟踪本页新商品数量
            for item in items:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, ".p-name em, .p-name a")
                    title = title_elem.text.strip()
                    if not title or title in seen_titles:
                        continue
                    seen_titles.add(title)
                    price = item.find_element(By.CSS_SELECTOR, ".p-price i, .p-price strong").text.strip()
                    link = item.find_element(By.CSS_SELECTOR, ".p-name a").get_attribute("href")
                    try:
                        shop = item.find_element(By.CSS_SELECTOR, ".p-shop a, .p-shop span").text.strip()
                    except NoSuchElementException:
                        shop = "京东自营"
                    try:
                        comment = item.find_element(By.CSS_SELECTOR, ".p-commit strong, .p-commit a").text.strip()
                    except NoSuchElementException:
                        comment = "0"
                    all_products.append({
                        "title": title, "price": price, "shop": shop, "comment": comment, "link": link
                    })
                    new_items += 1
                except (NoSuchElementException, NoSuchWindowException):
                    continue
            logging.info(f"本页新增 {new_items} 条有效数据。")
            if page < max_pages:
                for attempt in range(3):
                    try:
                        next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.pn-next")))
                        logging.info("点击'下一页'...")
                        ActionChains(driver).move_to_element(next_button).pause(random.uniform(0.5, 1)).click().perform()
                        time.sleep(random.uniform(4, 6))
                        check_captcha(driver)
                        # 验证翻页是否成功（京东页码：第 n 页为 page=2n-1）
                        expected_page = 2 * page + 1  # 第 2 页为 page=3，第 3 页为 page=5
                        WebDriverWait(driver, 10).until(
                            EC.url_contains(f"page={expected_page}")
                        )
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.ID, "J_goodsList"))
                        )
                        # 检查新页面是否加载了不同商品
                        new_items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
                        new_titles = [item.find_element(By.CSS_SELECTOR, ".p-name em, .p-name a").text.strip() for item in new_items[:5]]
                        if all(title in seen_titles for title in new_titles if title):
                            logging.warning("新页面商品与前页重复，尝试刷新...")
                            driver.refresh()
                            time.sleep(random.uniform(2, 4))
                            check_captcha(driver)
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.ID, "J_goodsList"))
                            )
                        break
                    except TimeoutException as e:
                        logging.warning(f"翻页失败，重试 {attempt+1}/3: {e}")
                        # 尝试备选选择器
                        try:
                            next_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".pn-next, .fp-next")))
                            logging.info("尝试备选'下一页'选择器...")
                            ActionChains(driver).move_to_element(next_button).pause(random.uniform(0.5, 1)).click().perform()
                            time.sleep(random.uniform(4, 6))
                            check_captcha(driver)
                            WebDriverWait(driver, 10).until(
                                EC.url_contains(f"page={expected_page}")
                            )
                            WebDriverWait(driver, 30).until(
                                EC.presence_of_element_located((By.ID, "J_goodsList"))
                            )
                            break
                        except TimeoutException:
                            if attempt == 2:
                                logging.warning("翻页失败，爬取结束。")
                                return all_products
                            time.sleep(5)
        except NoSuchWindowException:
            logging.error("浏览器窗口关闭，爬取失败")
            break
    return all_products

def save_data(products: list, filename: str):
    """将数据保存到CSV文件。"""
    if not products:
        logging.warning("没有爬取到任何数据，不创建文件。")
        return
    logging.info(f"共爬取 {len(products)} 条有效数据，准备写入文件 {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "shop", "comment", "link"])
        writer.writeheader()
        writer.writerows(products)
    logging.info(f"数据保存成功！文件位于: {filename}")

def main():
    """主执行函数"""
    logging.info("=" * 60)
    logging.info("  京东商品数据爬虫（手动确认登录版）启动")
    logging.info("=" * 60)
    driver = None
    try:
        # 获取用户输入的页数
        max_pages = get_user_page_count()
        logging.info(f"用户选择爬取 {max_pages} 页数据")
        if PERSISTENCE_STRATEGY == 'profile' and not os.path.exists(USER_PROFILE_PATH):
            os.makedirs(USER_PROFILE_PATH)
            logging.info(f"已自动创建用户数据目录: {USER_PROFILE_PATH}")
        driver = init_driver(PERSISTENCE_STRATEGY, USER_PROFILE_PATH)
        handle_login(driver, PERSISTENCE_STRATEGY, COOKIE_FILE_PATH)
        products = search_and_scrape(driver, SEARCH_KEYWORD, max_pages)
        save_data(products, OUTPUT_FILE_NAME)
    except Exception as e:
        logging.error(f"发生未捕获的严重错误: {e}", exc_info=True)
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass
        logging.info("浏览器已关闭，程序执行完毕。")
        logging.info("=" * 60)

if __name__ == "__main__":
    main()