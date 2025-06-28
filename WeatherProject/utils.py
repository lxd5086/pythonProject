# utils.py - 工具函数

import json
import re
from datetime import datetime


class Utils:
	"""工具函数集合"""

	@staticmethod
	def extract_numbers(text):
		"""提取文本中的数字"""
		return re.findall(r'-?\d+', str(text))

	@staticmethod
	def safe_json_loads(text):
		"""安全的JSON解析"""
		try:
			return json.loads(text)
		except (json.JSONDecodeError, TypeError):
			return None

	@staticmethod
	def get_current_timestamp():
		"""获取当前时间戳"""
		return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	@staticmethod
	def print_section(title):
		"""打印分节标题"""
		print(f"\n{'=' * 20} {title} {'=' * 20}")

	@staticmethod
	def print_step(step, description):
		"""打印步骤信息"""
		print(f"步骤 {step}: {description}")

	@staticmethod
	def save_debug_file(content, filename, mode='w'):
		"""保存调试文件"""
		try:
			with open(filename, mode, encoding='utf-8') as f:
				if isinstance(content, (dict, list)):
					json.dump(content, f, ensure_ascii=False, indent=2)
				else:
					f.write(content)
			print(f"调试文件已保存: {filename}")
			return True
		except Exception as e:
			print(f"保存调试文件失败: {e}")
			return False

	@staticmethod
	def load_debug_file(filename, is_json=False):
		"""加载调试文件"""
		try:
			with open(filename, 'r', encoding='utf-8') as f:
				if is_json:
					return json.load(f)
				else:
					return f.read()
		except FileNotFoundError:
			print(f"调试文件不存在: {filename}")
			return None
		except Exception as e:
			print(f"加载调试文件失败: {e}")
			return None


# 测试工具函数
if __name__ == "__main__":
	utils = Utils()

	# 测试数字提取
	test_text = "温度：25°C，湿度：60%"
	numbers = utils.extract_numbers(test_text)
	print(f"提取数字: {numbers}")

	# 测试JSON解析
	test_json = '{"temp": 25, "weather": "晴"}'
	parsed = utils.safe_json_loads(test_json)
	print(f"JSON解析: {parsed}")

	# 测试时间戳
	timestamp = utils.get_current_timestamp()
	print(f"当前时间: {timestamp}")

	# 测试打印函数
	utils.print_section("测试")
	utils.print_step(1, "这是一个测试步骤")