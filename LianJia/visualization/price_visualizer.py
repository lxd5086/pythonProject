# -*- coding: utf-8 -*-
"""
Module for price-related visualizations.
"""
import os
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PriceVisualizer:
    """Visualizer for price-related charts."""

    def __init__(self, config):
        """Initialize with configuration settings."""
        self.config = config

    def create_price_analysis_dashboard(self, df: pd.DataFrame) -> go.Figure:
        """Create price analysis dashboard."""
        print("📊 Generating price analysis dashboard...")

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Rent Distribution Histogram', 'Rent Box Plot',
                          'Price/Sqm vs Area Scatter', 'Layout Rent Comparison'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )

        # 1. Rent Distribution Histogram
        fig.add_trace(
            go.Histogram(
                x=df['price_numeric'],
                nbinsx=30,
                name='Rent Distribution',
                marker_color=self.config.colors[0],
                opacity=0.8
            ),
            row=1, col=1
        )

        # 2. Rent Box Plot by Layout
        top_layouts = df['layout'].value_counts().head(5).index
        for i, layout in enumerate(top_layouts):
            data = df[df['layout'] == layout]['price_numeric']
            fig.add_trace(
                go.Box(
                    y=data,
                    name=layout,
                    boxpoints='outliers',
                    marker_color=self.config.colors[i % len(self.config.colors)]
                ),
                row=1, col=2
            )

        # 3. Price/Sqm vs Area Scatter
        fig.add_trace(
            go.Scatter(
                x=df['area_numeric'],
                y=df['price_per_sqm'],
                mode='markers',
                name='Price/Sqm vs Area',
                marker=dict(
                    color=df['price_numeric'],
                    colorscale='Viridis',
                    showscale=True,
                    colorbar=dict(title="Rent (Yuan/Month)", x=0.45),
                    size=8,
                    opacity=0.7
                ),
                text=df['layout'],
                hovertemplate='<b>%{text}</b><br>Area: %{x:.1f}㎡<br>Price/Sqm: %{y:.2f}元/㎡<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Layout Average Rent Comparison
        layout_avg_price = df.groupby('layout')['price_numeric'].mean().sort_values(ascending=False).head(8)
        fig.add_trace(
            go.Bar(
                x=layout_avg_price.index,
                y=layout_avg_price.values,
                name='Average Rent',
                marker_color=self.config.colors[1],
                text=[f'{v:.0f}' for v in layout_avg_price.values],
                textposition='auto'
            ),
            row=2, col=2
        )

        fig.update_layout(
            height=800,
            title_text="<b>Pudong Rental Market Price Analysis</b>",
            title_x=0.5,
            showlegend=False,
            template='plotly_white'
        )

        output_path = os.path.join(self.config.output_dir, 'price_analysis_dashboard.html')
        fig.write_html(output_path)
        print(f"✅ Price analysis dashboard saved: {output_path}")

        return fig