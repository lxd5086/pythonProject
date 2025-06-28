import os
import csv
import sqlite3
import logging
from .config import BASE_DIR

def init_database():
    """初始化 SQLite 数据库"""
    try:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'jd_products.db'))
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS products
                     (title TEXT, price REAL, shop TEXT, comment TEXT, link TEXT, image_url TEXT, promotion TEXT)''')
        conn.commit()
        logging.info("数据库初始化成功")
        return conn
    except sqlite3.Error as e:
        logging.error(f"数据库初始化失败: {e}")
        raise

def save_to_database(products, conn):
    """保存数据到 SQLite"""
    try:
        c = conn.cursor()
        for product in products:
            c.execute("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (product["title"], product["price"], product["shop"], product["comment"],
                       product["link"], product["image_url"], product["promotion"]))
        conn.commit()
        logging.info(f"成功保存 {len(products)} 条数据到数据库")
    except sqlite3.Error as e:
        logging.error(f"数据库保存失败: {e}")

def save_data(products: list, filename: str):
    """将数据保存到CSV文件"""
    if not products:
        logging.warning("没有爬取到任何数据，不创建文件。")
        return
    logging.info(f"共爬取 {len(products)} 条有效数据，准备写入文件 {filename}...")
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=["title", "price", "shop", "comment", "link", "image_url", "promotion"])
        writer.writeheader()
        writer.writerows(products)
    logging.info(f"数据保存成功！文件位于: {filename}")
