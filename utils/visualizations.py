# utils/visualizations.py

from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go

PALETTES: Dict[str, List[str]] = {
    "okabe_ito": [
        "#000000", "#E69F00", "#56B4E9", "#009E73",
        "#F0E442", "#0072B2", "#D55E00", "#CC79A7", "#999999",
    ],
    "tableau10": [
        "#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F",
        "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC",
    ],
    "set2": ["#66C2A5","#FC8D62","#8DA0CB","#E78AC3","#A6D854","#FFD92F","#E5C494","#B3B3B3"],
}

def _cycle_colors(n: int, palette: str) -> List[str]:
    base = PALETTES.get(palette, PALETTES["okabe_ito"])
    if n <= len(base):
        return base[:n]
    out = []
    for i in range(n):
        out.append(base[i % len(base)])
    return out

def _hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Convert '#RRGGBB' to 'rgba(r,g,b,a)'. Falls back gracefully if already rgb/rgba."""
    if not isinstance(hex_color, str):
        return "rgba(0,0,0,1)"
    s = hex_color.strip()
    if s.startswith("rgba") or s.startswith("rgb"):
        return s  # assume valid
    if s.startswith("#"):
        s = s.lstrip("#")
        if len(s) >= 6:
            r = int(s[0:2], 16)
            g = int(s[2:4], 16)
            b = int(s[4:6], 16)
            a = max(0.0, min(1.0, float(alpha)))
            return f"rgba({r},{g},{b},{a})"
    # default fallback
    return "rgba(0,0,0,1)"

class ChartBuilder:
    def create_kpi_trend_chart(
        self,
        df: pd.DataFrame,
        title: str = "",
        palette: str = "okabe_ito",
        fill_opacity: float = 0.55,
    ) -> go.Figure:
        """
        Stacked area chart over 'Week' using accessible colors.
        Expects a 'Week' datetime column and 1+ numeric series columns.
        """
        fig = go.Figure()
        if df is None or df.empty or "Week" not in df.columns:
            return fig

        series = [c for c in df.columns if c != "Week"]
        colors = _cycle_colors(len(series), palette)

        for idx, col in enumerate(series):
            line_color = colors[idx]
            fig.add_trace(
                go.Scatter(
                    x=df["Week"],
                    y=df[col],
                    name=col,
                    mode="lines",
                    line=dict(width=2.3, color=line_color),
                    fill="tonexty" if idx > 0 else "tozeroy",
                    stackgroup="one",
                    hovertemplate="<b>%{x|%b %d, %Y}</b><br>%{fullData.name}: %{y:.0f}<extra></extra>",
                    fillcolor=_hex_to_rgba(line_color, fill_opacity),
                )
            )

        fig.update_layout(
            template="plotly_white",
            title=dict(text=f"📈 {title}" if title else "📈 Weekly Lead Trend (Last 12 Weeks)", x=0.02),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0.0),
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
