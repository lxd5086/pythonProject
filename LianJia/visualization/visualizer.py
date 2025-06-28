# -*- coding: utf-8 -*-
"""
Main visualization module for orchestrating different visualization tasks.
"""

import pandas as pd
import os
from typing import Dict
from .price_visualizer import PriceVisualizer
from .geo_visualizer import GeoVisualizer
from .layout_visualizer import LayoutVisualizer
from .config import Config

class Visualizer:
    """Main visualization orchestrator for rental data analysis."""

    def __init__(self, output_dir: str = None):
        """Initialize the visualizer with configuration settings."""
        self.config = Config(output_dir)
        self.output_dir = self.config.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"📊 Visualization output directory: {self.output_dir}")

        # Initialize specific visualizers
        self.price_viz = PriceVisualizer(self.config)
        self.geo_viz = GeoVisualizer(self.config)
        self.layout_viz = LayoutVisualizer(self.config)

    def create_comprehensive_charts(self, df: pd.DataFrame, district_stats: pd.DataFrame = None) -> Dict[str, 'go.Figure']:
        """Create a comprehensive set of visualization charts."""
        charts = {}

        # Generate visualizations using specific visualizer modules
        charts['price_analysis'] = self.price_viz.create_price_analysis_dashboard(df)
        charts['geographic_analysis'] = self.geo_viz.create_geographic_analysis(df, district_stats)
        charts['layout_analysis'] = self.layout_viz.create_layout_analysis(df)
        charts['market_insights'] = self.create_market_insights_dashboard(df)

        return charts

    def create_market_insights_dashboard(self, df: pd.DataFrame) -> 'go.Figure':
        """Create market insights dashboard."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots

        print("💡 Generating market insights dashboard...")

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Orientation Impact on Rent', 'Update Time Distribution',
                          'Cost-Performance Analysis', 'Rent Price Gradient'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # 1. Orientation vs Rent
        orientation_price = df.groupby('orientation_clean')['price_numeric'].mean().sort_values(ascending=False)
        fig.add_trace(
            go.Bar(
                x=orientation_price.index,
                y=orientation_price.values,
                name='Orientation Avg Rent',
                marker_color=self.config.colors[0],
                text=[f'{v:.0f}' for v in orientation_price.values],
                textposition='auto'
            ),
            row=1, col=1
        )

        # 2. Update Time Distribution
        update_counts = df['update_category'].value_counts()
        fig.add_trace(
            go.Bar(
                x=update_counts.index,
                y=update_counts.values,
                name='Update Time Distribution',
                marker_color=self.config.colors[1],
                text=update_counts.values,
                textposition='auto'
            ),
            row=1, col=2
        )

        # 3. Cost-Performance Analysis
        fig.add_trace(
            go.Scatter(
                x=df['area_numeric'],
                y=df['price_per_sqm'],
                mode='markers',
                name='Cost-Performance',
                marker=dict(
                    size=df['price_numeric'] / 200,
                    color=df['total_rooms'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Rooms", x=0.45),
                    opacity=0.7,
                    sizemode='diameter',
                    sizemin=4
                ),
                text=df['layout'],
                hovertemplate='<b>%{text}</b><br>Area: %{x:.1f}㎡<br>Price/Sqm: %{y:.2f}元/㎡<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Rent Price Gradient
        price_ranges = pd.cut(df['price_numeric'], bins=8, precision=0)
        price_range_counts = price_ranges.value_counts().sort_index()
        range_labels = [f"{int(interval.left)}-{int(interval.right)}" for interval in price_range_counts.index]

        fig.add_trace(
            go.Bar(
                x=range_labels,
                y=price_range_counts.values,
                name='Rent Distribution',
                marker_color=self.config.colors[2],
                text=price_range_counts.values,
                textposition='auto'
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="<b>Pudong Rental Market Insights</b>",
            title_x=0.5,
            showlegend=False,
            template='plotly_white'
        )

        output_path = os.path.join(self.output_dir, 'market_insights_dashboard.html')
        fig.write_html(output_path)
        print(f"✅ Market insights dashboard saved: {output_path}")

        return fig