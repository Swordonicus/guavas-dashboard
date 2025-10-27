# Guavas Dashboard - Visualizations
# All chart and graph generation using Plotly

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from config import COLORS, CHART_HEIGHT, CHART_TEMPLATE

class ChartBuilder:
    """Class to build all dashboard charts"""
    
    @staticmethod
    def create_kpi_trend_chart(data_df, title="Weekly Lead Trend"):
        """
        Create stacked area chart for leads by source over time
        
        Args:
            data_df: DataFrame with 'Week' column and channel columns
            title: Chart title
            
        Returns:
            plotly Figure
        """
        fig = go.Figure()
        
        # Get channel columns (exclude Week)
        channels = [col for col in data_df.columns if col != 'Week']
        
        # Color palette for channels
        colors = [COLORS['primary'], COLORS['success'], COLORS['warning'], 
                 COLORS['info'], COLORS['danger']]
        
        for idx, channel in enumerate(channels):
            fig.add_trace(go.Scatter(
                x=data_df['Week'],
                y=data_df[channel],
                mode='lines',
                name=channel,
                stackgroup='one',
                fillcolor=colors[idx % len(colors)],
                line=dict(width=0.5, color=colors[idx % len(colors)])
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Week",
            yaxis_title="Leads",
            hovermode='x unified',
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_channel_performance_chart(data_df, metric='CPL'):
        """
        Create bar chart for channel performance
        
        Args:
            data_df: DataFrame with channel data
            metric: Metric to display (CPL, Leads, etc.)
            
        Returns:
            plotly Figure
        """
        # Sort by metric
        data_df = data_df.sort_values(metric, ascending=True)
        
        # Color based on performance (lower CPL = better)
        if metric == 'CPL':
            colors = [COLORS['success'] if val < 25 else COLORS['warning'] if val < 50 else COLORS['danger'] 
                     for val in data_df[metric]]
        else:
            colors = COLORS['primary']
        
        fig = go.Figure(data=[
            go.Bar(
                x=data_df[metric],
                y=data_df['Channel'],
                orientation='h',
                marker_color=colors,
                text=data_df[metric],
                texttemplate='£%{text:.2f}' if metric == 'CPL' else '%{text}',
                textposition='outside'
            )
        ])
        
        fig.update_layout(
            title=f"Channel Performance by {metric}",
            xaxis_title=metric,
            yaxis_title="Channel",
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE,
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_dual_axis_chart(data_df, date_col='Week', bar_col='Leads', line_col='CPL'):
        """
        Create combo chart with bars and line (dual y-axis)
        
        Args:
            data_df: DataFrame with data
            date_col: X-axis column
            bar_col: Bar chart metric
            line_col: Line chart metric
            
        Returns:
            plotly Figure
        """
        fig = go.Figure()
        
        # Add bar chart (Leads)
        fig.add_trace(go.Bar(
            x=data_df[date_col],
            y=data_df[bar_col],
            name=bar_col,
            marker_color=COLORS['primary'],
            yaxis='y'
        ))
        
        # Add line chart (CPL)
        fig.add_trace(go.Scatter(
            x=data_df[date_col],
            y=data_df[line_col],
            name=line_col,
            mode='lines+markers',
            line=dict(color=COLORS['danger'], width=3),
            marker=dict(size=8),
            yaxis='y2'
        ))
        
        # Update layout with dual y-axes
        fig.update_layout(
            title=f"{bar_col} and {line_col} Over Time",
            xaxis=dict(title=date_col),
            yaxis=dict(
                title=bar_col,
                side='left'
            ),
            yaxis2=dict(
                title=line_col,
                overlaying='y',
                side='right',
                showgrid=False
            ),
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_funnel_chart(stages, values):
        """
        Create funnel visualization
        
        Args:
            stages: List of stage names
            values: List of values for each stage
            
        Returns:
            plotly Figure
        """
        fig = go.Figure(go.Funnel(
            y=stages,
            x=values,
            textinfo="value+percent initial",
            marker=dict(
                color=[COLORS['info'], COLORS['primary'], COLORS['success'], COLORS['warning']],
            ),
            connector=dict(line=dict(color=COLORS['grey_300'], width=2))
        ))
        
        fig.update_layout(
            title="Conversion Funnel",
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def create_sankey_diagram(source, target, value, labels):
        """
        Create Sankey flow diagram
        
        Args:
            source: List of source node indices
            target: List of target node indices
            value: List of flow values
            labels: List of all node labels
            
        Returns:
            plotly Figure
        """
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color=COLORS['grey_300'], width=0.5),
                label=labels,
                color=COLORS['primary']
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color='rgba(0, 102, 204, 0.3)'
            )
        )])
        
        fig.update_layout(
            title="Lead Flow: Source → Stage → Outcome",
            height=CHART_HEIGHT + 100,
            template=CHART_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def create_pie_chart(labels, values, title="Distribution"):
        """
        Create pie chart
        
        Args:
            labels: List of category labels
            values: List of values
            title: Chart title
            
        Returns:
            plotly Figure
        """
        colors = [COLORS['primary'], COLORS['success'], COLORS['warning'], 
                 COLORS['info'], COLORS['danger'], COLORS['grey_600']]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors[:len(labels)]),
            textinfo='label+percent',
            hoverinfo='label+value+percent'
        )])
        
        fig.update_layout(
            title=title,
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE,
            showlegend=True
        )
        
        return fig
    
    @staticmethod
    def create_gauge_chart(value, max_value, title="Score", threshold_low=30, threshold_high=70):
        """
        Create gauge chart for scores
        
        Args:
            value: Current value
            max_value: Maximum value (typically 100)
            title: Chart title
            threshold_low: Low threshold (red zone)
            threshold_high: High threshold (green zone starts here)
            
        Returns:
            plotly Figure
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            delta={'reference': threshold_high},
            gauge={
                'axis': {'range': [None, max_value]},
                'bar': {'color': COLORS['primary']},
                'steps': [
                    {'range': [0, threshold_low], 'color': COLORS['danger']},
                    {'range': [threshold_low, threshold_high], 'color': COLORS['warning']},
                    {'range': [threshold_high, max_value], 'color': COLORS['success']}
                ],
                'threshold': {
                    'line': {'color': COLORS['grey_900'], 'width': 4},
                    'thickness': 0.75,
                    'value': threshold_high
                }
            }
        ))
        
        fig.update_layout(
            height=300,
            template=CHART_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def create_heatmap(data_df, x_col, y_col, value_col, title="Heatmap"):
        """
        Create heatmap visualization
        
        Args:
            data_df: DataFrame with data
            x_col: X-axis column
            y_col: Y-axis column
            value_col: Value column for color intensity
            title: Chart title
            
        Returns:
            plotly Figure
        """
        # Pivot data for heatmap
        pivot = data_df.pivot(index=y_col, columns=x_col, values=value_col)
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns,
            y=pivot.index,
            colorscale='Blues',
            text=pivot.values,
            texttemplate='%{text:.0f}',
            textfont={"size": 10},
            colorbar=dict(title=value_col)
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE
        )
        
        return fig
    
    @staticmethod
    def create_line_chart_with_forecast(historical_df, forecast_df, date_col='Date', value_col='Value'):
        """
        Create line chart with historical data and forecast
        
        Args:
            historical_df: DataFrame with historical data
            forecast_df: DataFrame with forecast data
            date_col: Date column name
            value_col: Value column name
            
        Returns:
            plotly Figure
        """
        fig = go.Figure()
        
        # Historical data (solid line)
        fig.add_trace(go.Scatter(
            x=historical_df[date_col],
            y=historical_df[value_col],
            mode='lines+markers',
            name='Historical',
            line=dict(color=COLORS['primary'], width=2),
            marker=dict(size=6)
        ))
        
        # Forecast data (dashed line)
        fig.add_trace(go.Scatter(
            x=forecast_df[date_col],
            y=forecast_df[value_col],
            mode='lines+markers',
            name='Forecast',
            line=dict(color=COLORS['info'], width=2, dash='dash'),
            marker=dict(size=6)
        ))
        
        # Add shaded forecast region
        fig.add_trace(go.Scatter(
            x=forecast_df[date_col],
            y=forecast_df[value_col] * 1.1,  # Upper bound (+10%)
            mode='lines',
            line=dict(width=0),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        fig.add_trace(go.Scatter(
            x=forecast_df[date_col],
            y=forecast_df[value_col] * 0.9,  # Lower bound (-10%)
            mode='lines',
            line=dict(width=0),
            fillcolor='rgba(99, 102, 241, 0.2)',
            fill='tonexty',
            name='Confidence Interval',
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=f"{value_col} with 90-Day Forecast",
            xaxis_title="Date",
            yaxis_title=value_col,
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )
        
        return fig
    
    @staticmethod
    def create_waterfall_chart(categories, values, title="Waterfall Chart"):
        """
        Create waterfall chart for showing cumulative effect
        
        Args:
            categories: List of category names
            values: List of values (positive or negative)
            title: Chart title
            
        Returns:
            plotly Figure
        """
        fig = go.Figure(go.Waterfall(
            orientation="v",
            measure=["relative"] * (len(categories) - 1) + ["total"],
            x=categories,
            y=values,
            connector={"line": {"color": COLORS['grey_300']}},
            increasing={"marker": {"color": COLORS['success']}},
            decreasing={"marker": {"color": COLORS['danger']}},
            totals={"marker": {"color": COLORS['primary']}}
        ))
        
        fig.update_layout(
            title=title,
            height=CHART_HEIGHT,
            template=CHART_TEMPLATE,
            showlegend=False
        )
        
        return fig

# Singleton instance
_chart_builder = None

def get_chart_builder():
    """Get or create ChartBuilder instance"""
    global _chart_builder
    if _chart_builder is None:
        _chart_builder = ChartBuilder()
    return _chart_builder
