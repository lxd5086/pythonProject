import os
import time
import json
import logging
import random
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchWindowException
from .config import COOKIE_FILE_PATH

def check_captcha(driver: webdriver.Chrome) -> bool:
    """检查是否存在验证码页面"""
    try:
        if "captcha" in driver.current_url.lower() or "verify" in driver.page_source.lower():
            logging.warning("检测到验证码，请手动完成验证后按 Enter 继续...")
            input(">>> 完成验证码后按回车继续...")
            time.sleep(random.uniform(2, 4))
            return True
    except NoSuchWindowException:
        logging.error("浏览器窗口已关闭，尝试重新初始化...")
        raise
    return False

def is_logged_in(driver: webdriver.Chrome) -> bool:
    """检查是否已登录"""
    try:
        driver.get('https://www.jd.com/')
        time.sleep(random.uniform(2, 4))
        check_captcha(driver)
        driver.get('https://order.jd.com/center/list.action')
        check_captcha(driver)
        if 'login' in driver.current_url.lower() or 'passport' in driver.current_url.lower():
            return False
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".nickname, .jd_user, .user-info, .login-info"))
        )
        return True
    except (TimeoutException, NoSuchWindowException):
        return False

def handle_login(driver: webdriver.Chrome, strategy: str, cookie_path: str) -> None:
    """处理登录流程"""
    try:
        if strategy == 'cookie':
            if os.path.exists(cookie_path):
                logging.info(f"加载Cookies: {cookie_path}")
                driver.get("https://www.jd.com/")
                time.sleep(random.uniform(2, 4))
                with open(cookie_path, 'r', encoding='utf-8') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        logging.warning(f"添加 cookie 出错: {e}")
                driver.refresh()
                time.sleep(random.uniform(2, 4))
                if is_logged_in(driver):
                    logging.info("Cookie登录成功！")
                    return
            logging.warning("Cookie无效或不存在，需要手动登录。")
            driver.get("https://passport.jd.com/new/login.aspx")
            check_captcha(driver)
            input(">>> 登录成功后，请按回车继续...")
            check_captcha(driver)
            if is_logged_in(driver):
                logging.info("保存Cookies...")
                with open(cookie_path, 'w', encoding='utf-8') as f:
                    json.dump(driver.get_cookies(), f)
            else:
                raise Exception("登录失败")
    except NoSuchWindowException:
        logging.error("浏览器窗口意外关闭，程序终止")
        raise
