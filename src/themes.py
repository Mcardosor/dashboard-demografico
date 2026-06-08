THEMES = {
    "dark": {
        "bg":          "#0d1117",
        "bg_card":     "rgba(22,27,34,.92)",
        "bg_plot":     "rgba(0,0,0,0)",
        "text":        "#c9d1d9",
        "text_title":  "#f0f6fc",
        "text_muted":  "#8b949e",
        "border":      "#30363d",
        "border_hero": "#30363d",
        "grid":        "#21262d",
        "accent":      "#58a6ff",
        "success":     "#7ee787",
        "hero_bg":     "linear-gradient(135deg,#161b22 0%,#0d1117 60%,#112240 100%)",
        "map_line":    "#30363d",
        "bar_line":    "#0d1117",
        "footer":      "#484f58",
        "toggle_icon": "☀️",
        "toggle_label":"Modo claro",
    },
    "light": {
        "bg":          "#f6f8fa",
        "bg_card":     "rgba(255,255,255,.95)",
        "bg_plot":     "rgba(0,0,0,0)",
        "text":        "#24292f",
        "text_title":  "#1f2328",
        "text_muted":  "#57606a",
        "border":      "#d0d7de",
        "border_hero": "#d0d7de",
        "grid":        "#eaecef",
        "accent":      "#0969da",
        "success":     "#1a7f37",
        "hero_bg":     "linear-gradient(135deg,#ffffff 0%,#f6f8fa 60%,#dce8f8 100%)",
        "map_line":    "#d0d7de",
        "bar_line":    "#f6f8fa",
        "footer":      "#8c959f",
        "toggle_icon": "🌙",
        "toggle_label":"Modo escuro",
    },
}


def _css(t: dict) -> str:
    return f"""
<style>
  html, body, [class*="css"] {{ font-family: 'Segoe UI', sans-serif; }}
  .stApp {{ background: {t['bg']}; color: {t['text']}; }}

  .hero {{
    background: {t['hero_bg']};
    border: 1px solid {t['border_hero']};
    border-radius: 14px;
    padding: 32px 36px 28px;
    margin-bottom: 28px;
  }}
  .hero-title {{
    font-size: 2rem; font-weight: 700; color: {t['text_title']};
    display: flex; align-items: center; gap: 12px; margin: 0 0 8px;
  }}
  .hero-emoji {{ font-size: 2.2rem; }}
  .hero-subtitle {{ color: {t['text_muted']}; font-size: .97rem; max-width: 720px; margin: 0 0 18px; }}
  .hero-badges {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .hero-badge {{
    background: rgba(128,128,128,.1); border: 1px solid {t['border']};
    border-radius: 20px; padding: 4px 14px; font-size: .78rem;
    color: {t['text_muted']}; display: flex; align-items: center; gap: 6px;
  }}
  .hero-badge.accent {{ background: rgba(88,166,255,.12); border-color: {t['accent']}44; color: {t['accent']}; }}
  .hero-badge.success {{ background: rgba(46,160,67,.12); border-color: {t['success']}44; color: {t['success']}; }}
  .dot {{ width:7px; height:7px; border-radius:50%; background:currentColor; display:inline-block; }}

  .kpi-card {{
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-radius: 12px;
    padding: 18px 20px 14px;
    transition: border-color .2s, box-shadow .2s;
  }}
  .kpi-card:hover {{ border-color: {t['accent']}; box-shadow: 0 0 0 3px {t['accent']}22; }}
  .kpi-icon  {{ font-size: 1.6rem; margin-bottom: 4px; }}
  .kpi-title {{ color: {t['text_muted']}; font-size: .78rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; }}
  .kpi-value {{ color: {t['text_title']}; font-size: 1.9rem; font-weight: 700; line-height: 1.2; margin: 4px 0; }}
  .kpi-sub   {{ color: {t['text_muted']}; font-size: .78rem; }}
  .kpi-delta-pos {{ color: {t['success']}; font-size: .78rem; font-weight: 600; }}
  .kpi-delta-neg {{ color: #f85149; font-size: .78rem; font-weight: 600; }}
  .kpi-delta-neu {{ color: {t['text_muted']}; font-size: .78rem; }}

  h2, h3 {{ color: {t['text_title']} !important; }}
  hr {{ border-color: {t['grid']} !important; }}
  .stDataFrame {{ border-color: {t['border']} !important; }}
</style>
"""
