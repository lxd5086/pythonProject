# -*- coding: utf-8 -*-
"""
数据处理模块
负责数据加载、清洗、预处理等功能
"""

import pandas as pd
import numpy as np
import re
from typing import Dict, Tuple, Optional
import os
import warnings

warnings.filterwarnings('ignore')

class DataProcessor:
    """数据处理器"""

    def __init__(self, output_dir: str = 'cleaned_data'):
        """初始化处理器，设置输出目录"""
        self.raw_data = None
        self.cleaned_data = None
        self.stats = {}
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📊 Data processing output directory: {self.output_dir}")

    def load_data(self, file_path: str) -> bool:
        """加载CSV数据"""
        try:
            self.raw_data = pd.read_csv(file_path, encoding='utf-8-sig')
            print(f"✅ 成功加载 {len(self.raw_data)} 条原始数据")
            return True
        except Exception as e:
            print(f"❌ 数据加载失败: {e}")
            return False

    def clean_data(self) -> pd.DataFrame:
        """数据清洗和预处理"""
        if self.raw_data is None:
            raise ValueError("请先加载数据")

        print("🔄 正在进行数据清洗...")
        self.cleaned_data = self.raw_data.copy()

        # 1. 提取价格数字
        self.cleaned_data['price_numeric'] = self.cleaned_data['price'].apply(self._extract_price)

        # 2. 提取面积数字
        self.cleaned_data['area_numeric'] = self.cleaned_data['area'].apply(self._extract_area)

        # 3. 计算单价
        self.cleaned_data['price_per_sqm'] = (
            self.cleaned_data['price_numeric'] / self.cleaned_data['area_numeric']
        ).round(2)

        # 4. 解析户型信息
        layout_info = self.cleaned_data['layout'].apply(self._parse_layout)
        self.cleaned_data['bedrooms'] = [info['bedrooms'] for info in layout_info]
        self.cleaned_data['livingrooms'] = [info['livingrooms'] for info in layout_info]
        self.cleaned_data['total_rooms'] = [info['total_rooms'] for info in layout_info]

        # 5. 标准化朝向信息
        self.cleaned_data['orientation_clean'] = self.cleaned_data['orientation'].apply(self._standardize_orientation)

        # 6. 处理更新时间
        self.cleaned_data['update_category'] = self.cleaned_data['update_time'].apply(self._parse_update_time)

        # 7. 处理区域缺失值
        self.cleaned_data['district'] = self.cleaned_data['district'].replace('N/A', np.nan)
        self.cleaned_data['district'] = self.cleaned_data.apply(
            lambda row: self._extract_district_from_title(row['title']) if pd.isna(row['district']) else row['district'],
            axis=1
        )

        # 8. 清理异常值
        self._remove_outliers()

        # 9. 移除重复记录
        self.cleaned_data = self.cleaned_data.drop_duplicates(subset=['title', 'price', 'layout', 'area'], keep='first')

        # 保存清洗后的数据
        output_path = os.path.join(self.output_dir, 'cleaned_rental_data.csv')
        self.cleaned_data.to_csv(output_path, encoding='utf-8-sig', index=False)
        print(f"✅ 数据清洗完成，有效数据 {len(self.cleaned_data)} 条，保存至 {output_path}")

        return self.cleaned_data

    def _extract_price(self, price_str) -> Optional[float]:
        """提取价格数字"""
        if pd.isna(price_str):
            return np.nan

        # 处理价格区间，取中间值
        if '-' in str(price_str):
            numbers = re.findall(r'\d+', str(price_str))
            if len(numbers) >= 2:
                return (int(numbers[0]) + int(numbers[1])) / 2

        numbers = re.findall(r'\d+', str(price_str))
        return float(numbers[0]) if numbers else np.nan

    def _extract_area(self, area_str) -> Optional[float]:
        """提取面积数字"""
        if pd.isna(area_str):
            return np.nan

        # 处理面积区间，取中间值
        if '-' in str(area_str):
            numbers = re.findall(r'[\d.]+', str(area_str))
            if len(numbers) >= 2:
                return (float(numbers[0]) + float(numbers[1])) / 2

        numbers = re.findall(r'[\d.]+', str(area_str))
        return float(numbers[0]) if numbers else np.nan

    def _parse_layout(self, layout_str) -> Dict[str, int]:
        """解析户型信息"""
        if pd.isna(layout_str):
            return {'bedrooms': 0, 'livingrooms': 0, 'total_rooms': 0}

        bedroom_match = re.search(r'(\d+)室', str(layout_str))
        livingroom_match = re.search(r'(\d+)厅', str(layout_str))

        bedrooms = int(bedroom_match.group(1)) if bedroom_match else 0
        livingrooms = int(livingroom_match.group(1)) if livingroom_match else 0

        return {
            'bedrooms': bedrooms,
            'livingrooms': livingrooms,
            'total_rooms': bedrooms + livingrooms
        }

    def _standardize_orientation(self, orientation_str) -> str:
        """标准化朝向信息"""
        if pd.isna(orientation_str) or orientation_str == 'N/A':
            return '未知朝向'

        orientation_mapping = {
            '南': '南向', '北': '北向', '东': '东向', '西': '西向',
            '东南': '东南向', '西南': '西南向', '东北': '东北向', '西北': '西北向',
            '南北': '南北通透'
        }

        for key, value in orientation_mapping.items():
            if key in str(orientation_str):
                return value
        return '其他朝向'

    def _parse_update_time(self, time_str) -> str:
        """解析更新时间"""
        if pd.isna(time_str):
            return '未知'

        time_str = str(time_str).replace('维护', '')
        if '今天' in time_str:
            return '今天更新'
        elif '天前' in time_str:
            days = re.findall(r'(\d+)天前', time_str)
            return f"{days[0]}天前" if days else '最近更新'
        elif '个月前' in time_str:
            return '较早更新'
        else:
            return '未知'

    def _remove_outliers(self):
        """移除异常值"""
        numeric_columns = ['price_numeric', 'area_numeric', 'price_per_sqm']
        for col in numeric_columns:
            if col in self.cleaned_data.columns:
                Q1 = self.cleaned_data[col].quantile(0.01)
                Q99 = self.cleaned_data[col].quantile(0.99)
                self.cleaned_data = self.cleaned_data[
                    (self.cleaned_data[col] >= Q1) &
                    (self.cleaned_data[col] <= Q99)
                ]

    def get_basic_statistics(self) -> Dict:
        """获取基础统计信息"""
        if self.cleaned_data is None:
            raise ValueError("请先进行数据清洗")

        self.stats = {
            '数据概览': {
                '总房源数': len(self.cleaned_data),
                '平均租金': f"{self.cleaned_data['price_numeric'].mean():.0f} 元/月",
                '租金中位数': f"{self.cleaned_data['price_numeric'].median():.0f} 元/月",
                '平均面积': f"{self.cleaned_data['area_numeric'].mean():.1f} ㎡",
                '平均单价': f"{self.cleaned_data['price_per_sqm'].mean():.2f} 元/㎡/月"
            },
            '租金分布': {
                '最低租金': f"{self.cleaned_data['price_numeric'].min():.0f} 元/月",
                '最高租金': f"{self.cleaned_data['price_numeric'].max():.0f} 元/月",
                '租金标准差': f"{self.cleaned_data['price_numeric'].std():.0f} 元/月"
            },
            '户型分布': dict(self.cleaned_data['layout'].value_counts().head(10)),
            '朝向分布': dict(self.cleaned_data['orientation_clean'].value_counts()),
            '更新时间分布': dict(self.cleaned_data['update_category'].value_counts())
        }

        return self.stats

    def get_district_analysis(self) -> pd.DataFrame:
        """获取区域分析数据"""
        if self.cleaned_data is None:
            raise ValueError("请先进行数据清洗")

        district_stats = self.cleaned_data.groupby('district').agg({
            'price_numeric': ['count', 'mean', 'median'],
            'area_numeric': 'mean',
            'price_per_sqm': 'mean'
        }).round(2)

        district_stats.columns = ['房源数量', '平均租金', '租金中位数', '平均面积', '平均单价']
        district_stats = district_stats.sort_values('平均租金', ascending=False)

        return district_stats

    def _extract_district_from_title(self, title_str) -> str:
        """从标题中提取区域信息"""
        if pd.isna(title_str):
            return '浦东'

        districts = ['浦东', '黄浦', '徐汇', '长宁', '静安', '普陀', '虹口', '杨浦',
                     '闵行', '宝山', '嘉定', '金山', '松江', '青浦', '奉贤', '崇明']
        for district in districts:
            if district in title_str:
                return district

        return '浦东'  # 默认为浦东