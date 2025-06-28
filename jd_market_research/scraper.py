
import time
import random
import urllib.parse
import logging
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, NoSuchWindowException
from .login import check_captcha

def scroll_page(driver: webdriver.Chrome, max_scrolls: int = 10) -> None:
    """滚动页面加载更多商品"""
    logging.info("滚动页面加载更多商品...")
    last_count = 0
    for i in range(max_scrolls):
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(4, 6))
            check_captcha(driver)
            items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
            if len(items) == last_count and i > 0:
                break
            last_count = len(items)
        except NoSuchWindowException:
            logging.error("浏览器窗口关闭，滚动失败")
            raise
    logging.info(f"滚动完成，共加载 {last_count} 个商品")

def search_and_scrape(driver: webdriver.Chrome, keyword: str, max_pages: int, price_min: float, price_max: float, brands: List[str]) -> List[Dict]:
    """执行搜索、滚动、解析和翻页"""
    logging.info(f"开始搜索关键词: '{keyword}'")
    for attempt in range(3):
        try:
            driver.get("https://www.jd.com/")
            time.sleep(random.uniform(2, 4))
            try:
                search_box = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "key"))
                )
                search_box.clear()
                for char in keyword:
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

    all_products: List[Dict] = []
    seen_titles = set()
    for page in range(1, max_pages + 1):
        logging.info(f"--- 正在爬取第 {page}/{max_pages} 页 ---")
        try:
            current_url = driver.current_url
            logging.info(f"当前页面 URL: {current_url}")
            scroll_page(driver)
            items = driver.find_elements(By.CSS_SELECTOR, ".gl-item")
            logging.info(f"本页找到 {len(items)} 个商品条目。")
            new_items = 0
            for item in items:
                try:
                    title_elem = item.find_element(By.CSS_SELECTOR, ".p-name em, .p-name a")
                    title = title_elem.text.strip()
                    if not title or title in seen_titles or not any(brand.lower() in title.lower() for brand in brands):
                        continue
                    price_elem = item.find_element(By.CSS_SELECTOR, ".p-price i, .p-price strong")
                    price = float(price_elem.text.strip().replace(',', ''))
                    if not (price_min <= price <= price_max):
                        continue
                    seen_titles.add(title)
                    link = item.find_element(By.CSS_SELECTOR, ".p-name a").get_attribute("href")
                    shop = item.find_element(By.CSS_SELECTOR, ".p-shop a, .p-shop span").text.strip() or "京东自营"
                    comment = item.find_element(By.CSS_SELECTOR, ".p-commit strong, .p-commit a").text.strip() or "0"
                    image_url = item.find_element(By.CSS_SELECTOR, ".p-img img").get_attribute("src") or ""
                    promotion = item.find_element(By.CSS_SELECTOR, ".p-promotion, .p-tag").text.strip() or "无"
                    all_products.append({
                        "title": title, "price": price, "shop": shop, "comment": comment,
                        "link": link, "image_url": image_url, "promotion": promotion
                    })
                    new_items += 1
                except (NoSuchElementException, ValueError):
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
                        expected_page = 2 * page + 1
                        WebDriverWait(driver, 10).until(
                            EC.url_contains(f"page={expected_page}")
                        )
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located((By.ID, "J_goodsList"))
                        )
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
