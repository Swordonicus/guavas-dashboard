# utils/visualizations.py
from typing import Dict, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

PALETTES: Dict[str, List[str]] = {
    # Color-blind safe, high contrast (Okabe–Ito)
    "okabe_ito": [
        "#000000",  # black
        "#E69F00",  # orange
        "#56B4E9",  # sky blue
        "#009E73",  # bluish green
        "#F0E442",  # yellow
        "#0072B2",  # blue
        "#D55E00",  # vermillion
        "#CC79A7",  # reddish purple
        "#999999",  # gray
    ],
    # A second good option (Tableau 10)
    "tableau10": [
        "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
        "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"
    ],
    # Brewer Set2 (pastel but distinct)
    "set2": ["#66C2A5","#FC8D62","#8DA0CB","#E78AC3","#A6D854","#FFD92F","#E5C494","#B3B3B3"],
}

def _cycle_colors(n: int, palette: str) -> List[str]:
    base = PALETTES.get(palette, PALETTES["okabe_ito"])
    if n <= len(base):
        return base[:n]
    # If more series than colors, repeat but shift so adjacent series differ
    colors = []
    for i in range(n):
        colors.append(base[i % len(base)])
    return colors

class ChartBuilder:
    def create_kpi_trend_chart(
        self,
        df: pd.DataFrame,
        title: str = "",
        palette: str = "okabe_ito",
        fill_opacity: float = 0.55,
    ) -> go.Figure:
        """
        Stacked area (by columns other than 'Week') with accessible colors.
        Expects a 'Week' datetime column and 1+ numeric series columns.
        """
        if df is None or df.empty or "Week" not in df.columns:
            return go.Figure()

        series = [c for c in df.columns if c != "Week"]
        colors = _cycle_colors(len(series), palette)

        fig = go.Figure()
        for idx, col in enumerate(series):
            fig.add_trace(
                go.Scatter(
                    x=df["Week"],
                    y=df[col],
                    name=col,
                    mode="lines",
                    line=dict(width=2.3, color=colors[idx]),
                    fill="tonexty" if idx > 0 else "tozeroy",
                    stackgroup="one",
                    hovertemplate="<b>%{x|%b %d, %Y}</b><br>%{fullData.name}: %{y:.0f}<extra></extra>",
                    opacity=1.0,  # line opacity
                )
            )

        # Improve readability
        fig.update_traces(fillcolor=None)  # let Plotly handle fill; keep line crisp
        # Add semi-transparent fill by updating each trace's fillcolor
        for t, c in zip(fig.data, colors):
            t.fillcolor = c + hex(int(255 * fill_opacity))[2:].zfill(2)  # add alpha

        fig.update_layout(
            template="plotly_white",
            title=dict(text=f"📈 {title}" if title else "📈 Weekly Lead Trend (Last 12 Weeks)", x=0.02),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0, traceorder="normal"),
            margin=dict(l=40, r=20, t=60, b=40),
            yaxis_title="Leads",
            xaxis_title="Week",
            hovermode="x unified",
        )
        fig.update_yaxes(gridcolor="rgba(0,0,0,0.08)")
        fig.update_xaxes(showgrid=False)

        return fig

def get_chart_builder() -> ChartBuilder:
    return ChartBuilder()
