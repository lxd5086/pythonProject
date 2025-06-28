# src/data_cleaner.py

import pandas as pd
import re
import json
import jieba
import jieba.posseg as pseg
from collections import Counter
import config
import os

class TiebaDataCleaner:
	def __init__(self):
		self.raw_data_path = config.RAW_DATA_PATH
		self.json_data_path = config.JSON_DATA_PATH
		self.processed_data_path = config.PROCESSED_DATA_PATH
		self.stopwords_path = config.STOPWORDS_PATH
		self.custom_dict_path = config.CUSTOM_DICT_PATH

		# 加载停用词
		self.stopwords = self.load_stopwords()

		# 加载自定义词典
		self.load_custom_dict()

	def load_stopwords(self):
		"""加载停用词表"""
		stopwords = set()

		# 默认停用词
		default_stopwords = [
			'的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', '一', '一个',
			'上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好',
			'自己', '这', '当', '下', '能', '什么', '过', '如果', '然后', '怎么', '现在',
			'知道', '就是', '还', '因为', '这个', '中', '可以', '对', '里', '如', '得',
			'从', '以', '时', '地', '们', '用', '于', '等', '但', '与', '及', '而',
			'或', '之', '其', '被', '做', '成', '来', '让', '把', '给', '对于', '关于',
			'根据', '按照', '通过', '由于', '出现', '产生', '形成', '具有', '进行',
			'实现', '完成', '开始', '结束', '发生', '存在', '包含', '需要', '应该',
			'可能', '必须', '已经', '正在', '将要', '曾经', '刚刚', '马上', '立即',
			'经常', '总是', '从来', '绝不', '几乎', '差不多', '大概', '也许', '可能'
		]
		stopwords.update(default_stopwords)

		# 尝试从文件加载停用词
		try:
			if os.path.exists(self.stopwords_path):
				with open(self.stopwords_path, 'r', encoding='utf-8') as f:
					for line in f:
						word = line.strip()
						if word:
							stopwords.add(word)
				print(f"从文件加载停用词: {len(stopwords)} 个")
			else:
				# 创建默认停用词文件
				self.create_default_stopwords_file(default_stopwords)
				print(f"使用默认停用词: {len(stopwords)} 个")
		except Exception as e:
			print(f"加载停用词失败: {e}")

		return stopwords

	def create_default_stopwords_file(self, stopwords_list):
		"""创建默认停用词文件"""
		try:
			with open(self.stopwords_path, 'w', encoding='utf-8') as f:
				for word in stopwords_list:
					f.write(word + '\n')
			print(f"创建默认停用词文件: {self.stopwords_path}")
		except Exception as e:
			print(f"创建停用词文件失败: {e}")

	def load_custom_dict(self):
		"""加载自定义词典"""
		try:
			if os.path.exists(self.custom_dict_path):
				jieba.load_userdict(self.custom_dict_path)
				print("加载自定义词典成功")
			else:
				# 创建默认自定义词典
				self.create_default_custom_dict()
		except Exception as e:
			print(f"加载自定义词典失败: {e}")

	def create_default_custom_dict(self):
		"""创建默认自定义词典"""
		try:
			custom_words = [
				'Python 99 n',
				'机器学习 99 n',
				'深度学习 99 n',
				'人工智能 99 n',
				'数据分析 99 n',
				'爬虫 99 n',
				'Web开发 99 n',
				'编程 99 n',
				'算法 99 n',
				'框架 99 n'
			]

			with open(self.custom_dict_path, 'w', encoding='utf-8') as f:
				for word in custom_words:
					f.write(word + '\n')

			jieba.load_userdict(self.custom_dict_path)
			print(f"创建默认自定义词典: {self.custom_dict_path}")
		except Exception as e:
			print(f"创建自定义词典失败: {e}")

	def clean_text(self, text):
		"""清理文本内容"""
		if not text or not isinstance(text, str):
			return ""

		# 去除HTML标签
		text = re.sub(r'<[^>]+>', '', text)

		# 去除网址
		text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)

		# 去除邮箱
		text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)

		# 去除电话号码
		text = re.sub(r'\b\d{3,4}-?\d{7,8}\b', '', text)
		text = re.sub(r'\b1[3-9]\d{9}\b', '', text)

		# 去除特殊字符，保留中文、英文、数字
		text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s]', ' ', text)

		# 去除多余空格
		text = re.sub(r'\s+', ' ', text)

		# 去除首尾空格
		text = text.strip()

		return text

	def segment_text(self, text):
		"""文本分词"""
		if not text:
			return []

		# 使用jieba分词
		words = jieba.cut(text, cut_all=False)

		# 过滤词语
		filtered_words = []
		for word in words:
			word = word.strip()
			# 过滤条件：长度大于等于最小长度，不在停用词中，不是纯数字或纯英文字母
			if (len(word) >= config.MIN_WORD_LENGTH and
					word not in self.stopwords and
					not word.isdigit() and
					not word.isalpha() and
					'\u4e00' <= word[0] <= '\u9fff'):  # 确保是中文
				filtered_words.append(word)

		return filtered_words

	def extract_keywords(self, text, top_k=10):
		"""提取关键词"""
		import jieba.analyse

		if not text:
			return []

		try:
			# 使用TF-IDF提取关键词
			keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=True)
			return keywords
		except Exception as e:
			print(f"关键词提取失败: {e}")
			return []

	def process_dataframe(self, df):
		"""处理DataFrame数据"""
		print("开始处理数据...")

		processed_df = df.copy()

		# 清理内容字段
		if 'content' in processed_df.columns:
			print("清理文本内容...")
			processed_df['cleaned_content'] = processed_df['content'].apply(self.clean_text)

			# 分词
			print("进行文本分词...")
			processed_df['words'] = processed_df['cleaned_content'].apply(self.segment_text)

			# 计算文本长度
			processed_df['content_length'] = processed_df['cleaned_content'].apply(len)
			processed_df['word_count'] = processed_df['words'].apply(len)

			# 提取关键词
			print("提取关键词...")
			processed_df['keywords'] = processed_df['cleaned_content'].apply(lambda x: self.extract_keywords(x, 5))

		# 清理其他文本字段
		text_columns = ['post_title', 'username']
		for col in text_columns:
			if col in processed_df.columns:
				processed_df[f'cleaned_{col}'] = processed_df[col].apply(self.clean_text)

		# 去除空内容的行
		processed_df = processed_df[processed_df['cleaned_content'].str.len() > 0]

		print(f"数据处理完成，保留 {len(processed_df)} 条记录")
		return processed_df

	def get_word_frequency(self, df):
		"""获取词频统计"""
		if 'words' not in df.columns:
			return Counter()

		all_words = []
		for words_list in df['words']:
			if isinstance(words_list, list):
				all_words.extend(words_list)

		word_freq = Counter(all_words)

		# 过滤低频词
		filtered_freq = {word: freq for word, freq in word_freq.items()
						 if freq >= config.MIN_WORD_FREQ}

		return Counter(filtered_freq)

	def generate_statistics(self, df):
		"""生成数据统计信息"""
		stats = {}

		# 基本统计
		stats['total_records'] = len(df)
		stats['post_count'] = len(df[df['type'] == '主帖']) if 'type' in df.columns else 0
		stats['reply_count'] = len(df[df['type'] == '回复']) if 'type' in df.columns else 0

		# 内容统计
		if 'content_length' in df.columns:
			stats['avg_content_length'] = df['content_length'].mean()
			stats['max_content_length'] = df['content_length'].max()
			stats['min_content_length'] = df['content_length'].min()

		if 'word_count' in df.columns:
			stats['avg_word_count'] = df['word_count'].mean()
			stats['total_words'] = df['word_count'].sum()

		# 用户统计
		if 'username' in df.columns:
			stats['unique_users'] = df['username'].nunique()
			stats['most_active_users'] = df['username'].value_counts().head(10).to_dict()

		# 词频统计
		word_freq = self.get_word_frequency(df)
		stats['total_unique_words'] = len(word_freq)
		stats['top_words'] = dict(word_freq.most_common(20))

		return stats

	def run(self):
		"""执行数据清理的主函数"""
		print("--- [数据清理模块] 开始处理 ---")

		try:
			# 检查原始数据文件是否存在
			import os
			if not os.path.exists(self.raw_data_path):
				print(f"原始数据文件不存在: {self.raw_data_path}")
				return None

			# 读取原始数据
			print(f"读取原始数据: {self.raw_data_path}")
			df = pd.read_csv(self.raw_data_path, encoding='utf-8-sig')
			print(f"原始数据记录数: {len(df)}")

			# 处理数据
			processed_df = self.process_dataframe(df)

			# 生成统计信息
			stats = self.generate_statistics(processed_df)

			# 保存处理后的数据
			processed_df.to_csv(self.processed_data_path, index=False, encoding='utf-8-sig')
			print(f"处理后数据已保存: {self.processed_data_path}")

			# 保存统计信息
			stats_path = self.processed_data_path.replace('.csv', '_stats.json')
			with open(stats_path, 'w', encoding='utf-8') as f:
				json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
			print(f"统计信息已保存: {stats_path}")

			# 打印基本统计信息
			print("\n--- 数据统计信息 ---")
			print(f"总记录数: {stats['total_records']}")
			print(f"主帖数: {stats['post_count']}")
			print(f"回复数: {stats['reply_count']}")
			print(f"独特用户数: {stats.get('unique_users', 'N/A')}")
			print(
				f"平均内容长度: {stats.get('avg_content_length', 'N/A'):.2f}" if 'avg_content_length' in stats else "")
			print(f"总词数: {stats.get('total_words', 'N/A')}")
			print(f"独特词汇数: {stats['total_unique_words']}")

			print("--- [数据清理模块] 处理完成 ---")
			return processed_df, stats

		except Exception as e:
			print(f"数据清理过程中发生错误: {e}")
			return None, None


# 使用示例
if __name__ == "__main__":
	# 确保目录存在
	config.ensure_directories()

	# 创建数据清理器实例
	cleaner = TiebaDataCleaner()

	# 执行数据清理
	processed_data, stats = cleaner.run()

	if processed_data is not None:
		print("数据清理成功完成!")
	else:
		print("数据清理失败!")