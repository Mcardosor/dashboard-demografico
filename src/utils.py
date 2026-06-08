import plotly.graph_objects as go

PLOTLY_CFG = {"displayModeBar": False, "scrollZoom": False}
H_SMALL, H_MEDIUM, H_LARGE = 320, 420, 520
COLOR_M, COLOR_F = "#58a6ff", "#f778ba"


def _fmt(n: float) -> str:
    if abs(n) >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n/1_000:.1f}K"
    return f"{n:.0f}"


def _delta_html(val: float, prev: float, invert: bool = False) -> str:
    if prev == 0:
        return ""
    diff = val - prev
    pct  = diff / prev * 100
    arrow = "▲" if diff >= 0 else "▼"
    cls = "kpi-delta-pos" if (diff >= 0) != invert else "kpi-delta-neg"
    if diff == 0:
        cls = "kpi-delta-neu"
    return f'<span class="{cls}">{arrow} {abs(pct):.1f}% vs ano anterior</span>'


def kpi_card(title: str, value: str, subtitle: str, icon: str, delta_html: str = "") -> str:
    return f"""
    <div class="kpi-card">
      <div class="kpi-icon">{icon}</div>
      <div class="kpi-title">{title}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-sub">{subtitle}</div>
      {f'<div style="margin-top:6px">{delta_html}</div>' if delta_html else ''}
    </div>"""


def _apply_layout(fig: go.Figure, t: dict, height: int = H_MEDIUM) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor=t["bg_plot"],
        plot_bgcolor=t["bg_plot"],
        font_color=t["text"],
        font_size=12,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(bgcolor=t["bg_card"], bordercolor=t["border"], borderwidth=1),
    )
    fig.update_xaxes(gridcolor=t["grid"], linecolor=t["border"], zerolinecolor=t["border"])
    fig.update_yaxes(gridcolor=t["grid"], linecolor=t["border"], zerolinecolor=t["border"])
    return fig
