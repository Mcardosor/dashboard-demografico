THEMES = {
    "dark": {
        "bg":          "#0d1117",
        "bg_card":     "rgba(22,27,34,.92)",
        "bg_plot":     "rgba(0,0,0,0)",
        "text":        "#c9d1d9",
        "text_title":  "#f0f6fc",
        "text_muted":  "#8b949e",
        "border":      "#30363d",
        "border_hero": "#21262d",
        "grid":        "#21262d",
        "accent":      "#58a6ff",
        "success":     "#7ee787",
        "danger":      "#f85149",
        "hero_bg":     "linear-gradient(135deg,#161b22 0%,#0d1117 60%,#0d2137 100%)",
        "map_line":    "#30363d",
        "bar_line":    "#0d1117",
        "footer":      "#484f58",
        "sidebar_bg":  "#010409",
        "toggle_icon": "☀️",
        "toggle_label":"Modo claro",
    },
    "light": {
        "bg":          "#f6f8fa",
        "bg_card":     "rgba(255,255,255,.98)",
        "bg_plot":     "rgba(0,0,0,0)",
        "text":        "#24292f",
        "text_title":  "#1a3a5c",
        "text_muted":  "#57606a",
        "border":      "#d0d7de",
        "border_hero": "#b8d4ee",
        "grid":        "#eaecef",
        "accent":      "#2B7BB9",
        "accent2":     "#E07B54",
        "success":     "#1a7f37",
        "danger":      "#cf222e",
        "hero_bg":     "linear-gradient(135deg,#ffffff 0%,#eaf2fb 60%,#d4e8f6 100%)",
        "map_line":    "#d0d7de",
        "bar_line":    "#f6f8fa",
        "footer":      "#8c959f",
        "sidebar_bg":  "#ffffff",
        "toggle_icon": "🌙",
        "toggle_label":"Modo escuro",
    },
}


