# 3_analyze_sentiment.py
# 最终版功能：对热门评论进行数据清洗和情感分析。

import json
import os
import re
from snownlp import SnowNLP

# ==================== 配置区 ====================
DATA_DIR = r'C:\code-python\pythonProject\DatacollectionCode\data'
JSON_FILENAME = 'interstellar_HOTTEST_reviews.json'
JSON_FULL_PATH = os.path.join(DATA_DIR, JSON_FILENAME)


# ==================== 主程序 ====================
def clean_text(text):
	"""文本清洗函数"""
	text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9，。！？]', '', text)
	text = re.sub(r'\s+', ' ', text).strip()
	return text


def analyze_hottest_sentiment():
	"""主分析函数"""
	print("--- 开始执行“热门评论”情感分析任务 ---")

	if not os.path.exists(JSON_FULL_PATH):
		print(f"错误：找不到数据文件 '{JSON_FULL_PATH}'。请先运行爬虫脚本。")
		return

	print("正在读取JSON文件...")
	with open(JSON_FULL_PATH, 'r', encoding='utf-8') as f:
		reviews = json.load(f)

	sentiments = {'positive': 0, 'neutral': 0, 'negative': 0}
	total_reviews = len(reviews)

	print(f"开始分析 {total_reviews} 条热门影评...")

	for i, review in enumerate(reviews):
		cleaned_text = clean_text(review['content'])
		if not cleaned_text: continue

		score = SnowNLP(cleaned_text).sentiments

		if score > 0.6:
			sentiments['positive'] += 1
		elif score < 0.4:
			sentiments['negative'] += 1
		else:
			sentiments['neutral'] += 1

		if (i + 1) % 10 == 0 or (i + 1) == total_reviews:
			print(f"已处理 {i + 1}/{total_reviews} 条...")

	print("\n================== 热门评论情感分析报告 ==================")
	print(f"总计分析影评数: {total_reviews}")
	print(f"  - 积极情感 (分数 > 0.6): {sentiments['positive']} 条")
	print(f"  - 中性情感 (0.4 <= 分数 <= 0.6): {sentiments['neutral']} 条")
	print(f"  - 消极情感 (分数 < 0.4): {sentiments['negative']} 条")

	if total_reviews > 0:
		pos_percent = (sentiments['positive'] / total_reviews) * 100
		print(f"\n积极评论占比: {pos_percent:.2f}%")
	print("==========================================================")
	print("--- 情感分析任务结束 ---")


if __name__ == '__main__':
	# 运行前请确保已安装 snownlp: pip install snownlp
	analyze_hottest_sentiment()