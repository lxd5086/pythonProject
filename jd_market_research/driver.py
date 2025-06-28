import os
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from .config import BASE_DIR

def init_driver(strategy: str, profile_path: str = None) -> webdriver.Chrome:
    """初始化 Chrome 浏览器驱动"""
    logging.info("初始化Chrome浏览器驱动...")
    ua = UserAgent()
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--start-maximized')
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
