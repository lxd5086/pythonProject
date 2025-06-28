# -*- coding: utf-8 -*-
"""
Configuration module for visualization settings.
"""

import os
import plotly.express as px

class Config:
    """Configuration settings for visualizations."""

    def __init__(self, output_dir: str = None):
        """Initialize configuration with default or provided output directory."""
        self.output_dir = output_dir or os.path.join(os.getcwd(), 'visualization_output')
        self.colors = px.colors.qualitative.Set3
        self.font_settings = {
            'family': 'SimHei, Microsoft YaHei',
            'size': 12
        }