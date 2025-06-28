from data_processor import DataProcessor
from visualization.visualizer import Visualizer

def main():
    # 数据处理
    processor = DataProcessor(output_dir='cleaned_data')
    if not processor.load_data('data/Lianjia_pudong_rentals.csv'):  # 修改此处
        print("❌ 数据加载失败，退出程序")
        return

    cleaned_df = processor.clean_data()
    district_stats = processor.get_district_analysis()
    stats = processor.get_basic_statistics()

    # 打印基础统计信息
    print("\n📈 基础统计信息：")
    for category, data in stats.items():
        print(f"\n{category}:")
        for key, value in data.items():
            print(f"  {key}: {value}")

    # 可视化
    visualizer = Visualizer(output_dir='output')
    charts = visualizer.create_comprehensive_charts(cleaned_df, district_stats)

    # 可选：显示图表
    for chart_name, chart in charts.items():
        print(f"📈 Displaying {chart_name}")
        chart.show()

if __name__ == "__main__":
    main()