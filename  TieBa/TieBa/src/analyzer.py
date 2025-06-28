# src/analyzer.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import jieba.analyse
from collections import Counter
import json
import os
from datetime import datetime
import re
import config

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class TiebaAnalyzer:
	def __init__(self):
		self.processed_data_path = config.PROCESSED_DATA_PATH
		self.figures_dir = config.FIGURES_DIR
		self.reports_dir = config.REPORTS_DIR
		self.tieba_name = config.TIEBA_NAME

		# 确保输出目录存在
		os.makedirs(self.figures_dir, exist_ok=True)
		os.makedirs(self.reports_dir, exist_ok=True)

		self.df = None
		self.stats = None

	def load_data(self):
		"""加载处理后的数据"""
		try:
			print(f"加载数据: {self.processed_data_path}")
			self.df = pd.read_csv(self.processed_data_path, encoding='utf-8-sig')

			# 加载统计信息
			stats_path = self.processed_data_path.replace('.csv', '_stats.json')
			if os.path.exists(stats_path):
				with open(stats_path, 'r', encoding='utf-8') as f:
					self.stats = json.load(f)

			print(f"数据加载成功，记录数: {len(self.df)}")
			return True
		except Exception as e:
			print(f"数据加载失败: {e}")
			return False

	def content_length_analysis(self):
		"""内容长度分析"""
		if 'content_length' not in self.df.columns:
			print("缺少content_length字段，跳过内容长度分析")
			return

		print("进行内容长度分析...")

		fig, axes = plt.subplots(2, 2, figsize=(15, 12))
		fig.suptitle(f'{self.tieba_name}贴吧 - 内容长度分析', fontsize=16, fontweight='bold')

		# 内容长度分布直方图
		axes[0, 0].hist(self.df['content_length'], bins=50, alpha=0.7, color='skyblue', edgecolor='black')
		axes[0, 0].set_title('内容长度分布')
		axes[0, 0].set_xlabel('内容长度（字符数）')
		axes[0, 0].set_ylabel('频次')
		axes[0, 0].grid(True, alpha=0.3)

		# 主帖vs回复的内容长度对比
		if 'type' in self.df.columns:
			post_data = self.df[self.df['type'] == '主帖']['content_length']
			reply_data = self.df[self.df['type'] == '回复']['content_length']

			axes[0, 1].boxplot([post_data, reply_data], labels=['主帖', '回复'])
			axes[0, 1].set_title('主帖vs回复内容长度对比')
			axes[0, 1].set_ylabel('内容长度（字符数）')
			axes[0, 1].grid(True, alpha=0.3)

		# 词数分布
		if 'word_count' in self.df.columns:
			axes[1, 0].hist(self.df['word_count'], bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
			axes[1, 0].set_title('词数分布')
			axes[1, 0].set_xlabel('词数')
			axes[1, 0].set_ylabel('频次')
			axes[1, 0].grid(True, alpha=0.3)

		# 长度统计表
		length_stats = self.df['content_length'].describe()
		stats_text = f"""内容长度统计:
平均长度: {length_stats['mean']:.1f}
中位数: {length_stats['50%']:.1f}
最大长度: {length_stats['max']:.0f}
最小长度: {length_stats['min']:.0f}
标准差: {length_stats['std']:.1f}"""

		axes[1, 1].text(0.1, 0.5, stats_text, fontsize=12, transform=axes[1, 1].transAxes,
						verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
		axes[1, 1].set_title('内容长度统计')
		axes[1, 1].axis('off')

		plt.tight_layout()

		# 保存图片
		fig_path = os.path.join(self.figures_dir, f'{self.tieba_name}_content_length_analysis.png')
		plt.savefig(fig_path, dpi=config.DPI, bbox_inches='tight', facecolor='white')
		plt.show()

		print(f"内容长度分析图已保存: {fig_path}")

	def user_activity_analysis(self):
		"""用户活跃度分析"""
		if 'username' not in self.df.columns:
			print("缺少username字段，跳过用户活跃度分析")
			return

		print("进行用户活跃度分析...")

		# 用户发帖统计
		user_counts = self.df['username'].value_counts()

		fig, axes = plt.subplots(2, 2, figsize=(15, 12))
		fig.suptitle(f'{self.tieba_name}贴吧 - 用户活跃度分析', fontsize=16, fontweight='bold')

		# 用户发帖数分布
		axes[0, 0].hist(user_counts.values, bins=30, alpha=0.7, color='orange', edgecolor='black')
		axes[0, 0].set_title('用户发帖数分布')
		axes[0, 0].set_xlabel('发帖数')
		axes[0, 0].set_ylabel('用户数')
		axes[0, 0].grid(True, alpha=0.3)

		# 最活跃用户TOP10
		top_users = user_counts.head(10)
		axes[0, 1].barh(range(len(top_users)), top_users.values, color='lightcoral')
		axes[0, 1].set_yticks(range(len(top_users)))
		axes[0, 1].set_yticklabels(top_users.index, fontsize=10)
		axes[0, 1].set_title('最活跃用户TOP10')
		axes[0, 1].set_xlabel('发帖数')
		axes[0, 1].grid(True, alpha=0.3)

		# 用户活跃度分级
		activity_levels = pd.cut(user_counts.values,
								 bins=[0, 1, 3, 5, 10, float('inf')],
								 labels=['仅1次', '2-3次', '4-5次', '6-10次', '10次以上'])
		activity_counts = activity_levels.value_counts()

		axes[1, 0].pie(activity_counts.values, labels=activity_counts.index,
					   autopct='%1.1f%%', startangle=90, colors=plt.cm.Set3.colors)
		axes[1, 0].set_title('用户活跃度分级')

		# 用户统计信息
		user_stats = f"""用户统计信息:
总用户数: {len(user_counts)}
平均发帖数: {user_counts.mean():.1f}
最多发帖数: {user_counts.max()}
单次发帖用户: {sum(user_counts == 1)}
活跃用户(>3帖): {sum(user_counts > 3)}"""

		axes[1, 1].text(0.1, 0.5, user_stats, fontsize=12, transform=axes[1, 1].transAxes,
						verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
		axes[1, 1].set_title('用户统计')
		axes[1, 1].axis('off')

		plt.tight_layout()

		# 保存图片
		fig_path = os.path.join(self.figures_dir, f'{self.tieba_name}_user_activity_analysis.png')
		plt.savefig(fig_path, dpi=config.DPI, bbox_inches='tight', facecolor='white')
		plt.show()

		print(f"用户活跃度分析图已保存: {fig_path}")

	def word_frequency_analysis(self):
		"""词频分析"""
		if 'words' not in self.df.columns:
			print("缺少words字段，跳过词频分析")
			return

		print("进行词频分析...")

		# 获取所有词语
		all_words = []
		for words_str in self.df['words']:
			if pd.notna(words_str) and words_str.strip():
				try:
					# 尝试解析为列表（如果是字符串格式的列表）
					if words_str.startswith('[') and words_str.endswith(']'):
						words_list = eval(words_str)
					else:
						words_list = words_str.split(',')

					if isinstance(words_list, list):
						all_words.extend([word.strip().strip("'\"") for word in words_list if word.strip()])
				except:
					continue

		if not all_words:
			print("没有找到有效的词语数据")
			return

		# 词频统计
		word_freq = Counter(all_words)
		top_words = word_freq.most_common(50)

		fig, axes = plt.subplots(2, 2, figsize=(15, 12))
		fig.suptitle(f'{self.tieba_name}贴吧 - 词频分析', fontsize=16, fontweight='bold')

		# 词频分布柱状图（TOP20）
		top_20 = word_freq.most_common(20)
		words, freqs = zip(*top_20)

		axes[0, 0].barh(range(len(words)), freqs, color='steelblue')
		axes[0, 0].set_yticks(range(len(words)))
		axes[0, 0].set_yticklabels(words, fontsize=10)
		axes[0, 0].set_title('高频词TOP20')
		axes[0, 0].set_xlabel('频次')
		axes[0, 0].grid(True, alpha=0.3)

		# 词频分布直方图
		freq_values = list(word_freq.values())
		axes[0, 1].hist(freq_values, bins=30, alpha=0.7, color='green', edgecolor='black')
		axes[0, 1].set_title('词频分布')
		axes[0, 1].set_xlabel('词频')
		axes[0, 1].set_ylabel('词数')
		axes[0, 1].grid(True, alpha=0.3)

		# 生成词云
		try:
			# 创建词云字典
			wordcloud_dict = dict(word_freq.most_common(config.MAX_WORD_COUNT))

			# 创建词云对象
			wordcloud = WordCloud(
				width=800, height=400,
				background_color='white',
				font_path='simhei.ttf',  # 如果没有字体文件，会使用默认字体
				max_words=config.MAX_WORD_COUNT,
				colormap='viridis',
				relative_scaling=0.5,
				random_state=42
			).generate_from_frequencies(wordcloud_dict)

			axes[1, 0].imshow(wordcloud, interpolation='bilinear')
			axes[1, 0].set_title('词云图')
			axes[1, 0].axis('off')

		except Exception as e:
			print(f"生成词云失败: {e}")
			axes[1, 0].text(0.5, 0.5, '词云生成失败\n请检查字体配置',
							ha='center', va='center', transform=axes[1, 0].transAxes)
			axes[1, 0].set_title('词云图')

		# 词频统计信息
		vocab_stats = f"""词汇统计信息:
总词数: {len(all_words):,}
独特词汇: {len(word_freq):,}
平均词频: {np.mean(list(word_freq.values())):.1f}
最高词频: {max(word_freq.values())}
单次出现词: {sum(1 for f in word_freq.values() if f == 1):,}"""

		axes[1, 1].text(0.1, 0.5, vocab_stats, fontsize=12, transform=axes[1, 1].transAxes,
						verticalalignment='center', bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
		axes[1, 1].set_title('词汇统计')
		axes[1, 1].axis('off')

		plt.tight_layout()

		# 保存图片
		fig_path = os.path.join(self.figures_dir, f'{self.tieba_name}_word_frequency_analysis.png')
		plt.savefig(fig_path, dpi=config.DPI, bbox_inches='tight', facecolor='white')
		plt.show()

		print(f"词频分析图已保存: {fig_path}")

		# 保存词频数据
		word_freq_path = os.path.join(self.reports_dir, f'{self.tieba_name}_word_frequency.json')
		with open(word_freq_path, 'w', encoding='utf-8') as f:
			json.dump(dict(top_words), f, ensure_ascii=False, indent=2)
		print(f"词频数据已保存: {word_freq_path}")

	def post_type_analysis(self):
		"""帖子类型分析"""
		if 'type' not in self.df.columns:
			print("缺少type字段，跳过帖子类型分析")
			return

		print("进行帖子类型分析...")

		type_counts = self.df['type'].value_counts()

		fig, axes = plt.subplots(1, 2, figsize=(12, 5))
		fig.suptitle(f'{self.tieba_name}贴吧 - 帖子类型分析', fontsize=16, fontweight='bold')

		# 饼图
		axes[0].pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%',
					startangle=90, colors=['lightblue', 'lightcoral'])
		axes[0].set_title('帖子类型分布')

		# 柱状图
		axes[1].bar(type_counts.index, type_counts.values, color=['lightblue', 'lightcoral'])
		axes[1].set_title('帖子类型数量')
		axes[1].set_ylabel('数量')
		for i, v in enumerate(type_counts.values):
			axes[1].text(i, v + max(type_counts.values) * 0.01, str(v), ha='center', va='bottom')

		plt.tight_layout()

		# 保存图片
		fig_path = os.path.join(self.figures_dir, f'{self.tieba_name}_post_type_analysis.png')
		plt.savefig(fig_path, dpi=config.DPI, bbox_inches='tight', facecolor='white')
		plt.show()

		print(f"帖子类型分析图已保存: {fig_path}")

	def keyword_analysis(self):
		"""关键词分析"""
		if 'keywords' not in self.df.columns:
			print("缺少keywords字段，跳过关键词分析")
			return

		print("进行关键词分析...")

		# 提取所有关键词
		all_keywords = []
		for keywords_str in self.df['keywords']:
			if pd.notna(keywords_str) and keywords_str.strip():
				try:
					# 解析关键词（通常是带权重的元组列表）
					if keywords_str.startswith('[') and keywords_str.endswith(']'):
						keywords_list = eval(keywords_str)
						for item in keywords_list:
							if isinstance(item, tuple) and len(item) >= 2:
								all_keywords.append((item[0], item[1]))
							elif isinstance(item, str):
								all_keywords.append((item, 1.0))
				except:
					continue

		if not all_keywords:
			print("没有找到有效的关键词数据")
			return

		# 关键词频次统计
		keyword_freq = {}
		for keyword, weight in all_keywords:
			if keyword in keyword_freq:
				keyword_freq[keyword] += weight
			else:
				keyword_freq[keyword] = weight

		# 排序获取top关键词
		top_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)[:20]

		fig, axes = plt.subplots(1, 2, figsize=(15, 6))
		fig.suptitle(f'{self.tieba_name}贴吧 - 关键词分析', fontsize=16, fontweight='bold')

		# 关键词权重柱状图
		keywords, weights = zip(*top_keywords)
		axes[0].barh(range(len(keywords)), weights, color='purple', alpha=0.7)
		axes[0].set_yticks(range(len(keywords)))
		axes[0].set_yticklabels(keywords, fontsize=10)
		axes[0].set_title('关键词权重TOP20')
		axes[0].set_xlabel('权重')
		axes[0].grid(True, alpha=0.3)

		# 关键词词云
		try:
			wordcloud_dict = dict(top_keywords[:config.MAX_WORD_COUNT])
			wordcloud = WordCloud(
				width=600, height=400,
				background_color='white',
				font_path='simhei.ttf',
				max_words=50,
				colormap='plasma',
				relative_scaling=0.5,
				random_state=42
			).generate_from_frequencies(wordcloud_dict)

			axes[1].imshow(wordcloud, interpolation='bilinear')
			axes[1].set_title('关键词云')
			axes[1].axis('off')
		except Exception as e:
			print(f"生成关键词云失败: {e}")
			axes[1].text(0.5, 0.5, '关键词云生成失败', ha='center', va='center', transform=axes[1].transAxes)
			axes[1].set_title('关键词云')

		plt.tight_layout()

		# 保存图片
		fig_path = os.path.join(self.figures_dir, f'{self.tieba_name}_keyword_analysis.png')
		plt.savefig(fig_path, dpi=config.DPI, bbox_inches='tight', facecolor='white')
		plt.show()

		print(f"关键词分析图已保存: {fig_path}")

	def generate_summary_report(self):
		"""生成总结报告"""
		print("生成总结报告...")

		report = []
		report.append(f"# {self.tieba_name}贴吧数据分析报告")
		report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
		report.append(f"\n## 1. 数据概览")

		if self.stats:
			report.append(f"- 总记录数: {self.stats.get('total_records', 'N/A'):,}")
			report.append(f"- 主帖数量: {self.stats.get('post_count', 'N/A'):,}")
			report.append(f"- 回复数量: {self.stats.get('reply_count', 'N/A'):,}")
			report.append(f"- 独特用户数: {self.stats.get('unique_users', 'N/A'):,}")
			report.append(
				f"- 平均内容长度: {self.stats.get('avg_content_length', 'N/A'):.1f}字符" if 'avg_content_length' in self.stats else "")
			report.append(f"- 总词数: {self.stats.get('total_words', 'N/A'):,}")
			report.append(f"- 独特词汇数: {self.stats.get('total_unique_words', 'N/A'):,}")

		report.append(f"\n## 2. 内容分析")
		if 'content_length' in self.df.columns:
			length_stats = self.df['content_length'].describe()
			report.append(f"- 内容长度中位数: {length_stats['50%']:.0f}字符")
			report.append(f"- 最长内容: {length_stats['max']:.0f}字符")
			report.append(f"- 最短内容: {length_stats['min']:.0f}字符")

		report.append(f"\n## 3. 用户活跃度")
		if 'username' in self.df.columns:
			user_counts = self.df['username'].value_counts()
			report.append(f"- 平均每用户发帖: {user_counts.mean():.1f}次")
			report.append(f"- 最活跃用户发帖: {user_counts.max()}次")
			report.append(f"- 仅发1帖用户比例: {(sum(user_counts == 1) / len(user_counts) * 100):.1f}%")

		report.append(f"\n## 4. 高频词汇")
		if self.stats and 'top_words' in self.stats:
			report.append("前10个高频词:")
			for i, (word, freq) in enumerate(list(self.stats['top_words'].items())[:10], 1):
				report.append(f"{i}. {word}: {freq}次")

		report.append(f"\n## 5. 分析结论")
		report.append(f"基于对{self.tieba_name}贴吧的数据分析，我们可以得出以下结论:")

		# 根据数据特征生成结论
		if self.stats:
			post_reply_ratio = self.stats.get('reply_count', 0) / max(self.stats.get('post_count', 1), 1)
			report.append(
				f"- 平均每个主帖获得 {post_reply_ratio:.1f} 个回复，显示了{'较高' if post_reply_ratio > 5 else '一般'}的互动水平")

			if 'unique_users' in self.stats and 'total_records' in self.stats:
				participation_rate = self.stats['unique_users'] / self.stats['total_records']
				report.append(
					f"- 用户参与度{'较高' if participation_rate > 0.3 else '中等'}，{'社区活跃度良好' if participation_rate > 0.3 else '有提升空间'}")

		report.append(f"\n---")
		report.append(f"报告生成完毕。详细图表请查看 figures/ 目录。")

		# 保存报告
		report_content = '\n'.join(report)
		report_path = os.path.join(self.reports_dir, f'{self.tieba_name}_analysis_report.md')

		with open(report_path, 'w', encoding='utf-8') as f:
			f.write(report_content)

		print(f"分析报告已保存: {report_path}")
		print("\n" + "=" * 50)
		print("报告预览:")
		print("=" * 50)
		print(report_content)

		return report_content

	def run_all_analysis(self):
		"""执行所有分析"""
		print("--- [分析模块] 开始分析 ---")

		# 加载数据
		if not self.load_data():
			print("数据加载失败，无法进行分析")
			return

		if self.df is None or len(self.df) == 0:
			print("没有可分析的数据")
			return

		try:
			# 执行各项分析
			self.content_length_analysis()
			self.user_activity_analysis()
			self.word_frequency_analysis()
			self.post_type_analysis()
			self.keyword_analysis()

			# 生成总结报告
			self.generate_summary_report()

			print("--- [分析模块] 所有分析完成 ---")

		except Exception as e:
			print(f"分析过程中发生错误: {e}")

	def run_single_analysis(self, analysis_type):
		"""执行单个分析"""
		if not self.load_data():
			return

		analysis_methods = {
			'content': self.content_length_analysis,
			'user': self.user_activity_analysis,
			'word': self.word_frequency_analysis,
			'type': self.post_type_analysis,
			'keyword': self.keyword_analysis,
			'report': self.generate_summary_report
		}

		if analysis_type in analysis_methods:
			analysis_methods[analysis_type]()
		else:
			print(f"不支持的分析类型: {analysis_type}")
			print(f"可用类型: {list(analysis_methods.keys())}")


# 使用示例
if __name__ == "__main__":
	# 确保目录存在
	config.ensure_directories()

	# 创建分析器实例
	analyzer = TiebaAnalyzer()

	# 执行所有分析
	analyzer.run_all_analysis()

	print("数据分析完成!")