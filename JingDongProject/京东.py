from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
import time
import json
import csv
import urllib.parse
import os
import logging
import random

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
SEARCH_KEYWORD = "笔记本电脑"
OUTPUT_FILE = "jd_products.csv"
COOKIE_FILE = "jd_cookies.json"

def init_driver():
    """初始化 Chrome 浏览器驱动."""
    ua = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--no-sandbox')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def check_captcha(driver):
    """检查是否存在验证码页面."""
    if "captcha" in driver.current_url.lower() or "verify" in driver.page_source.lower():
        logging.warning("检测到验证码，请手动完成验证后按 Enter 继续...")
        input()
        return True
    return False

def save_cookies(driver, path):
    """保存 cookies 到文件."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(driver.get_cookies(), f)
    logging.info(f"Cookies 已保存到 {path}")

def load_cookies(driver, path):
    """加载 cookies 并验证登录状态."""
    if not os.path.exists(path):
        logging.info(f"未找到 cookies 文件: {path}")
        return False
    with open(path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    driver.get("https://www.jd.com/")  # 先访问主页以设置域名
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            logging.warning(f"添加 cookie 出错: {str(e)}")
    driver.refresh()
    time.sleep(2)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nickname, .user_menu .nickname, .jd_user"))
        )
        logging.info("Cookies 登录成功")
        return True
    except TimeoutException:
        logging.warning("Cookies 无效，需要重新登录")
        return False

def manual_login_and_save(driver):
    """手动登录并保存 cookies."""
    driver.get("https://www.jd.com/")
    check_captcha(driver)
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".link-login, .login-btn, .jd_login"))
        )
        login_btn.click()
    except TimeoutException:
        logging.warning("无法自动点击登录按钮，请手动登录")
    logging.info("请手动完成京东登录（扫码/账号登录），完成后按 Enter 保存 cookies")
    input("登录完成后按 Enter: ")
    check_captcha(driver)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nickname, .user_menu .nickname, .jd_user"))
        )
        logging.info("登录成功")
        save_cookies(driver, COOKIE_FILE)
        return True
    except TimeoutException:
        logging.error("登录验证失败")
        return False

def use_cookies_and_search(driver, keyword):
    """使用 cookies 进行搜索."""
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://search.jd.com/Search?keyword={encoded_keyword}"
    driver.get(search_url)
    check_captcha(driver)
    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".gl-item"))
        )
        logging.info("搜索结果加载完成")
        return True
    except TimeoutException:
        logging.error("搜索超时或页面结构变化")
        return False

def scroll_page(driver, max_scrolls=10):
    """滚动页面加载更多商品."""
    logging.info("滚动页面加载更多商品...")
    last_count = 0
    for i in range(max_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 4))
        check_captcha(driver)
        items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
        if len(items) == last_count and i > 0:
            break
        last_count = len(items)
    logging.info(f"页面滚动完成，共加载 {last_count} 个商品")

def parse_products(driver):
    """解析商品信息."""
    products = []
    items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
    logging.info(f"找到 {len(items)} 个商品")
    for index, item in enumerate(items):
        try:
            title_elem = item.find_element(By.CSS_SELECTOR, ".p-name em, .p-name a")
            title = title_elem.text.strip() or title_elem.get_attribute("title")
            price = item.find_element(By.CSS_SELECTOR, ".p-price strong, .p-price i").text.strip()
            try:
                shop = item.find_element(By.CSS_SELECTOR, ".p-shop a, .p-shop span").text.strip()
            except NoSuchElementException:
                shop = "京东自营"
            try:
                comment = item.find_element(By.CSS_SELECTOR, ".p-commit strong, .p-commit a").text.strip()
            except NoSuchElementException:
                comment = "0"
            link = item.find_element(By.CSS_SELECTOR, ".p-img a").get_attribute("href")
            products.append({
                "title": title,
                "price": price,
                "shop": shop,
                "comment": comment,
                "link": link
            })
            if (index + 1) % 10 == 0:
                logging.info(f"已解析 {index + 1}/{len(items)} 个商品")
        except Exception as e:
            logging.warning(f"解析商品 {index + 1} 出错: {str(e)}")
    logging.info(f"完成解析 {len(products)} 个商品")
    return products

def save_to_csv(products, filename):
    """保存商品数据到 CSV."""
    if not products:
        logging.warning("没有商品数据可保存")
        return
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "shop", "comment", "link"])
        writer.writeheader()
        writer.writerows(products)
    logging.info(f"成功保存 {len(products)} 条数据到 {filename}")

def main():
    """主函数."""
    logging.info("=" * 50)
    logging.info("京东商品爬虫启动")
    logging.info("=" * 50)

    driver = init_driver()
    try:
        login_success = False
        if os.path.exists(COOKIE_FILE):
            logging.info("尝试加载 cookies")
            login_success = load_cookies(driver, COOKIE_FILE)
        if not login_success:
            logging.info("需要手动登录")
            if not manual_login_and_save(driver):
                logging.error("登录失败，退出程序")
                return

        if use_cookies_and_search(driver, SEARCH_KEYWORD):
            scroll_page(driver)
            products = parse_products(driver)
            save_to_csv(products, OUTPUT_FILE)
        else:
            logging.error("搜索失败，程序终止")

    except Exception as e:
        logging.error(f"程序出错: {str(e)}")
    finally:
        driver.quit()
        logging.info("浏览器已关闭")
        logging.info("=" * 50)
        logging.info("程序执行完成")
        logging.info("=" * 50)

if __name__ == "__main__":
    main()