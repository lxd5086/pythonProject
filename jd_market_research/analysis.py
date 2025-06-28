import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from .config import BASE_DIR

def analyze_data(products, brands):
    """分析价格分布和品牌占比，生成可视化"""
    if not products:
        logging.warning("无数据可分析")
        return
    df = pd.DataFrame(products)
    # 价格直方图
    plt.figure(figsize=(10, 6))
    sns.histplot(df["price"], bins=20, kde=True)
    plt.title("Price Distribution of Laptops (3000-8000 CNY)")
    plt.xlabel("Price (CNY)")
    plt.ylabel("Count")
    plt.savefig(os.path.join(BASE_DIR, "price_distribution.png"))
    plt.close()
    # 品牌占比饼图
    df["brand"] = df["title"].apply(lambda x: next((b for b in brands if b.lower() in x.lower()), "Other"))
    brand_counts = df["brand"].value_counts()
    plt.figure(figsize=(8, 8))
    plt.pie(brand_counts, labels=brand_counts.index, autopct='%1.1f%%')
    plt.title("Brand Distribution of Laptops")
    plt.savefig(os.path.join(BASE_DIR, "brand_distribution.png"))
    plt.close()
    # 促销统计
    promotion_counts = df["promotion"].value_counts().to_dict()
    logging.info(f"促销类型统计：{promotion_counts}")
