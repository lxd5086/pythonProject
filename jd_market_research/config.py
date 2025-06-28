
import os
import logging
from typing import List, Tuple

# 全局配置
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")
BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))
PERSISTENCE_STRATEGY: str = 'cookie'
USER_PROFILE_PATH: str = os.path.join(BASE_DIR, 'JDProfile')
COOKIE_FILE_PATH: str = os.path.join(BASE_DIR, 'jd_cookies.json')

def get_user_input() -> Tuple[str, float, float, List[str], int]:
    """获取用户输入的关键词、价格范围、品牌和页数"""
    logging.info("获取用户输入...")
    search_keyword: str = input("请输入搜索关键词（如‘笔记本电脑 联想’）：")
    try:
        price_min: float = float(input("请输入最低价格（如 3000）："))
        price_max: float = float(input("请输入最高价格（如 8000）："))
    except ValueError:
        logging.error("价格必须为数字")
        raise ValueError("请输入有效的价格")
    brands: List[str] = [brand.strip() for brand in input("请输入品牌（多个品牌用逗号分隔，如‘联想,戴尔,惠普’）：").split(',')]
    while True:
        try:
            pages: int = int(input("请输入想爬取的页数（例如，3 表示爬取 3 页）："))
            if pages < 1:
                print("页数必须为正整数，请重新输入。")
                continue
            return search_keyword, price_min, price_max, brands, pages
        except ValueError:
            print("请输入有效的数字，例如 3。")
