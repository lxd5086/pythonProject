import requests
from bs4 import BeautifulSoup
import json
import os

# --- 1. 发送请求，获取页面 ---
url = 'https://movie.douban.com/subject/1889243/'
# 伪装成浏览器访问，防止被网站屏蔽
headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
	print("正在请求豆瓣电影页面...")
	response = requests.get(url, headers=headers)
	response.raise_for_status()  # 如果请求失败（如404、500等），会抛出异常
	print("页面请求成功！")

	# --- 2. 解析页面，提取演员信息 ---
	print("正在解析演员信息...")
	soup = BeautifulSoup(response.text, 'html.parser')

	# --- 代码修改处 ---
	# 旧的查找方式失效了，我们使用新的方式。
	# 演员信息现在位于 id="info" 的 div 中，每个主演都是一个带有 rel="v:starring" 属性的 a 标签。
	info_div = soup.find('div', id='info')

	actor_names = []
	if info_div:
		# 查找所有 rel="v:starring" 的 a 标签来获取主演列表
		actors = info_div.find_all('a', attrs={'rel': 'v:starring'})
		for actor in actors:
			actor_names.append(actor.get_text().strip())  # .strip() 用于移除可能存在的前后空格

	if actor_names:
		print(f"成功提取到 {len(actor_names)} 位演员信息。")
		print(actor_names)
	else:
		# 如果新的方法也失败了，会打印这条信息
		print("未找到演员信息，可能是页面结构已再次改变。")

	# --- 3. 准备文件路径并保存为 JSON 文件 ---
	if actor_names:  # 仅当成功提取到演员信息时才保存文件
		output_path = r'C:\code-python\pythonProject\DatacollectionCode\data'
		file_name = 'actors.json'
		full_path = os.path.join(output_path, file_name)

		print(f"准备将数据保存到: {full_path}")

		# 检查并创建目录（如果不存在）
		os.makedirs(output_path, exist_ok=True)

		# 写入 JSON 文件
		with open(full_path, 'w', encoding='utf-8') as f:
			# ensure_ascii=False 确保中文字符能被正确写入，而不是被转换成 ASCII 码
			json.dump(actor_names, f, ensure_ascii=False, indent=4)

		print("文件保存成功！")

except requests.exceptions.RequestException as e:
	print(f"请求页面时发生错误: {e}")
except Exception as e:
	print(f"处理过程中发生未知错误: {e}")