def _css(t: dict) -> str:
    return f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }}

  .stApp {{ background: {t['bg']}; color: {t['text']}; }}

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] > div:first-child {{
    background: {t['sidebar_bg']};
    border-right: 1px solid {t['border']};
  }}

  /* ── Hero ── */
  .hero {{
    background: {t['hero_bg']};
    border: 1px solid {t['border_hero']};
    border-radius: 16px;
    padding: 36px 40px 30px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
  }}
  .hero::before {{
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, {t['accent']}18 0%, transparent 70%);
    border-radius: 50%;
  }}
  .hero-title {{
    font-size: 2.1rem; font-weight: 800; color: {t['text_title']};
    display: flex; align-items: center; gap: 14px; margin: 0 0 10px;
    letter-spacing: -0.5px;
  }}
  .hero-subtitle {{
    color: {t['text_muted']}; font-size: .95rem;
    max-width: 680px; margin: 0 0 20px; line-height: 1.6;
  }}
  .hero-badges {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .hero-badge {{
    background: rgba(128,128,128,.08);
    border: 1px solid {t['border']};
    border-radius: 20px; padding: 5px 14px; font-size: .78rem;
    color: {t['text_muted']}; display: flex; align-items: center; gap: 6px;
    font-weight: 500;
  }}
  .hero-badge.accent {{
    background: {t['accent']}15;
    border-color: {t['accent']}50; color: {t['accent']};
  }}
  .hero-badge.success {{
    background: {t['success']}15;
    border-color: {t['success']}50; color: {t['success']};
  }}
  .dot {{ width: 7px; height: 7px; border-radius: 50%; background: currentColor; display: inline-block; }}

  /* ── KPI Cards ── */
  .kpi-grid {{ display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 8px; }}
  .kpi-card {{
    background: {t['bg_card']};
    border: 1px solid {t['border']};
    border-top: 3px solid {t['accent']};
    border-radius: 12px;
    padding: 20px 22px 16px;
    transition: transform .15s, box-shadow .15s;
  }}
  .kpi-card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,.15);
  }}
  .kpi-card.green  {{ border-top-color: {t['success']}; }}
  .kpi-card.blue   {{ border-top-color: {t['accent']}; }}
  .kpi-card.purple {{ border-top-color: #bc8cff; }}
  .kpi-card.orange {{ border-top-color: #e3b341; }}

  .kpi-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }}
  .kpi-icon   {{ font-size: 1.5rem; }}
  .kpi-title  {{
    color: {t['text_muted']}; font-size: .72rem; font-weight: 600;
    text-transform: uppercase; letter-spacing: .06em;
  }}
  .kpi-value  {{
    color: {t['text_title']}; font-size: 2.2rem; font-weight: 800;
    line-height: 1.1; margin: 2px 0 6px; letter-spacing: -1px;
  }}
  .kpi-sub    {{ color: {t['text_muted']}; font-size: .78rem; margin-bottom: 4px; }}
  .kpi-delta-pos {{ color: {t['success']}; font-size: .75rem; font-weight: 600; }}
  .kpi-delta-neg {{ color: {t['danger']};  font-size: .75rem; font-weight: 600; }}
  .kpi-delta-neu {{ color: {t['text_muted']}; font-size: .75rem; }}

  /* ── Section headers ── */
  .section-header {{
    display: flex; align-items: center; gap: 10px;
    margin: 8px 0 4px;
  }}
  .section-num {{
    background: {t['accent']}20;
    color: {t['accent']};
    font-size: .7rem; font-weight: 700;
    padding: 2px 8px; border-radius: 20px;
    border: 1px solid {t['accent']}40;
  }}
  .section-title {{
    font-size: 1.1rem; font-weight: 700;
    color: {t['text_title']}; margin: 0;
  }}
  .section-caption {{
    color: {t['text_muted']}; font-size: .82rem;
    margin: 0 0 12px; line-height: 1.5;
  }}

  /* ── Cenários+ header bar (tema claro apenas) ── */
  .cenarios-bar {{
    background: #2B7BB9;
    padding: 8px 24px;
    margin: -1rem -1rem 1.5rem -1rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .cenarios-bar-logo {{
    font-size: 1.1rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.3px;
  }}
  .cenarios-bar-logo span {{
    color: #E07B54;
  }}
  .cenarios-bar-sep {{
    color: rgba(255,255,255,.4);
    margin: 0 6px;
  }}
  .cenarios-bar-title {{
    font-size: .85rem;
    font-weight: 500;
    color: rgba(255,255,255,.85);
  }}

  /* ── Misc ── */
  h2, h3 {{ color: {t['text_title']} !important; }}
  hr {{ border-color: {t['grid']} !important; margin: 24px 0 !important; }}
  .stDataFrame {{ border-color: {t['border']} !important; border-radius: 8px !important; }}

  /* ── Widgets nativos do Streamlit ── */

  /* Botões */
  .stButton > button {{
    background-color: transparent !important;
    color: {t['text']} !important;
    border: 1px solid {t['border']} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    width: 100%;
  }}
  .stButton > button p,
  .stButton > button span,
  .stButton > button div {{
    color: {t['text']} !important;
  }}
  .stButton > button:hover {{
    background-color: {t['accent']}18 !important;
    border-color: {t['accent']} !important;
    color: {t['accent']} !important;
  }}
  .stButton > button:hover p,
  .stButton > button:hover span {{
    color: {t['accent']} !important;
  }}

  /* Selectbox */
  [data-testid="stSelectbox"] > div > div {{
    background-color: {t['bg_card']} !important;
    border-color: {t['border']} !important;
    color: {t['text']} !important;
  }}
  [data-testid="stSelectbox"] label,
  [data-testid="stSelectbox"] span {{
    color: {t['text_muted']} !important;
  }}

  /* Multiselect */
  [data-testid="stMultiSelect"] > div > div {{
    background-color: {t['bg_card']} !important;
    border-color: {t['border']} !important;
  }}
  [data-testid="stMultiSelect"] label {{
    color: {t['text_muted']} !important;
  }}

  /* Checkbox e Toggle */
  .stCheckbox label, .stCheckbox p, .stCheckbox span,
  .stToggle label, .stToggle p, .stToggle span,
  [data-testid="stCheckbox"] label,
  [data-testid="stCheckbox"] p,
  [data-testid="stToggle"] label,
  [data-testid="stToggle"] p,
  [data-testid="stToggle"] > label > div > p,
  [data-testid="stToggle"] > label > div,
  div[class*="toggle"] p,
  div[class*="checkbox"] p {{
    color: {t['text']} !important;
    opacity: 1 !important;
  }}

  /* Divider */
  [data-testid="stDivider"] hr {{
    border-color: {t['border']} !important;
  }}

  /* Caption / texto pequeno */
  [data-testid="stCaptionContainer"] p {{
    color: {t['text_muted']} !important;
  }}

  /* Sidebar labels */
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span {{
    color: {t['text']} !important;
  }}

  /* Input text dropdown */
  [data-baseweb="select"] * {{
    background-color: {t['bg_card']} !important;
    color: {t['text']} !important;
  }}
  [data-baseweb="popover"] * {{
    background-color: {t['bg_card']} !important;
    color: {t['text']} !important;
  }}
  [data-baseweb="menu"] li:hover {{
    background-color: {t['accent']}20 !important;
  }}

  /* Esconde deploy button nativo */
  .stDeployButton {{ display: none !important; }}
</style>
"""
