# 2_generate_wordcloud.py
# 最终版功能：读取热门评论数据，过滤停用词，生成词云。

import json
import os
import jieba
from wordcloud import WordCloud
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# ==================== 配置区 ====================
DATA_DIR = r'C:\code-python\pythonProject\DatacollectionCode\data'
JSON_FILENAME = 'interstellar_HOTTEST_reviews.json'
JSON_FULL_PATH = os.path.join(DATA_DIR, JSON_FILENAME)
FONT_PATH = 'C:/Windows/Fonts/simhei.ttf'


# ==================== 主程序 ====================
def create_hottest_wordcloud():
	print("\n--- 开始执行“热门评论”词云生成任务 ---")

	if not os.path.exists(JSON_FULL_PATH):
		print(f"错误：找不到数据文件 '{JSON_FULL_PATH}'。请先运行爬虫脚本。")
		return
	if not os.path.exists(FONT_PATH):
		print(f"错误：找不到字体文件 '{FONT_PATH}'。")
		return

	stopwords = {'的', '了', '是', '我', '你', '他', '她', '它', '也', '都', '就',
				 '一个', '这个', '那个', '我们', '你们', '他们', '她们', '它们',
				 '这部', '电影', '一部', '还是', '就是', '自己', '可以', '没有',
				 '什么', '这样', '那样', '如果', '觉得', '因为', '所以', '但是',
				 '展开', '影评', '可能', '有剧', '这篇', '全文'}

	print("正在读取并合并热门评论文本...")
	with open(JSON_FULL_PATH, 'r', encoding='utf-8') as f:
		reviews = json.load(f)
	text_corpus = " ".join([review['content'] for review in reviews])

	if not text_corpus.strip():
		print("错误：影评内容为空。");
		return

	print("正在进行中文分词并过滤停用词...")
	word_list = jieba.cut(text_corpus)
	filtered_words = [word for word in word_list if len(word) > 1 and word not in stopwords]
	processed_text = " ".join(filtered_words)

	print("正在生成词云...")
	wc = WordCloud(
		font_path=FONT_PATH, background_color='white',
		width=800, height=600, max_words=200, margin=2,
		collocations=False
	).generate(processed_text)

	print("词云生成完毕！正在显示图片...")
	plt.figure(figsize=(10, 8))
	plt.imshow(wc, interpolation='bilinear')
	plt.axis('off')
	plt.show()
	print("--- 词云任务结束 ---")


if __name__ == '__main__':
	create_hottest_wordcloud()