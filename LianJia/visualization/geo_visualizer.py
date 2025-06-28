# -*- coding: utf-8 -*-
"""
Module for geographic-related visualizations.
"""
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class GeoVisualizer:
    """Visualizer for geographic-related charts."""

    def __init__(self, config):
        """Initialize with configuration settings."""
        self.config = config

    def create_geographic_analysis(self, df: pd.DataFrame, district_stats: pd.DataFrame) -> go.Figure:
        """Create geographic analysis dashboard."""
        print("🗺️ Generating geographic analysis...")

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('District Property Counts', 'District Average Rent',
                          'District Average Price/Sqm', 'Rent vs Property Count'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # 1. Property Counts by District
        fig.add_trace(
            go.Bar(
                x=district_stats.index,
                y=district_stats['房源数量'],
                name='Property Count',
                marker_color=self.config.colors[0],
                text=district_stats['房源数量'],
                textposition='auto'
            ),
            row=1, col=1
        )

        # 2. Average Rent by District
        fig.add_trace(
            go.Bar(
                x=district_stats.index,
                y=district_stats['平均租金'],
                name='Average Rent',
                marker_color=self.config.colors[1],
                text=[f'{v:.0f}' for v in district_stats['平均租金']],
                textposition='auto'
            ),
            row=1, col=2
        )

        # 3. Average Price/Sqm by District
        fig.add_trace(
            go.Bar(
                x=district_stats.index,
                y=district_stats['平均单价'],
                name='Average Price/Sqm',
                marker_color=self.config.colors[2],
                text=[f'{v:.1f}' for v in district_stats['平均单价']],
                textposition='auto'
            ),
            row=2, col=1
        )

        # 4. Rent vs Property Count Scatter
        fig.add_trace(
            go.Scatter(
                x=district_stats['房源数量'],
                y=district_stats['平均租金'],
                mode='markers+text',
                text=district_stats.index,
                textposition='top center',
                name='Rent vs Count',
                marker=dict(
                    size=15,
                    color=self.config.colors[3],
                    line=dict(width=2, color='white')
                )
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="<b>Pudong District Rental Market Analysis</b>",
            title_x=0.5,
            showlegend=False,
            template='plotly_white'
        )

        output_path = os.path.join(self.config.output_dir, 'geographic_analysis.html')
        fig.write_html(output_path)
        print(f"✅ Geographic analysis saved: {output_path}")

        return fig