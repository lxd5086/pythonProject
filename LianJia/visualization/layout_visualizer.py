# -*- coding: utf-8 -*-
"""
Module for layout-related visualizations.
"""
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class LayoutVisualizer:
    """Visualizer for layout-related charts."""

    def __init__(self, config):
        """Initialize with configuration settings."""
        self.config = config

    def create_layout_analysis(self, df: pd.DataFrame) -> go.Figure:
        """Create layout analysis dashboard."""
        print("🏠 Generating layout analysis...")

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Layout Distribution', 'Layout Rent Distribution',
                          'Room Count vs Rent', 'Area vs Rent'),
            specs=[[{"type": "domain"}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # 1. Layout Pie Chart
        layout_counts = df['layout'].value_counts().head(8)
        fig.add_trace(
            go.Pie(
                labels=layout_counts.index,
                values=layout_counts.values,
                name="Layout Distribution",
                hole=0.3,
                marker=dict(colors=px.colors.qualitative.Set3)
            ),
            row=1, col=1
        )

        # 2. Layout Rent Violin Plot
        layouts_to_show = df['layout'].value_counts().head(6).index
        for i, layout in enumerate(layouts_to_show):
            data = df[df['layout'] == layout]['price_numeric']
            fig.add_trace(
                go.Violin(
                    y=data,
                    name=layout,
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor=self.config.colors[i % len(self.config.colors)],
                    opacity=0.8
                ),
                row=1, col=2
            )

        # 3. Room Count vs Rent
        room_price = df.groupby('total_rooms')['price_numeric'].mean()
        fig.add_trace(
            go.Scatter(
                x=room_price.index,
                y=room_price.values,
                mode='lines+markers',
                name='Rooms vs Avg Rent',
                line=dict(color=self.config.colors[1], width=4),
                marker=dict(size=10, color='white', line=dict(width=2, color=self.config.colors[1]))
            ),
            row=2, col=1
        )

        # 4. Area vs Rent Scatter
        for i, layout in enumerate(layouts_to_show):
            data = df[df['layout'] == layout]
            fig.add_trace(
                go.Scatter(
                    x=data['area_numeric'],
                    y=data['price_numeric'],
                    mode='markers',
                    name=layout,
                    marker=dict(
                        color=self.config.colors[i % len(self.config.colors)],
                        size=8,
                        opacity=0.7
                    ),
                    hovertemplate='<b>%{text}</b><br>Area: %{x:.1f}㎡<br>Rent: %{y:.0f}元<extra></extra>',
                    text=[layout] * len(data)
                ),
                row=2, col=2
            )

        fig.update_layout(
            height=800,
            title_text="<b>Pudong Layout Analysis</b>",
            title_x=0.5,
            template='plotly_white'
        )

        output_path = os.path.join(self.config.output_dir, 'layout_analysis.html')
        fig.write_html(output_path)
        print(f"✅ Layout analysis saved: {output_path}")

        return fig