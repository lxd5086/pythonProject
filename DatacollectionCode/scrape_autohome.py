import requests
from bs4 import BeautifulSoup

# 目标 URL
url = "https://www.autohome.com.cn/price/levelid_9/x-x-x-x-1"

# 请求头
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Origin": "https://www.autohome.com.cn",
    "Referer": "https://www.autohome.com.cn/",
    "Sec-Ch-Ua": '"Microsoft Edge";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36 Edg/137.0.0.0",
    "Priority": "u=1, i"
}

# 发送请求
try:
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    response.encoding = 'utf-8'
except requests.RequestException as e:
    print(f"请求失败: {e}")
    exit(1)

# 解析 HTML
soup = BeautifulSoup(response.text, 'html.parser')

# 提取车辆名称
vehicle_elements = soup.select('a.tw-text-hover')
vehicle_names = [elem.get_text().strip() for elem in vehicle_elements if elem.get_text().strip()]

# 检查结果
if not vehicle_names:
    print("未找到车辆名称，可能是选择器错误或动态加载。")
    print("当前页面片段：")
    print(soup.prettify()[:1000])
    print("\n建议：")
    print("1. 确认选择器（F12 检查元素）")
    print("2. 使用 Selenium：")
    print("   from selenium import webdriver")
    print("   driver = webdriver.Chrome()")
    print("   driver.get('https://www.autohome.com.cn/price/levelid_9/x-x-x-x-1')")
    exit(1)

# 去重并保存
unique_vehicle_names = list(set(vehicle_names))
output_file = "suv_names.txt"

with open(output_file, 'w', encoding='utf-8') as f:
    for name in unique_vehicle_names:
        f.write(name + '\n')
        print(name)

print(f"\n共找到 {len(unique_vehicle_names)} 个车辆名称，已保存到 {output_file}")