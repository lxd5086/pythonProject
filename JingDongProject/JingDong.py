from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import json
import csv
import urllib.parse
import os

SEARCH_KEYWORD = "笔记本电脑"
OUTPUT_FILE = "jd_products.csv"
COOKIE_FILE = "jd_cookies.json"
DRIVER_PATH = r"C:\Users\柯南\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-infobars')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--no-sandbox')
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    )
    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver

def save_cookies(driver, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(driver.get_cookies(), f)
    print(f"✅ Cookies 已保存到 {path}")

def load_cookies(driver, path):
    with open(path, 'r', encoding='utf-8') as f:
        cookies = json.load(f)
    for cookie in cookies:
        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"⚠ 添加cookie时出错: {str(e)}")
    print(f"✅ Cookies 已加载")
    driver.refresh()
    time.sleep(2)
    try:
        driver.find_element(By.CSS_SELECTOR, ".nickname")
        print("✅ Cookies 登录成功")
        return True
    except NoSuchElementException:
        print("❌ Cookies 无效，需要重新登录")
        return False

def manual_login_and_save(driver):
    driver.get("https://www.jd.com/")
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".link-login"))
        )
        login_btn.click()
    except:
        print("⚠ 无法自动点击登录按钮，请手动登录")

    print("👉 请手动完成京东登录（扫码/账号登录），完成后按 Enter 保存 cookies")
    input("👉 登录完成后按 Enter: ")

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nickname"))
        )
        print("✅ 登录成功")
        save_cookies(driver, COOKIE_FILE)
        return True
    except TimeoutException:
        print("❌ 登录验证失败")
        return False

def use_cookies_and_search(driver, keyword):
    encoded_keyword = urllib.parse.quote(keyword)
    search_url = f"https://search.jd.com/Search?keyword={encoded_keyword}"
    driver.get(search_url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".gl-item"))
        )
        print("✅ 搜索结果加载完成")
        return True
    except TimeoutException:
        print("❌ 搜索超时或页面结构变化")
        return False

def scroll_page(driver):
    print("📜 滚动页面加载更多商品...")
    last_count = 0
    for _ in range(20):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
        if len(items) == last_count:
            break
        last_count = len(items)
    print(f"✅ 页面滚动完成，共加载 {last_count} 个商品")

def parse_products(driver):
    products = []
    items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
    print(f"🔍 找到 {len(items)} 个商品")
    for index, item in enumerate(items):
        try:
            title_elem = item.find_element(By.CSS_SELECTOR, ".p-name em")
            title = title_elem.text.strip() or title_elem.get_attribute("title")
            price = item.find_element(By.CSS_SELECTOR, ".p-price strong").text.strip()
            try:
                shop = item.find_element(By.CSS_SELECTOR, ".p-shop a").text.strip()
            except NoSuchElementException:
                shop = "京东自营"
            try:
                comment = item.find_element(By.CSS_SELECTOR, ".p-commit strong").text.strip()
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
                print(f"🔄 已解析 {index + 1}/{len(items)} 个商品")
        except Exception as e:
            print(f"⚠ 解析商品 {index + 1} 出错: {str(e)}")
    print(f"✅ 完成解析 {len(products)} 个商品")
    return products

def save_to_csv(products, filename):
    if not products:
        print("⚠ 没有商品数据可保存")
        return
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "shop", "comment", "link"])
        writer.writeheader()
        writer.writerows(products)
    print(f"💾 成功保存 {len(products)} 条数据到 {filename}")

def main():
    print("=" * 50)
    print("🚀 京东商品爬虫启动")
    print("=" * 50)

    driver = init_driver()
    try:
        login_success = False
        if os.path.exists(COOKIE_FILE):
            print("🔑 尝试加载 cookies")
            login_success = load_cookies(driver, COOKIE_FILE)
        if not login_success:
            print("🔑 需要手动登录")
            if not manual_login_and_save(driver):
                print("❌ 登录失败，退出程序")
                return

        if use_cookies_and_search(driver, SEARCH_KEYWORD):
            scroll_page(driver)
            products = parse_products(driver)
            save_to_csv(products, OUTPUT_FILE)
        else:
            print("❌ 搜索失败，程序终止")

    except Exception as e:
        print(f"❌ 程序出错: {str(e)}")
    finally:
        driver.quit()
        print("🛑 浏览器已关闭")
        print("=" * 50)
        print("🏁 程序执行完成")
        print("=" * 50)

if __name__ == "__main__":
    main()
